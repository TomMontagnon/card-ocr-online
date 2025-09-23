from __future__ import annotations
import threading
import cv2
from PySide6 import QtCore
from core.api.types import Meta
from apps.gui_qt.qt_ui_sink import QtUISink
from core.api.types import Expansion, NoCardDetectedError
from core.utils.fetch_artwork import FetchArtwork
from core.utils.imaging import np_from_url

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.pipeline.base import Pipeline
    from core.api.interfaces import IFrameSource
    from apps.widgets.settings_widget import SettingsWidget


class AppController(QtCore.QObject):
    def __init__(
        self,
        source: IFrameSource,
        pipeline_main: Pipeline,
        pipeline_side: Pipeline,
        pipeline_ocr: Pipeline,
        setting_widget: SettingsWidget,
        parent: QtCore.QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._source = source
        self._pipeline_main = pipeline_main
        self._pipeline_side = pipeline_side
        self._pipeline_ocr = pipeline_ocr
        self._stop_evt = threading.Event()
        self._thread: threading.Thread | None = None
        self.setting_widget = setting_widget
        self.main_cam_sink = QtUISink()
        self.card_id_zoom_sink = QtUISink()
        self.card_artwork_sink = QtUISink()
        self.image = self.image = np_from_url(
            "https://cdn.starwarsunlimited.com/SWH_01fr_045_Yoda_477278dec2.png"
        )
        self.default_art_url = (
            "https://cdn.starwarsunlimited.com/SWH_01fr_045_Yoda_477278dec2.png"
        )

        self.fetchArt = FetchArtwork()
        self.setting_widget.connect(self.fetchArt.process)
        self.fetchArt.connect(self.card_artwork_sink.push)

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_evt.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_evt.set()
        if self._thread:
            self._thread.join(timeout=1.0)

    def _loop(self) -> None:
        self._source.start()
        try:
            while not self._stop_evt.is_set():
                item = self._source.read()
                if item is None:
                    break
                raw_frame, raw_meta = item
                try:
                    main_frame, main_meta = self._pipeline_main.run_once(
                        raw_frame, raw_meta
                    )
                    side_frame, side_meta = self._pipeline_side.run_once(
                        main_frame, main_meta
                    )
                    _, ocr_meta = self._pipeline_ocr.run_once(side_frame, side_meta)
                    self.setting_widget.set_value(Expansion.JTL_FR, 2, auto_detect=True)
                    # self.setting_widget.set_value(
                    #     ocr_meta["expansion"], ocr_meta["idcard"], auto_detect=True
                    # )

                    cv2.polylines(
                        raw_frame,
                        [main_meta.info["quad"].astype(int)],
                        True,
                        (0, 255, 0),
                        3,
                    )
                    cv2.putText(
                        raw_frame,
                        "Card detected",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        2,
                    )

                except NoCardDetectedError:
                    side_frame = self.fetchArt.process2(self.default_art_url)
                    side_meta = raw_meta
                    cv2.putText(
                        raw_frame,
                        "No card",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 0, 255),
                        2,
                    )

                # SINK PUSHED
                self.main_cam_sink.push(raw_frame, raw_meta)
                self.card_id_zoom_sink.push(side_frame, side_meta)
                # Expansion, idCard = (Expansion.LOF_FR, 45)#foo2(txt)

                # self.card_artwork_sink.push(self.image, Meta(0))
        finally:
            self._source.stop()
