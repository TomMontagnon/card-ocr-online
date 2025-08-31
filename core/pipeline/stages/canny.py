from __future__ import annotations
import cv2
from core.api.interfaces import IPipelineStage
from core.api.types import Frame, Meta

class CannyStage(IPipelineStage):
    def __init__(self, low: int = 50, high: int = 150):
        self.low, self.high = low, high

    def process(self, frame: Frame, meta: Meta):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if frame.ndim == 3 else frame
        edges = cv2.Canny(gray, self.low, self.high)
        bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        return bgr, meta
