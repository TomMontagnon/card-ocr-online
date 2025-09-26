from __future__ import annotations
import cv2
import numpy as np
from core.api.types import NoCardDetectedError
from core.api.interfaces import IPipelineStage
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.api.types import Frame, Meta


class CardDetectorStage(IPipelineStage):
    def process(self, frame: Frame, meta: Meta) -> (Frame, Meta):
        # Contours
        cnts, _ = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not cnts:
            msg = "no contours found"
            raise NoCardDetectedError(msg)

        h, w = frame.shape
        img_area = h * w

        # Trier par aire décroissante pour trouver "la" carte dominante
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

        for c in cnts:
            area = cv2.contourArea(c)
            if area < 0.1 * img_area:  # ignorer petits objets (<10% de l'image)
                msg = "no big enough contours found"
                raise NoCardDetectedError(msg)

            # Vérifier ratio via bounding box minAreaRect
            rect = cv2.minAreaRect(c)
            (cx, cy), (wrect, hrect), angle = rect
            if wrect == 0 or hrect == 0:
                continue
            aspect = min(wrect, hrect) / max(wrect, hrect)  # ratio <= 1

            # Une carte Magic ~0.716, tolérance +/- ~0.06
            if 0.66 <= aspect <= 0.76:
                # OK, on renvoie les 4 points (float32)
                box = cv2.boxPoints(rect)
                meta.info["quad"] = box.reshape(-1, 2).astype(np.float32)
                return frame, meta
        msg = "no good aspect contours found"
        raise NoCardDetectedError(msg)


class EdgeExtractionStage(IPipelineStage):
    def process(self, frame: Frame, meta: Meta) -> (Frame, Meta):
        # pretraitement
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        # Bords et renforcement
        edges = cv2.Canny(gray, 60, 180)
        edges = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=1)
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

        return edges, meta
