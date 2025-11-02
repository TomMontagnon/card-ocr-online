import numpy as np
import cv2
from .network import request_url, request_url_async
from PySide6 import QtGui
import asyncio


def np_to_qimage_bgr(bgr: np.ndarray) -> QtGui.QImage:
    h, w, _ = bgr.shape
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

    # print("imaging : ", bgr.shape)
    qimg = QtGui.QImage(rgb.data, w, h, 3 * w, QtGui.QImage.Format_RGB888)
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


SEM_DOWNLOAD = 20  # limite de téléchargements simultanés

sem_download = asyncio.Semaphore(SEM_DOWNLOAD)


async def np_from_url_async(
    url: str, headers=None, timeout: float = 10.0
) -> np.ndarray | None:
    try:
        async with sem_download:  # limite le nombre de téléchargements simultanés
            resp = await request_url_async(url, headers=headers, timeout=timeout)
            buf = np.frombuffer(resp.content, dtype=np.uint8)
            img_bgr = cv2.imdecode(buf, cv2.IMREAD_COLOR)
            return img_bgr
    except Exception as e:
        print("Download error:", e)
        return None
