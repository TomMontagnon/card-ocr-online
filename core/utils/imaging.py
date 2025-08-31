import numpy as np
import cv2
from typing import Tuple

def np_to_qimage_bgr(img: np.ndarray):
    # BGR uint8 -> QImage (Format_BGR888)
    from PySide6 import QtGui
    h, w = img.shape[:2]
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    assert img.dtype == np.uint8 and img.shape[2] == 3
    return QtGui.QImage(img.data, w, h, 3*w, QtGui.QImage.Format.Format_BGR888)

