from __future__ import annotations
from core.api.interfaces import IPipelineStage
from typing import TYPE_CHECKING
import numpy as np
import cv2

if TYPE_CHECKING:
    from core.api.types import Frame, Meta



CARD_W_MM = 63.0
CARD_H_MM = 88.0
CARD_RATIO = CARD_W_MM / CARD_H_MM  # ~0.7159
OUT_W = 500
OUT_H = int(round(OUT_W * (CARD_H_MM / CARD_W_MM)))  # ~1006



class CardWarpStage(IPipelineStage):
    def process(self, frame: Frame, meta: Meta) -> (Frame, Meta):
            # pts: (4,2)
        # renvoie: [top-left, top-right, bottom-right, bottom-left]
        pts = meta.info["quad"]
        rect = np.zeros((4, 2), dtype=np.float32)
        s = pts.sum(axis=1)
        diff = np.diff(pts, axis=1)

        rect[0] = pts[np.argmin(s)]  # top-left (x+y min)
        rect[2] = pts[np.argmax(s)]  # bottom-right (x+y max)
        rect[1] = pts[np.argmin(diff)]  # top-right (x - y min)
        rect[3] = pts[np.argmax(diff)]  # bottom-left (x - y max)

        dst = np.array(
            [[0, 0], [OUT_W - 1, 0], [OUT_W - 1, OUT_H - 1], [0, OUT_H - 1]],
            dtype=np.float32,
        )
        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(frame, M, (OUT_W, OUT_H))
        return warped, meta

class CardCropStage(IPipelineStage):
    def process(self, frame: Frame, meta: Meta) -> (Frame, Meta):
        if frame is None:
            return None, None
        h, w = frame.shape[:2]
        if h == 0 or w == 0:
            return None
        band_h = max(1, int(round(0.065 * h)))
        y_deb = max(0, h - band_h)
        y_fin = h
        x_deb = int(w * 0.7)
        x_fin = w
        return frame[y_deb:y_fin, x_deb:x_fin, :], meta
