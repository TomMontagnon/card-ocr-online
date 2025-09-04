from __future__ import annotations
import cv2
from pathlib import Path
from core.api.interfaces import IFrameSink
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.api.types import Meta


class NullSink(IFrameSink):
    def push(self, item, meta: Meta) -> None:
        pass

class VideoWriterSink(IFrameSink):
    def __init__(self, path: str, fps: float = 30.0) -> None:
        self.path = Path(path)
        self.writer = None
        self.fps = fps

    def _ensure(self, w: int, h: int) -> None:
        if self.writer is None:
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            self.writer = cv2.VideoWriter(str(self.path), fourcc, self.fps, (w, h))

    def push(self, item, meta: Meta) -> None:
        # item doit être BGR uint8 shape (H,W,3)
        self._ensure(item.shape[1], item.shape[0])
        self.writer.write(item)

    def close(self) -> None:
        if self.writer:
            self.writer.release()
            self.writer = None
