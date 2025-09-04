from __future__ import annotations
import cv2
import time
from core.api.interfaces import IFrameSource
from core.api.types import Frame, Meta


class CameraSource(IFrameSource):
    def __init__(
        self, index: int = 0, width: int | None = None, height: int | None = None
    ) -> None:
        self.index = index
        self.cap: cv2.VideoCapture | None = None
        self.width, self.height = width, height

    def start(self) -> None:
        self.cap = cv2.VideoCapture(self.index, cv2.CAP_ANY)
        if self.width:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        if self.height:
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

    def read(self) -> tuple[Frame, Meta] | None:
        if self.cap is None:
            m = "self.cap not initiated"
            raise ValueError(m)
        ok, frame = self.cap.read()
        if not ok:
            return None
        return frame, Meta(int(time.time() * 1000))

    def stop(self) -> None:
        if self.cap is not None:
            self.cap.release()
            self.cap = None


class RtspSource(IFrameSource):
    def __init__(
        self, url: str, width: int | None = None, height: int | None = None
    ) -> None:
        self.url = url
        self.cap: cv2.VideoCapture | None = None
        self.width, self.height = width, height

    def start(self) -> None:
        self.cap = cv2.VideoCapture(self.url, cv2.CAP_ANY)
        if self.width:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        if self.height:
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

    def read(self) -> tuple[Frame, Meta] | None:
        if self.cap is None:
            m = "self.cap not initiated"
            raise ValueError(m)
        ok, frame = self.cap.read()
        if not ok:
            return None
        return frame, Meta(int(time.time() * 1000))

    def stop(self) -> None:
        if self.cap is not None:
            self.cap.release()
            self.cap = None


class VideoFileSource(IFrameSource):
    def __init__(self, path: str) -> None:
        self.path = path
        self.cap: cv2.VideoCapture | None = None

    def start(self) -> None:
        self.cap = cv2.VideoCapture(self.path)

    def read(self) -> tuple[Frame, Meta] | None:
        if self.cap is None:
            m = "self.cap not initiated"
            raise ValueError(m)
        ok, frame = self.cap.read()
        if not ok:
            return None
        return frame, Meta(int(self.cap.get(cv2.CAP_PROP_POS_MSEC)))

    def stop(self) -> None:
        if self.cap:
            self.cap.release()
            self.cap = None
