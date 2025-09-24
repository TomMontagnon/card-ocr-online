from __future__ import annotations
from core.api.interfaces import IPipelineStage
from paddleocr import PaddleOCR
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.api.types import Frame, Meta

class OcrProcessStage(IPipelineStage):
    def __init__(self) -> None:
        self.OCR = PaddleOCR(
            lang="en",
            device="cpu",  # "gpu:0" si CUDA ok
            use_textline_orientation=False,
        )
    def process(self, frame: Frame, meta: Meta) -> (Frame, Meta):
        meta.info["ocr_results"] = self.OCR.predict(
            frame, use_textline_orientation=False
        )
        return frame, meta
