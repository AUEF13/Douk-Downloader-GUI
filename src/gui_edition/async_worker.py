import asyncio
import sys
from asyncio import AbstractEventLoop, new_event_loop
from threading import Event, Thread

from qasync import QEventLoop

from PySide6.QtCore import QObject, Signal, Slot


class AsyncWorker(QObject):
    """桥接 asyncio 事件循环与 Qt 事件循环"""
    error = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._loop: AbstractEventLoop | None = None
        self._thread: Thread | None = None
        self._ready = Event()

    def start(self):
        self._thread = Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        self._ready.wait()

    def _run_loop(self):
        self._loop = new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._ready.set()
        self._loop.run_forever()

    def stop(self):
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread:
            self._thread.join(timeout=3)

    def run_coroutine(self, coro):
        if self._loop and self._loop.is_running():
            return asyncio.run_coroutine_threadsafe(coro, self._loop)
        return None

    @property
    def loop(self):
        return self._loop
