from __future__ import annotations
from core.api.interfaces import IPipelineStage
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.api.types import Frame, Meta

class CardCropStage(IPipelineStage):
    def process(self, frame: Frame, meta: Meta) -> (Frame, Meta):
        if frame is None:
            return None, None
        h, w = frame.shape[:2]
        if h == 0 or w == 0:
            return None
        band_h = max(1, int(round(0.07 * h)))  # 5% de la hauteur, au moins 1 px
        y0 = max(0, h - band_h)
        x0 = 3 * w // 4  # moitié droite
        return frame[y0:h, x0:w], meta
