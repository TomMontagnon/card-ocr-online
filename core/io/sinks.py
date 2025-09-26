from __future__ import annotations
import cv2
from pathlib import Path
from core.api.interfaces import IFrameSink
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable
    from core.api.types import Meta
    import numpy as np


class NullSink(IFrameSink):
    def push(self, item: np.ndarray, meta: Meta) -> None:
        pass

    def connect(self, slot: callable) -> None:
        pass

    def close(self) -> None:
        pass


class VideoWriterSink(IFrameSink):
    def __init__(self, path: str, fps: float = 30.0) -> None:
        self._path = Path(path)
        self._writer = None
        self._fps = fps

    def _ensure(self, w: int, h: int) -> None:
        if self._writer is None:
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            self._writer = cv2.VideoWriter(str(self._path), fourcc, self._fps, (w, h))

    def push(self, item: np.ndarray, meta: Meta) -> None:
        # item doit être BGR uint8 shape (H,W,3)
        self._ensure(item.shape[1], item.shape[0])
        self._writer.write(item)

    def connect(self, slot: callable) -> None:
        pass

    def close(self) -> None:
        if self._writer:
            self._writer.release()
            self._writer = None


class CompositeSink(IFrameSink):
    def __init__(self, sinks: Iterable[IFrameSink]) -> None:
        self._sinks = sinks

    def push(self, item: np.ndarray, meta: Meta) -> None:
        for s in self._sinks:
            s.push(item, meta)

    def connect(self, slot: callable) -> None:
        for s in self._sinks:
            s.connect(slot)

    def close(self) -> None:
        for s in self._sinks:
            s.close()
