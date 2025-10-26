from __future__ import annotations
from collections import deque, Counter
from core.api.interfaces import IPipelineStage
from core.api.types import Expansion
from paddleocr import PaddleOCR
import cv2
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.api.types import Frame, Meta

MIN_CONF = 0.8
SEUIL_SCALE = 0.01
CHAR_HEIGHT_RATIO = 0.25


class OcrPreprocessStage(IPipelineStage):
    def process(self, frame: Frame, meta: Meta) -> (Frame, Meta):
        img_bgr = self._ensure_bgr_u8(frame)
        img_bgr_up = self._scale(img_bgr)

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

        for r in results:
            # r.print()
            # r.save_to_img("output")
            # r.save_to_json("output")
            rec_texts = r.get("rec_texts")
            rec_scores = r.get("rec_scores")
            polys = r.get("rec_polys")
            # print(rec_texts, rec_scores)

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

                    poly_width = np.linalg.norm(poly[1] - poly[0])
                    n_chars = max(len(t), 1)  # éviter division par zéro
                    font_scale = poly_width / n_chars / 30.0

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

                    txt = (
                        t.upper()
                        .replace(".", "_")
                        .replace("-", "_")
                        .replace("•", "_")
                        .replace("·", "_")
                    )

                    if "_" in txt:  # EXPANSION
                        if txt in Expansion.__members__:
                            txt = txt.replace("0", "O")
                            expansion = Expansion[txt]
                        else:
                            print(f"ERROR, expansion not recognized : {txt}")
                    else:  # ID_CARD
                        txt = t.split("/")[0]
                        if len(txt) > 0 and txt[0] == "T":
                            print("TOKEN, OSEF")
                            break

                        if txt.isdecimal():
                            idcard = int(txt)
                        else:
                            print(f"ERROR, id_card not recognized : {txt}")

        meta.info["idcard"] = idcard
        meta.info["expansion"] = expansion
        # retourne le frame annoté
        return annotated_frame, meta


class OcrMeanYield(IPipelineStage):
    def __init__(self, history_depth: int = 10) -> None:
        """
        history_depth : nombre de derniers résultats à retenir
        """
        self.history_depth = history_depth
        self._history: deque[(str, int)] = deque(maxlen=history_depth)

    def process(self, frame: Frame, meta: Meta) -> (Frame, Meta):
        # récupère le couple courant s'il existe
        expansion = meta.info.get("expansion")
        idcard = meta.info.get("idcard")

        if expansion is not None and idcard is not None:
            # ajoute le couple dans l'historique
            self._history.append((expansion, idcard))

        if self._history:
            # calcul du couple le plus fréquent
            most_common = Counter(self._history).most_common(1)[0][0]
            meta.info["expansion"], meta.info["idcard"] = most_common

        return frame, meta
