import cv2
from PySide6 import QtCore
from core.api.types import Expansion, NoCardDetectedError, NoSourceAvailableError
from core.api.types import Frame, Meta
from core.pipeline.base import Pipeline
from core.api.interfaces import IFrameSource
from collections.abc import Iterable
from core.io.sources import VideoFileSource


class DetectCardWorker(QtCore.QObject):
    frames_ready = QtCore.Signal(Frame, Meta, Frame, Meta)
    card_detected = QtCore.Signal(Expansion, int)
    finished = QtCore.Signal()

    def __init__(
        self,
        pipelines: Iterable[Pipeline],
    ) -> None:
        super().__init__()
        self._running = False
        self._default_side_image = cv2.imread(
            "apps/gui_qt/images/no_zoom_available.png"
        )
        self._default_main_image = cv2.imread(
            "apps/gui_qt/images/no_image_source_available.png"
        )
        self._source = None
        self.set_source(VideoFileSource("videos/video0.mp4"))
        self._pipeline_main = pipelines["pipeline_main"]
        self._pipeline_side = pipelines["pipeline_side"]
        self._pipeline_ocr = pipelines["pipeline_ocr"]

    @QtCore.Slot()
    def run(self) -> None:
        self._running = True
        while self._running:
            QtCore.QCoreApplication.processEvents()
            try:
                if not self._source:
                    m = "rez"
                    raise NoSourceAvailableError(m)
                raw_frame, raw_meta = self._source.read()
            except NoSourceAvailableError:
                self.frames_ready.emit(
                    self._default_main_image,
                    Meta(),
                    self._default_side_image,
                    Meta(),
                )
                QtCore.QThread.msleep(100)
                continue
            out_frame, out_meta = raw_frame.copy(), raw_meta
            try:
                _, edge_meta = self._pipeline_main.run_once(raw_frame, raw_meta)
                # raise NoCardDetectedError("fr")
                cv2.polylines(
                    out_frame,
                    [edge_meta.info["quad"].astype(int)],
                    True,
                    (0, 255, 0),
                    3,
                )
                cv2.putText(
                    out_frame,
                    "Card detected",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2,
                )
            except NoCardDetectedError:
                side_frame = self._default_side_image
                side_meta = raw_meta
                cv2.putText(
                    out_frame,
                    "No card",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2,
                )
            else:
                tmp_frame, tmp_meta = self._pipeline_side.run_once(raw_frame, edge_meta)
                side_frame, side_meta = self._pipeline_ocr.run_once(tmp_frame, tmp_meta)
                if side_meta.info["expansion"] and side_meta.info["idcard"]:
                    self.card_detected.emit(
                        side_meta.info["expansion"], side_meta.info["idcard"]
                    )
            self.frames_ready.emit(out_frame, out_meta, side_frame, side_meta)

        self.frames_ready.emit(
            self._default_main_image, Meta(), self._default_side_image, Meta()
        )
        self.finished.emit()

    @QtCore.Slot()
    def stop(self) -> None:
        self._running = False

    @QtCore.Slot()
    def set_source(self, src: IFrameSource) -> None:
        self._source = src
        self._source.start()
