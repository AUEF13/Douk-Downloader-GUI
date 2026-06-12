# DucK-Downloader-GUI

<p align="center">
  <b>TikTok / 抖音 数据采集与下载工具 — 图形界面版本</b>
</p>

## 项目说明

本项目是在 [DouK-Downloader](https://github.com/JoeanAmier/TikTokDownloader) 的基础上开发的 **PySide6 图形界面版本**，由 **Xiaomi MiMo Code** 设计并发布。


## 功能特性

- 📥 **作品下载** — 输入链接批量下载抖音/TikTok 作品
- 👤 **账号下载** — 批量采集账号发布、喜欢、收藏作品
- 🍪 **Cookie 管理** — 支持手动粘贴、从文件读取
- ⚙️ **设置** — 下载路径、命名格式、代理、平台开关
- 🌗 **深色/浅色模式** — 一键切换，全局样式统一管理
- 📋 **实时日志** — 终端风格日志面板，支持筛选

## 快速开始

### 方式一：安装程序

前往 `Releases` 下载 `exe`，双击运行即可。

### 方式二：源码运行

```bash
# 安装依赖
pip install PySide6 qasync
pip install -r requirements.txt

# 启动 GUI
python gui_main.py
```

## 项目结构

```
src/gui_edition/
├── __init__.py        # 应用入口
├── main_window.py     # 主窗口 + 侧边栏导航
├── theme.py           # 主题管理（深色/浅色）
├── bridge.py          # GUI 与核心业务逻辑桥接
├── pages/
│   ├── home_page.py       # 首页
│   ├── download_page.py   # 作品下载
│   ├── account_page.py    # 账号下载
│   ├── cookie_page.py     # Cookie 管理
│   ├── settings_page.py   # 设置
│   └── log_page.py        # 运行日志
```

## 致谢

- [DouK-Downloader](https://github.com/JoeanAmier/TikTokDownloader) — 原项目核心逻辑
- [Xiaomi MiMo Code](https://mimo.mi.com/) — GUI 设计与发布

## 许可证

本项目基于 GPL-3.0 许可证开源，详见 [license](license) 文件。
