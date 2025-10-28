from __future__ import annotations
from PySide6 import QtCore
from card_scanner.apps.gui_qt.workers import DetectCardWorker, FetchArtsWorker
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from card_scanner.core.api import Frame, Meta, IFrameSink, IFrameSource
    from card_scanner.core.pipeline import Pipeline
    from collections.abc import Iterable


class AppController(QtCore.QObject):
    source_changed = QtCore.Signal(object)

    def __init__(
        self,
        pipelines: Iterable[Pipeline],
        sinks: Iterable[IFrameSink],
        parent: QtCore.QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._source = None
        self._main_cam_sink = sinks["sink_main"]
        self._card_id_zoom_sink = sinks["sink_side"]
        self._card_artwork_sink = sinks["sink_artwork"]

        # DETECT_CARD_WORKER
        self._thread = QtCore.QThread(self)
        self.worker = DetectCardWorker(pipelines)
        self.worker.moveToThread(self._thread)
        self.worker.frames_ready.connect(self._push)
        self._thread.started.connect(self.worker.run)

        # FETCH_ARTWORK_WORKER
        self._thread2 = QtCore.QThread(self)
        self.worker2 = FetchArtsWorker()
        self.worker2.moveToThread(self._thread2)

        # CONNEXIONS
        self.source_changed.connect(self.worker.set_source)
        self.launch()

    def _push(
        self, main_frame: Frame, main_meta: Meta, side_frame: Frame, side_meta: Meta
    ) -> None:
        self._main_cam_sink.push(main_frame, main_meta)
        self._card_id_zoom_sink.push(side_frame, side_meta)

    def set_source(self, src: IFrameSource) -> None:
        self._source = src
        self.source_changed.emit(src)

    def start(self) -> None:
        if self._source:
            self._source.start()
        if not self._thread.isRunning():
            self._thread.start()

    def stop(self) -> None:
        QtCore.QMetaObject.invokeMethod(self.worker, "stop", QtCore.Qt.QueuedConnection)
        self._thread.quit()
        self._thread.wait()

        if self._source:
            self._source.stop()

    def launch(self) -> None:
        self._main_cam_sink.open()
        self._card_id_zoom_sink.open()
        self._card_artwork_sink.open()
        self.start()
        self._thread2.start()

    def quit(self) -> None:
        self.stop()

        self._thread2.quit()
        self._thread2.wait()
