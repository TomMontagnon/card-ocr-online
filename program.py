import cv2
import numpy as np
from paddleocr import PaddleOCR

# Proportions d'une carte Magic (mm) ~ 63 x 88
CARD_W_MM = 63.0
CARD_H_MM = 88.0
CARD_RATIO = CARD_W_MM / CARD_H_MM  # ~0.7159
RTSP_URL = "http://192.168.1.82:8080/video/mjpeg"

# Taille de sortie en pixels (gardez le ratio 63:88)
OUT_W = 500
OUT_H = int(round(OUT_W * (CARD_H_MM / CARD_W_MM)))  # ~1006


OCR = PaddleOCR(
    lang="en",  # "en" ou "fr" selon ton cas
    device="cpu",  # "gpu:0" si CUDA ok
    use_textline_orientation=False,
)


def _ensure_bgr_u8(img):
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    if img.dtype != np.uint8:
        img = np.clip(img, 0, 255).astype(np.uint8)
    return img


def _upscale(img, max_side=1200):
    h, w = img.shape[:2]
    s = min(max_side / max(h, w), 2.0)
    if s > 1.01:
        img = cv2.resize(img, (int(w * s), int(h * s)), interpolation=cv2.INTER_CUBIC)
    return img


def _clahe_bgr(img, clip=2.0, tiles=8):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clip, tileGridSize=(tiles, tiles))
    l = clahe.apply(l)
    lab = cv2.merge([l, a, b])
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)


def _unsharp(img, amount=0.6, sigma=1.0):
    blur = cv2.GaussianBlur(img, (0, 0), sigma)
    return cv2.addWeighted(img, 1 + amount, blur, -amount, 0)


def _to_binarized(img, block=31, C=5):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return cv2.cvtColor(th, cv2.COLOR_GRAY2BGR)


def preprocess_img(img0):
    img_bgr = _ensure_bgr_u8(img0)
    img_bgr_up = _upscale(img_bgr, 1200)
    base = _clahe_bgr(img_bgr_up, clip=2.0, tiles=8)
    soft = _unsharp(base, amount=0.4, sigma=1.2)
    # return _to_binarized(soft)
    return soft


def extract_texts(results, min_conf=0.3):
    out = []

    def accept(t, s):
        try:
            return bool(t) and (s is None or float(s) >= min_conf)
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
    return out


def _find_card_quad(bgr):
    # Prétraitements
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    # Bords et renforcement
    edges = cv2.Canny(gray, 60, 180)
    edges = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=1)
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

    # Contours
    cnts, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        return None, edges

    h, w = gray.shape
    img_area = w * h

    # Trier par aire décroissante pour trouver "la" carte dominante
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

    for c in cnts:
        area = cv2.contourArea(c)
        if area < 0.02 * img_area:  # ignorer petits objets (<2% de l'image)
            continue

        # Approx polygone
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)  # 2% du périmètre

        if len(approx) != 4 or not cv2.isContourConvex(approx):
            continue

        # Vérifier ratio via bounding box minAreaRect
        rect = cv2.minAreaRect(approx)
        (cx, cy), (wrect, hrect), angle = rect
        if wrect == 0 or hrect == 0:
            continue
        aspect = min(wrect, hrect) / max(wrect, hrect)  # ratio <= 1

        # Une carte Magic ~0.716, tolérance +/- ~0.06
        if 0.66 <= aspect <= 0.76:
            # OK, on renvoie les 4 points (float32)
            quad = approx.reshape(-1, 2).astype(np.float32)
            return quad, edges

    return None, edges


def _order_points_clockwise(pts):
    # pts: (4,2)
    # renvoie: [top-left, top-right, bottom-right, bottom-left]
    rect = np.zeros((4, 2), dtype=np.float32)
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)

    rect[0] = pts[np.argmin(s)]  # top-left (x+y min)
    rect[2] = pts[np.argmax(s)]  # bottom-right (x+y max)
    rect[1] = pts[np.argmin(diff)]  # top-right (x - y min)
    rect[3] = pts[np.argmax(diff)]  # bottom-left (x - y max)
    return rect


def _warp_card(bgr, quad, out_w=OUT_W, out_h=OUT_H):
    src = _order_points_clockwise(quad)
    dst = np.array(
        [[0, 0], [out_w - 1, 0], [out_w - 1, out_h - 1], [0, out_h - 1]],
        dtype=np.float32,
    )
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(bgr, M, (out_w, out_h))
    return warped, M


def bottom_right_roi(img):
    """Retourne l'intersection: bas 5% × droite 50% d'une image BGR."""
    if img is None:
        return None
    h, w = img.shape[:2]
    if h == 0 or w == 0:
        return None
    band_h = max(1, int(round(0.07 * h)))  # 5% de la hauteur, au moins 1 px
    y0 = max(0, h - band_h)
    x0 = 3 * w // 4  # moitié droite
    return img[y0:h, x0:w]


def process_frame(frame):
    quad, edges = _find_card_quad(frame)
    vis = frame.copy()
    warped = None
    if quad is not None:
        # Dessiner le quadrilatère détecté
        cv2.polylines(vis, [quad.astype(int)], True, (0, 255, 0), 3)

        # Redressement
        warped, _ = _warp_card(frame, quad, OUT_W, OUT_H)

        # Afficher quelques infos
        cv2.putText(
            vis, "Card detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
        )
    else:
        cv2.putText(
            vis, "No card", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2
        )

    return vis, edges, warped


def print_results(lines):
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


# Exemple boucle vidéo (depuis RTSP ou webcam locale)
def main() -> None:
    cap = cv2.VideoCapture(RTSP_URL)
    if not cap.isOpened():
        raise RuntimeError("Impossible d'ouvrir la source video")

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("Perte du flux")
                break

            vis, edges, warped = process_frame(frame)
            cv2.imshow("Input + detection", vis)
            cv2.imshow("Edges", edges)
            if warped is not None:
                warped_roi = bottom_right_roi(warped)
                warped_roi_filtred = preprocess_img(warped_roi)
                cv2.imshow("Card rectifiee (63:88)", warped_roi_filtred)

                results = OCR.predict(
                    warped_roi_filtred, use_textline_orientation=False
                )
                lines = extract_texts(results, min_conf=0.3)
                print_results(lines)

            key = cv2.waitKey(1) & 0xFF
            if key in (27, ord("q")):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
