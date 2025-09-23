import numpy as np
import cv2
from core.utils.network import request_url
from PySide6 import QtGui

# def np_to_qimage_bgr(img: np.ndarray):
#     # BGR uint8 -> QImage (Format_BGR888)
#     from PySide6 import QtGui
#     h, w = img.shape[:2]
#     if img.ndim == 2:
#         img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
#     assert img.dtype == np.uint8 and img.shape[2] == 3
#     return QtGui.QImage(img.data, w, h, 3*w, QtGui.QImage.Format.Format_BGR888)

def np_to_qimage_bgr(bgr: np.ndarray) -> QtGui.QImage:
    h, w, _ = bgr.shape
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    qimg = QtGui.QImage(rgb.data, w, h, 3*w, QtGui.QImage.Format_RGB888)
    return qimg.copy()  # copie pour décorréler du buffer numpy


def np_from_url(url: str, timeout: float = 10.0) -> np.ndarray | None:
    try:
        resp = request_url(url)
        buf = np.frombuffer(resp.content, dtype=np.uint8)  # 1D uchar buffer
        img_bgr = cv2.imdecode(buf, cv2.IMREAD_COLOR)  # HxWx3, BGR, uint8
    except Exception as e:
        print("Download error:", e)
        img_bgr = None
    return img_bgr
