import asyncio
from asyncio import TaskGroup
from datetime import date
from pathlib import Path
from time import time
from types import SimpleNamespace
from typing import Callable

from PySide6.QtCore import QObject, Signal as QSignal

from ..application.main_terminal import TikTok
from ..config import Parameter, Settings
from ..downloader import Downloader
from ..extract import Extractor
from ..interface import API, Account, AccountTikTok, Detail, DetailTikTok
from ..link import Extractor as LinkExtractor
from ..link import ExtractorTikTok
from ..manager import Database
from ..module import Cookie, MigrateFolder
from ..record import BaseLogger, LoggerManager
from ..storage import RecordManager
from ..tools import ColorfulConsole, create_client, cookie_dict_to_str
from ..translation import _, switch_language

__all__ = ["GUIBridge"]


class GUIBridge:
    def __init__(self, log_callback: Callable[[str, str], None] = None):
        self.log_callback = log_callback or (lambda msg, level="info": None)
        self.console = ColorfulConsole(debug=False)
        self.database = Database()
        self.settings: Settings | None = None
        self.parameter: Parameter | None = None
        self.tiktok: TikTok | None = None
        self._initialized = False

    async def initialize(self):
        await self.database.__aenter__()
        from ..custom import PROJECT_ROOT
        self.settings = Settings(PROJECT_ROOT, self.console)
        config = await self.database.read_config_data()
        option = await self.database.read_option_data()
        config_dict = {i["NAME"]: i["VALUE"] for i in config}
        option_dict = {i["NAME"]: i["VALUE"] for i in option}

        lang = option_dict.get("Language", "zh_CN")
        switch_language(lang)

        self._recorder_class = {1: LoggerManager, 0: BaseLogger}[
            config_dict.get("Logger", 0)
        ]
        self._record_enabled = config_dict.get("Record", 0)

        from ..manager import DownloadRecorder
        recorder = DownloadRecorder(
            self.database,
            self._record_enabled,
            self.console,
        )

        self.parameter = Parameter(
            self.settings,
            Cookie(self.settings, self.console),
            logger=self._recorder_class,
            console=self.console,
            **self.settings.read(),
            recorder=recorder,
        )
        self.parameter.set_headers_cookie()

        self.tiktok = TikTok(self.parameter, self.database)
        self._initialized = True
        self.log("核心模块初始化完成")

    async def close(self):
        if self.parameter:
            await self.parameter.close_client()
        await self.database.__aexit__(None, None, None)

    def log(self, msg: str, level: str = "info"):
        self.log_callback(msg, level)

    async def update_cookie(self, cookie: str, cookie_tiktok: str):
        if cookie:
            self.parameter.set_cookie(cookie, "")
            self.log("抖音 Cookie 已更新")
        if cookie_tiktok:
            self.parameter.set_cookie("", cookie_tiktok)
            self.log("TikTok Cookie 已更新")
        self.parameter.set_headers_cookie()

    async def download_detail(self, urls: list[str], tiktok: bool = False) -> dict:
        link_obj = self.tiktok.links_tiktok if tiktok else self.tiktok.links
        platform = "TikTok" if tiktok else "抖音"
        result = {"success": 0, "failed": 0, "total": len(urls)}

        for i, url in enumerate(urls, 1):
            self.log(f"[{i}/{len(urls)}] 正在处理: {url}")
            try:
                ids = await link_obj.run(url.strip())
                if not any(ids):
                    self.log(f"提取作品 ID 失败: {url}", "warning")
                    result["failed"] += 1
                    continue

                processor = DetailTikTok if tiktok else Detail
                detail_data = []
                for detail_id in ids:
                    data = await processor(
                        self.parameter, None, None, detail_id
                    ).run()
                    if data:
                        detail_data.append(data)

                if not detail_data:
                    self.log(f"获取作品详情失败: {url}", "warning")
                    result["failed"] += 1
                    continue

                extractor = Extractor(self.parameter)
                record = RecordManager()
                root, params, logger_cls = record.run(self.parameter)
                async with logger_cls(
                    root, console=self.console, **params
                ) as recorder:
                    extracted = await extractor.run(
                        detail_data, recorder, tiktok=tiktok,
                    )

                downloader = Downloader(self.parameter)
                await downloader.run(extracted, "detail", tiktok=tiktok)
                self.log(f"下载完成: {url}", "success")
                result["success"] += 1

            except Exception as e:
                self.log(f"处理失败: {url} - {e}", "error")
                result["failed"] += 1

        self.log(
            f"批量下载完成: 总计 {result['total']} 个, "
            f"成功 {result['success']} 个, 失败 {result['failed']} 个"
        )
        return result

    async def download_account(
        self,
        urls: list[str],
        mode: str = "post",
        tiktok: bool = False,
        max_pages: int = 0,
    ) -> dict:
        platform = "TikTok" if tiktok else "抖音"
        tab_names = {
            "post": "发布作品",
            "favorite": "喜欢作品",
            "collection": "收藏作品",
        }
        tab_name = tab_names.get(mode, "发布作品")
        result = {"success": 0, "failed": 0, "total": len(urls)}

        for i, url in enumerate(urls, 1):
            self.log(f"[{i}/{len(urls)}] 正在处理账号: {url}")
            try:
                link_obj = self.tiktok.links_tiktok if tiktok else self.tiktok.links
                sec_user_ids = await link_obj.run(url.strip(), "user")
                if not sec_user_ids:
                    self.log(f"提取账号 sec_user_id 失败: {url}", "warning")
                    result["failed"] += 1
                    continue

                for sec_id in sec_user_ids:
                    acquirer = (
                        self.tiktok._get_account_data_tiktok
                        if tiktok
                        else self.tiktok._get_account_data
                    )
                    account_data, earliest, latest = await acquirer(
                        sec_user_id=sec_id,
                        tab=mode,
                        pages=max_pages or None,
                    )
                    if not any(account_data):
                        self.log(f"获取账号数据失败: {sec_id}", "warning")
                        result["failed"] += 1
                        continue

                    extractor = Extractor(self.parameter)
                    record = RecordManager()
                    root, params, logger_cls = record.run(self.parameter)
                    async with logger_cls(
                        root, console=self.console, **params
                    ) as recorder:
                        extracted = await extractor.run(
                            account_data,
                            recorder,
                            type_="batch",
                            tiktok=tiktok,
                            earliest=earliest or date(2016, 9, 20),
                            latest=latest or date.today(),
                            same=mode == "post",
                        )

                    downloader = Downloader(self.parameter)
                    await downloader.run(
                        extracted, "batch", tiktok=tiktok,
                        mode=mode, user_id=sec_id,
                    )
                    self.log(
                        f"账号 {sec_id} 的{tab_name}下载完成", "success"
                    )
                    result["success"] += 1

            except Exception as e:
                self.log(f"处理账号失败: {url} - {e}", "error")
                result["failed"] += 1

        self.log(
            f"账号下载完成: 总计 {result['total']} 个, "
            f"成功 {result['success']} 个, 失败 {result['failed']} 个"
        )
        return result

    def save_settings(self, settings: dict):
        try:
            current = self.settings.read()
            current.update({k: v for k, v in settings.items() if v is not None})
            self.settings.update(current)
            self._pending_settings = current
            self.log("设置已保存（重启后生效）")
        except Exception as e:
            self.log(f"保存设置失败: {e}", "error")

    def apply_pending_settings(self):
        if not hasattr(self, '_pending_settings') or not self._pending_settings:
            return
        data = self._pending_settings
        self._pending_settings = None
        if self.parameter:
            try:
                p = self.parameter
                root = data.get("root", "")
                p.root = Path(root) if root and Path(root).is_dir() else p.ROOT
                p.folder_name = data.get("folder_name", "Download") or "Download"
                p.folder_mode = bool(data.get("folder_mode", False))
                p.music = bool(data.get("music", False))
                p.dynamic_cover = bool(data.get("dynamic_cover", False))
                p.static_cover = bool(data.get("static_cover", False))
                name_format = data.get("name_format", "create_time type nickname desc")
                p.name_format = name_format.split() if name_format else ["create_time", "type", "nickname", "desc"]
                p.split = data.get("split", "-") or "-"
                p.name_length = int(data.get("name_length", 128))
                p.desc_length = int(data.get("desc_length", 64))
                p.timeout = int(data.get("timeout", 10))
                p.max_retry = int(data.get("max_retry", 5))
                p.download = bool(data.get("download", True))
                self.log("运行参数已更新")
            except Exception as e:
                self.log(f"更新运行参数失败: {e}", "error")

    def _reload_settings(self, data: dict):
        if self.parameter:
            try:
                p = self.parameter
                root = data.get("root", "")
                p.root = Path(root) if root and Path(root).is_dir() else p.ROOT
                p.folder_name = data.get("folder_name", "Download") or "Download"
                p.folder_mode = bool(data.get("folder_mode", False))
                p.music = bool(data.get("music", False))
                p.dynamic_cover = bool(data.get("dynamic_cover", False))
                p.static_cover = bool(data.get("static_cover", False))
                name_format = data.get("name_format", "create_time type nickname desc")
                p.name_format = name_format.split() if name_format else ["create_time", "type", "nickname", "desc"]
                p.split = data.get("split", "-") or "-"
                p.name_length = int(data.get("name_length", 128))
                p.desc_length = int(data.get("desc_length", 64))
                p.timeout = int(data.get("timeout", 10))
                p.max_retry = int(data.get("max_retry", 5))
                p.download = bool(data.get("download", True))
            except Exception as e:
                self.log(f"更新运行参数失败: {e}", "error")

    def save_cookies(self, cookie: str = "", cookie_tiktok: str = ""):
        current = self.settings.read()
        if cookie:
            current["cookie"] = cookie
        if cookie_tiktok:
            current["cookie_tiktok"] = cookie_tiktok
        self.settings.update(current)
        self.log("Cookie 已保存")
