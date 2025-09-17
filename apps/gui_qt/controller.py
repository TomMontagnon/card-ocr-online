from __future__ import annotations
import threading
from PySide6 import QtCore, QtGui
from apps.gui_qt.qt_ui_sink import QtUISink
from typing import TYPE_CHECKING
from core.api.types import Meta
import requests
import numpy as np
import cv2
from core.api.types import Expansion,NoCardDetectedError

if TYPE_CHECKING:
    from core.pipeline.base import Pipeline
    from core.api.interfaces import IFrameSource
    from apps.widgets.settings_widget import SettingsWidget


def pixmap_from_url(url: str, timeout: float = 10.0) -> QtGui.QPixmap | None:
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        buf = np.frombuffer(r.content, dtype=np.uint8)  # 1D uchar buffer
        img_bgr = cv2.imdecode(buf, cv2.IMREAD_COLOR)  # HxWx3, BGR, uint8
        # img = QtGui.QImage.fromData(r.content)
        # if img.isNull():
        #     return None
        # return QtGui.QPixmap.fromImage(img)
    except Exception as e:
        print("Download error:", e)
        img_bgr = None
    return img_bgr


class AppController(QtCore.QObject):
    def __init__(
        self,
        source: IFrameSource,
        pipeline_main: Pipeline,
        pipeline_side: Pipeline,
        setting_widget: SettingsWidget,
        parent: QtCore.QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._source = source
        self._pipeline_main = pipeline_main
        self._pipeline_side = pipeline_side
        self._stop_evt = threading.Event()
        self._thread: threading.Thread | None = None
        self._setting_widget = setting_widget
        self.main_cam_sink = QtUISink()
        self.card_id_zoom_sink = QtUISink()
        self.card_artwork_sink = QtUISink()
        self.image = pixmap_from_url(
            "https://cdn.starwarsunlimited.com/SWH_01fr_045_Yoda_477278dec2.png"
        )

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
                frame, meta = item
                try:
                    frame2, meta2 = self._pipeline_main.run_once(frame, meta)
                    frame3, meta3 = self._pipeline_side.run_once(frame, meta2)
                    txt = "LOF-FR 45"  # foo(out)
                    self._setting_widget.set_value(
                        Expansion.JTL_FR, 2, auto_detect=True
                    )

                    cv2.polylines(
                        frame, [meta2.info["quad"].astype(int)], True, (0, 255, 0), 3
                    )
                    cv2.putText(
                        frame,
                        "Card detected",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        2,
                    )

                except NoCardDetectedError:
                    frame3 = pixmap_from_url(
                        "https://cdn.starwarsunlimited.com/SWH_01fr_045_Yoda_477278dec2.png"
                    )
                    meta3 = meta
                    cv2.putText(
                        frame,
                        "No card",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 0, 255),
                        2,
                    )

                # SINK PUSHED
                self.main_cam_sink.push(frame, meta)
                self.card_id_zoom_sink.push(frame3, meta3)
                # Expansion, idCard = (Expansion.LOF_FR, 45)#foo2(txt)

                self.card_artwork_sink.push(self.image, Meta(0))
        finally:
            self._source.stop()
