from __future__ import annotations
import numpy as np
from PySide6 import QtCore, QtGui
from core.api.interfaces import IFrameSink
from core.utils.imaging import np_to_qimage_bgr
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.api.types import Frame, Meta


class _Emitter(QtCore.QObject):
    frame_ready = QtCore.Signal(QtGui.QImage)


class QtUISink(IFrameSink):
    def __init__(self, *, drop_if_busy: bool = True) -> None:
        self._em = _Emitter()
        self._busy = False
        self._drop = drop_if_busy
        self._closed = True

    def open(self) -> None:
        self._closed = False

    def connect(self, slot: callable) -> None:
        # Connection queued => thread-safe si push() vient d'un thread worker
        self._em.frame_ready.connect(slot, QtCore.Qt.ConnectionType.QueuedConnection)

    def push(self, item: Frame, _: Meta) -> None:
        if self._closed:
            return
        if not isinstance(item, np.ndarray) or item.ndim != 3:
            return
        if self._drop and self._busy:
            return
        self._busy = True
        qimg = np_to_qimage_bgr(item)
        self._em.frame_ready.emit(qimg)
        self._busy = False

    def close(self) -> None:
        self._closed = True
