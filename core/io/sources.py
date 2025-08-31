from __future__ import annotations
import cv2, time
from typing import Optional, Tuple
from core.api.interfaces import IFrameSource
from core.api.types import Frame, Meta

class CameraSource(IFrameSource):
    def __init__(self, index: int = 0, width: int | None = None, height: int | None = None):
        self.index = index
        self.cap: cv2.VideoCapture | None = None
        self.width, self.height = width, height

    def start(self) -> None:
        self.cap = cv2.VideoCapture(self.index, cv2.CAP_ANY)
        if self.width:  self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        if self.height: self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

    def read(self) -> Optional[Tuple[Frame, Meta]]:
        assert self.cap is not None, "call start() before read()"
        ok, frame = self.cap.read()
        if not ok:
            return None
        return frame, Meta(int(time.time() * 1000))

    def stop(self) -> None:
        if self.cap is not None:
            self.cap.release()
            self.cap = None

class VideoFileSource(IFrameSource):
    def __init__(self, path: str):
        self.path = path
        self.cap: cv2.VideoCapture | None = None

    def start(self) -> None:
        self.cap = cv2.VideoCapture(self.path)

    def read(self) -> Optional[Tuple[Frame, Meta]]:
        assert self.cap is not None
        ok, frame = self.cap.read()
        if not ok:
            return None
        return frame, Meta(int(self.cap.get(cv2.CAP_PROP_POS_MSEC)))

    def stop(self) -> None:
        if self.cap: self.cap.release(); self.cap = None
