from __future__ import annotations
from core.api.interfaces import IPipelineStage
from typing import TYPE_CHECKING
import cv2
import numpy as np

if TYPE_CHECKING:
    from core.api.types import Frame, Meta


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
