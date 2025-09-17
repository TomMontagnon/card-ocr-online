from __future__ import annotations
import cv2
import numpy as np
from core.api.interfaces import IPipelineStage
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.api.types import Frame, Meta


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
