from __future__ import annotations
from core.api.interfaces import IPipelineStage
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.api.types import Frame, Meta

class OcrPrintResultsStage(IPipelineStage):
    def process(self, frame: Frame, meta: Meta) -> (Frame, Meta):
        lines = meta.info["out"]
        if not lines:
            print("[OCR] Aucun texte détecté (>=0.3). Active le mode debug pour inspecter.")
        print(f"[OCR] {len(lines)} éléments:")
        for i, (t, s, poly) in enumerate(lines):
            if s is not None:
                print(f"  {i:02d}. {t} (score={s:.3f})")
            else:
                print(f"  {i:02d}. {t} (score=NA)")
            if poly is not None:
                # poly est typiquement une liste de 4 points [[x,y],...]
                try:
                    xs = [int(p[0]) for p in poly]
                    ys = [int(p[1]) for p in poly]
                    print(f"      box=({min(xs)},{min(ys)})-({max(xs)},{max(ys)})")
                except Exception:
                    pass
        return frame, meta
