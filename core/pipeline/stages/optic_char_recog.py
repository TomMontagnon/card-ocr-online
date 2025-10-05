from __future__ import annotations
from core.api.interfaces import IPipelineStage
from core.api.types import Expansion
from paddleocr import PaddleOCR
import cv2
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.api.types import Frame, Meta

MIN_CONF = 0.9
SEUIL_SCALE = 0.01
CHAR_HEIGHT_RATIO = 0.5


class OcrPreprocessStage(IPipelineStage):
    def process(self, frame: Frame, meta: Meta) -> (Frame, Meta):
        img_bgr = self._ensure_bgr_u8(frame)
        img_bgr_up = self._scale(img_bgr)
        print(img_bgr_up.shape)
        # base = self._clahe_bgr(img_bgr_up, clip=2.0, tiles=8)
        # soft = self._unsharp(base, amount=0.4, sigma=1.2)

        return img_bgr_up, meta

    def _ensure_bgr_u8(self, img: Frame) -> Frame:
        if img.ndim == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        if img.dtype != np.uint8:
            img = np.clip(img, 0, 255).astype(np.uint8)
        return img

    def _scale(self, img: Frame, target_char_height: int = 30) -> Frame:
        h, w = img.shape[:2]
        target_h = target_char_height / CHAR_HEIGHT_RATIO
        scale = target_h / h

        if abs(scale - 1.0) > SEUIL_SCALE:
            img = cv2.resize(
                img,
                (int(w * scale), int(h * scale)),
                interpolation=cv2.INTER_CUBIC if scale > 1 else cv2.INTER_AREA,
            )

        return img

    # def _clahe_bgr(self, img: Frame, clip: float = 2.0, tiles: int = 8) -> Frame:
    #     lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    #     l, a, b = cv2.split(lab)
    #     clahe = cv2.createCLAHE(clipLimit=clip, tileGridSize=(tiles, tiles))
    #     l = clahe.apply(l)
    #     lab = cv2.merge([l, a, b])
    #     return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    # def _unsharp(self, img: Frame, amount: float = 0.6, sigma: float = 1.0) -> Frame:
    #     blur = cv2.GaussianBlur(img, (0, 0), sigma)
    #     return cv2.addWeighted(img, 1 + amount, blur, -amount, 0)


class OcrProcessStage(IPipelineStage):
    def __init__(self) -> None:
        self.OCR = PaddleOCR(
            lang="en",
            device="cpu",
            use_angle_cls=False,
        )

    def process(self, frame: Frame, meta: Meta) -> (Frame, Meta):
        try:
            meta.info["ocr_results"] = self.OCR.predict(
                frame,
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
            )
        except Exception:
            print("OCR Exception")
        return frame, meta


class OcrExtractTextStage(IPipelineStage):
    def process(self, frame: Frame, meta: Meta) -> (Frame, Meta):
        results = meta.info.get("ocr_results", [])
        expansion = None
        idcard = None

        annotated_frame = frame.copy()
        h, w = annotated_frame.shape[:2]
        font_scale = h / 150.0

        for r in results:
            # r.print()
            # r.save_to_img("output")
            # r.save_to_json("output")
            rec_texts = r.get("rec_texts")
            rec_scores = r.get("rec_scores")
            polys = r.get("rec_polys")
            print(rec_texts, rec_scores)

            for t, s, p in zip(rec_texts, rec_scores, polys, strict=True):
                if s >= MIN_CONF:
                    # dessin sur l'image
                    poly = p.astype(int)
                    cv2.polylines(
                        annotated_frame,
                        [poly],
                        isClosed=True,
                        color=(0, 255, 0),
                        thickness=2,
                    )
                    # texte au-dessus du polygone
                    x, y = poly[3]
                    cv2.putText(
                        annotated_frame,
                        f"{t} ({float(s):.2f})" if s is not None else t,
                        (x, y + 15),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        font_scale,
                        (0, 0, 255),
                        1,
                        cv2.LINE_AA,
                    )

                    txt = t.split("/")[0]
                    if txt.isdecimal():
                        idcard = int(txt)
                        continue
                    txt = (
                        t.upper()
                        .replace("-", "_")
                        .replace("•", "_")
                        .replace("·", "_")
                        .replace("0", "O")
                    )
                    if txt in Expansion.__members__:
                        expansion = Expansion[txt]

        meta.info["idcard"] = idcard
        meta.info["expansion"] = expansion
        # retourne le frame annoté
        return annotated_frame, meta

