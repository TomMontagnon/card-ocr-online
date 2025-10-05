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


class CardWarpStage(IPipelineStage):
    def process(self, frame: Frame, meta: Meta) -> (Frame, Meta):
        pts = meta.info["quad"]
        rect = np.zeros((4, 2), dtype=np.float32)
        s = pts.sum(axis=1)
        diff = np.diff(pts, axis=1)

        rect[0] = pts[np.argmin(s)]  # top-left (x+y min)
        rect[2] = pts[np.argmax(s)]  # bottom-right (x+y max)
        rect[1] = pts[np.argmin(diff)]  # top-right (x - y min)
        rect[3] = pts[np.argmax(diff)]  # bottom-left (x - y max)

        # -- Calcule les tailles réelles du quadrilatère
        width_top = np.linalg.norm(rect[1] - rect[0])
        width_bottom = np.linalg.norm(rect[2] - rect[3])
        height_left = np.linalg.norm(rect[3] - rect[0])
        height_right = np.linalg.norm(rect[2] - rect[1])

        est_width = (width_top + width_bottom) / 2.0
        est_height = (height_left + height_right) / 2.0

        # -- On garde la taille moyenne mais on corrige le ratio vers CARD_RATIO
        current_ratio = est_width / est_height

        if current_ratio > CARD_RATIO:
            # trop large → ajuste la hauteur
            out_w = round(est_width)
            out_h = round(est_width / CARD_RATIO)
        else:
            # trop haut → ajuste la largeur
            out_h = round(est_height)
            out_w = round(est_height * CARD_RATIO)

        dst = np.array(
            [[0, 0], [out_w - 1, 0], [out_w - 1, out_h - 1], [0, out_h - 1]],
            dtype=np.float32,
        )
        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(frame, M, (out_w, out_h))
        return warped, meta


class CardCropStage(IPipelineStage):
    def process(self, frame: Frame, meta: Meta) -> (Frame, Meta):
        if frame is None:
            return None, None
        h, w = frame.shape[:2]
        if h == 0 or w == 0:
            return None
        corner = round(0.02 * h)
        y_deb = h - round(0.065 * h)
        y_fin = h - corner
        x_deb = round(w * 0.7)
        x_fin = w - corner
        out = frame[y_deb:y_fin, x_deb:x_fin, :]
        print("OUT : ", out.shape)
        return out, meta
