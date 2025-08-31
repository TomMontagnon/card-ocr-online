from __future__ import annotations
import threading
from typing import Callable
from PySide6 import QtCore
from core.api.types import Frame, Meta
from core.pipeline.base import Pipeline
from core.api.interfaces import IFrameSource
from core.utils.imaging import np_to_qimage_bgr

class QtImageSink(QtCore.QObject):
    frame_ready = QtCore.Signal(object)  # emits QImage

    def push_np(self, img_np):
        qimg = np_to_qimage_bgr(img_np)
        # Deep copy to detach from numpy buffer lifetime
        self.frame_ready.emit(qimg.copy())

class AppController(QtCore.QObject):
    def __init__(self, source: IFrameSource, pipeline: Pipeline, parent=None):
        super().__init__(parent)
        self._source = source
        self._pipeline = pipeline
        self._stop_evt = threading.Event()
        self._thread: threading.Thread | None = None
        self.sink = QtImageSink()

    def start(self):
        if self._thread and self._thread.is_alive(): return
        self._stop_evt.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_evt.set()
        if self._thread:
            self._thread.join(timeout=1.0)

    def _loop(self):
        self._source.start()
        try:
            while not self._stop_evt.is_set():
                item = self._source.read()
                if item is None:
                    break
                frame, meta = item
                out, meta2 = self._pipeline.run_once(frame, meta)
                self.sink.push_np(out)
        finally:
            self._source.stop()
