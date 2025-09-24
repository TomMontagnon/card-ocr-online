import cv2
import numpy as np

# Proportions d'une carte Magic (mm) ~ 63 x 88
CARD_W_MM = 63.0
CARD_H_MM = 88.0
CARD_RATIO = CARD_W_MM / CARD_H_MM  # ~0.7159
RTSP_URL = "http://10.170.225.2:8080/video/mjpeg"

# Taille de sortie en pixels (gardez le ratio 63:88)
OUT_W = 500
OUT_H = int(round(OUT_W * (CARD_H_MM / CARD_W_MM)))  # ~1006



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
