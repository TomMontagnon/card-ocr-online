import cv2
from PySide6 import QtCore
from core.api.types import Expansion, NoCardDetectedError
from core.api.types import Frame, Meta
from core.pipeline.base import Pipeline
from core.api.interfaces import IFrameSource
from collections.abc import Iterable

class DetectCardWorker(QtCore.QObject):
    frames_ready = QtCore.Signal(Frame, Meta, Frame, Meta)  # (QImage, meta)
    settings_update = QtCore.Signal(Expansion, int)
    finished = QtCore.Signal()

    def __init__(
        self,
        source: IFrameSource,
        pipelines: Iterable[Pipeline],
    ) -> None:
        super().__init__()
        self._running = False
        self.default_image = cv2.imread("yoda.png")
        self._source = source
        self._pipeline_main = pipelines["pipeline_main"]
        self._pipeline_side = pipelines["pipeline_side"]
        self._pipeline_ocr = pipelines["pipeline_ocr"]

    @QtCore.Slot()
    def run(self) -> None:
        self._running = True
        try:
            while self._running:
                item = self._source.read()
                if item is None:
                    break
                raw_frame, raw_meta = item
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
                    side_frame = self.default_image
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
                    side_frame, side_meta = self._pipeline_side.run_once(
                        raw_frame, edge_meta
                    )
                # _, ocr_meta = self._pipeline_ocr.run_once(side_frame, side_meta)
                # self.settings_update.emit(ocr_meta["expansion"], ocr_meta["idcard"])
                # self.settings_update.emit(Expansion.JTL_FR, 2)
                self.frames_ready.emit(out_frame, out_meta, side_frame, side_meta)

                QtCore.QCoreApplication.processEvents()
        finally:
            self.finished.emit()

    @QtCore.Slot()
    def stop(self) -> None:
        self._running = False
