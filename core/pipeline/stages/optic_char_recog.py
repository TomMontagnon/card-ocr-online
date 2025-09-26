from __future__ import annotations
from core.api.interfaces import IPipelineStage
from paddleocr import PaddleOCR
import cv2
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.api.types import Frame, Meta

MIN_CONF = 0.5

class OcrPreprocessStage(IPipelineStage):
    def process(self, frame: Frame, meta: Meta) -> (Frame, Meta):
        img_bgr = self._ensure_bgr_u8(frame)
        img_bgr_up = self._upscale(img_bgr, 1200)
        base = self._clahe_bgr(img_bgr_up, clip=2.0, tiles=8)
        soft = self._unsharp(base, amount=0.4, sigma=1.2)

        return soft, meta

    def _ensure_bgr_u8(self, img):
        if img.ndim == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        if img.dtype != np.uint8:
            img = np.clip(img, 0, 255).astype(np.uint8)
        return img

    def _upscale(self, img, max_side=1200):
        h, w = img.shape[:2]
        s = min(max_side / max(h, w), 2.0)
        if s > 1.01:
            img = cv2.resize(
                img, (int(w * s), int(h * s)), interpolation=cv2.INTER_CUBIC
            )
        return img

    def _clahe_bgr(self, img, clip=2.0, tiles=8):
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=clip, tileGridSize=(tiles, tiles))
        l = clahe.apply(l)
        lab = cv2.merge([l, a, b])
        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    def _unsharp(self, img, amount=0.6, sigma=1.0):
        blur = cv2.GaussianBlur(img, (0, 0), sigma)
        return cv2.addWeighted(img, 1 + amount, blur, -amount, 0)

    def _to_binarized(self, img, block=31, C=5):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return cv2.cvtColor(th, cv2.COLOR_GRAY2BGR)

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
