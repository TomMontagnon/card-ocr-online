from __future__ import annotations
import threading
from PySide6 import QtCore
from apps.gui_qt.qt_ui_sink import QtUISink
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.pipeline.base import Pipeline
    from core.api.interfaces import IFrameSource


class AppController(QtCore.QObject):
    def __init__(
        self,
        source: IFrameSource,
        pipeline: Pipeline,
        parent: QtCore.QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._source = source
        self._pipeline = pipeline
        self._stop_evt = threading.Event()
        self._thread: threading.Thread | None = None
        self.main_sink = QtUISink()
        self.side_sink = QtUISink()

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_evt.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_evt.set()
        if self._thread:
            self._thread.join(timeout=1.0)

    def _loop(self) -> None:
        self._source.start()
        try:
            while not self._stop_evt.is_set():
                item = self._source.read()
                if item is None:
                    break
                frame, meta = item
                out, meta2 = self._pipeline.run_once(frame, meta)
                self.main_sink.push(frame, meta)
                self.side_sink.push(out, meta2)
        finally:
            self._source.stop()
