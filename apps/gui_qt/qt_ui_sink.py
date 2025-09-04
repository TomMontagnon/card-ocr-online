from __future__ import annotations
import cv2
import numpy as np
from PySide6 import QtCore, QtGui
from core.api.interfaces import IFrameSink
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.api.types import Meta

class _Emitter(QtCore.QObject):
    frame_ready = QtCore.Signal(QtGui.QImage)

def np_to_qimage_bgr(bgr: np.ndarray) -> QtGui.QImage:
    h, w, _ = bgr.shape
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    qimg = QtGui.QImage(rgb.data, w, h, 3*w, QtGui.QImage.Format_RGB888)
    return qimg.copy()  # copie pour décorréler du buffer numpy

class QtUISink(IFrameSink):
    def __init__(self, *,drop_if_busy: bool = True) -> None:
        self._em = _Emitter()
        self.frame_ready = self._em.frame_ready
        self._busy = False
        self._drop = drop_if_busy

    def connect(self, slot) -> None:
        # VideoView.set_frame par ex.
        # Connection queued => thread-safe si push() vient d’un thread worker
        self.frame_ready.connect(slot, QtCore.Qt.ConnectionType.QueuedConnection)

    def push(self, item, meta: Meta) -> None:
        if not isinstance(item, np.ndarray) or item.ndim != 3:
            return
        if self._drop and self._busy:
            return
        self._busy = True
        qimg = np_to_qimage_bgr(item)
        # émettre dans le thread UI
        self._em.frame_ready.emit(qimg)
        self._busy = False

