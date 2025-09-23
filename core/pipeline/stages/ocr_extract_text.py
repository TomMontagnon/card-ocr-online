from __future__ import annotations
from core.api.interfaces import IPipelineStage
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.api.types import Frame, Meta

MIN_CONF = 0.5

class OcrExtractTextStage(IPipelineStage):
    def process(self, frame: Frame, meta: Meta) -> (Frame, Meta):
        results = meta.info["ocr_results"]
        out = []

        def accept(t, s) -> bool:
            try:
                return bool(t) and (s is None or float(s) >= MIN_CONF)
            except Exception:
                return bool(t)

        for r in results:
            # 1) Cas mapping/dict (PaddleX 3.x OCRResult dict-like)
            if hasattr(r, "keys") and hasattr(r, "get"):
                rec_texts = r.get("rec_texts") or r.get("texts")
                rec_scores = r.get("rec_scores") or r.get("scores")
                polys = r.get("boxes") or r.get("polygons")
                if rec_texts is not None:
                    if rec_scores is None:
                        rec_scores = [None] * len(rec_texts)
                    if polys is None:
                        polys = [None] * len(rec_texts)
                    for t, s, p in zip(rec_texts, rec_scores, polys):
                        if accept(t, s):
                            out.append((t, float(s) if s is not None else None, p))
                    continue
        meta.info["out"] = out
        return frame, meta
