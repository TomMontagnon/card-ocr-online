from __future__ import annotations
import cv2
import time
from core.api.interfaces import IFrameSource
from core.api.types import Frame, Meta


class CameraSource(IFrameSource):
    def __init__(
        self, index: int = 0, width: int | None = None, height: int | None = None
    ) -> None:
        self._index = index
        self._cap: cv2.VideoCapture | None = None
        self._width, self._height = width, height

    def start(self) -> None:
        self._cap = cv2.VideoCapture(self._index, cv2.CAP_ANY)
        if self._width:
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
        if self._height:
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)

    def read(self) -> tuple[Frame, Meta] | None:
        if self._cap is None:
            m = "self.cap not initiated"
            raise ValueError(m)
        ok, frame = self._cap.read()
        if not ok:
            return None
        return frame, Meta(int(time.time() * 1000))

    def stop(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None


class RtspSource(IFrameSource):
    def __init__(
        self, url: str, width: int | None = None, height: int | None = None
    ) -> None:
        self._url = url
        self._cap: cv2.VideoCapture | None = None
        self._width, self._height = width, height

    def start(self) -> None:
        self._cap = cv2.VideoCapture(self._url, cv2.CAP_ANY)
        if self._width:
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
        if self._height:
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)

    def read(self) -> tuple[Frame, Meta] | None:
        if self._cap is None:
            m = "self.cap not initiated"
            raise ValueError(m)
        ok, frame = self._cap.read()
        if not ok:
            return None
        return frame, Meta(int(time.time() * 1000))

    def stop(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None


class VideoFileSource(IFrameSource):
    def __init__(self, path: str, fps: int = 5) -> None:
        self._path = path
        self._cap: cv2.VideoCapture | None = None
        self._target_dt = 1.0 / fps
        self._last_time = None

    def start(self) -> None:
        self._cap = cv2.VideoCapture(self._path)
        self._last_time = time.time()

    def read(self) -> tuple[Frame, Meta] | None:
        if self._cap is None:
            m = "self.cap not initiated"
            raise ValueError(m)
        ok, frame = self._cap.read()

        if not ok:
            # on est arrivé à la fin : repartir au début
            self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ok, frame = self._cap.read()
            if not ok:
                return None

        now = time.time()
        if self._last_time is not None:
            elapsed = now - self._last_time
            to_sleep = self._target_dt - elapsed
            if to_sleep > 0:
                time.sleep(to_sleep)
        self._last_time = time.time()

        return frame.copy(), Meta(int(self._cap.get(cv2.CAP_PROP_POS_MSEC)))

    def stop(self) -> None:
        if self._cap:
            self._cap.release()
            self._cap = None
