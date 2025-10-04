from __future__ import annotations
from PySide6 import QtCore

# from core.io.sinks import CompositeSink, VideoWriterSink
from apps.gui_qt.workers.detect_card_worker import DetectCardWorker
from apps.gui_qt.workers.fetch_art_worker import FetchArtWorker
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.api.types import Frame, Meta
    from core.pipeline.base import Pipeline
    from core.api.interfaces import IFrameSource
    from core.api.interfaces import IFrameSink
    from collections.abc import Iterable


class AppController(QtCore.QObject):
    def __init__(
        self,
        source: IFrameSource,
        pipelines: Iterable[Pipeline],
        sinks: Iterable[IFrameSink],
        parent: QtCore.QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._source = source
        self._pipelines = pipelines
        self._main_cam_sink = sinks["sink_main"]
        self._card_id_zoom_sink = sinks["sink_side"]
        self._card_artwork_sink = sinks["sink_artwork"]

        self._thread = None
        self._thread2 = None
        self.start()

    def _push(
        self, main_frame: Frame, main_meta: Meta, side_frame: Frame, side_meta: Meta
    ) -> None:
        self._main_cam_sink.push(main_frame, main_meta)
        self._card_id_zoom_sink.push(side_frame, side_meta)

    def start(self) -> None:
        self._main_cam_sink.open()
        self._card_id_zoom_sink.open()
        self._card_artwork_sink.open()
        self._source.start()

        # DETECT_CARD_WORKER
        if self._thread is None or not self._thread.isRunning():
            self.worker = DetectCardWorker(self._source, self._pipelines)
            self.worker.frames_ready.connect(self._push)
            self._thread = QtCore.QThread(self)
            self.worker.moveToThread(self._thread)
            self._thread.started.connect(self.worker.run)
            self._thread.start()

        # FETCH_ARTWORK_WORKER
        if self._thread2 is None or not self._thread2.isRunning():
            self.worker2 = FetchArtWorker()
            self.worker2.frame_ready.connect(self._card_artwork_sink.push)
            self._thread2 = QtCore.QThread(self)
            self.worker2.moveToThread(self._thread2)
            self._thread2.start()

    def stop(self) -> None:
        QtCore.QMetaObject.invokeMethod(self.worker, "stop", QtCore.Qt.QueuedConnection)
        self._thread.quit()
        self._thread.wait()

        self._thread2.quit()
        self._thread2.wait()

        self._source.stop()
        self._main_cam_sink.close()
        self._card_id_zoom_sink.close()
        self._card_artwork_sink.close()
