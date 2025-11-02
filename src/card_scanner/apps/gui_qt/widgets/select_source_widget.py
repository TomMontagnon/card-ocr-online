from __future__ import annotations
import cv2
from PySide6 import QtWidgets, QtCore
from card_scanner.core.api import IFrameSource
from card_scanner.core.io import RtspSource, CameraSource, VideoFileSource


class SourceSelectorWidget(QtWidgets.QToolButton):
    source_selected = QtCore.Signal(IFrameSource)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setText("Source")
        self.setPopupMode(QtWidgets.QToolButton.InstantPopup)

        menu = QtWidgets.QMenu(self)

        cam_action = menu.addAction("Caméra")
        cam_action.triggered.connect(self._choose_camera)

        rtsp_action = menu.addAction("RTSP / MJPEG")
        rtsp_action.triggered.connect(self._choose_rtsp)

        file_action = menu.addAction("Fichier vidéo")
        file_action.triggered.connect(self._choose_video)

        self.setMenu(menu)

    # ------------------------------------------------------------------
    def _choose_camera(self) -> None:
        cameras = self._list_cameras()
        if not cameras:
            QtWidgets.QMessageBox.warning(
                self, "Aucune caméra", "Aucune caméra détectée"
            )
            return

        # Si une seule caméra
        if len(cameras) == 1:
            index = int(cameras[0].split()[0])
            self.source_selected.emit(CameraSource(index))
            print(("camera", index))
            return

        # Menu contextuel rapide
        menu = QtWidgets.QMenu(self)
        for cam in cameras:
            action = menu.addAction(cam)
            action.triggered.connect(lambda _, c=cam: self._select_camera(c))
        menu.exec(self.mapToGlobal(QtCore.QPoint(0, self.height())))

    def _select_camera(self, cam: str) -> None:
        index = int(cam.split()[0])
        self.source_selected.emit(CameraSource(index))

    # ------------------------------------------------------------------
    def _choose_rtsp(self) -> None:
        text, ok = QtWidgets.QInputDialog.getText(
            self,
            "RTSP / MJPEG",
            "Adresse :",
            QtWidgets.QLineEdit.Normal,
            "http://:8080/video/mjpeg",
        )
        if ok and text.strip():
            self.source_selected.emit(RtspSource(text.strip()))
            print(("rtsp", text.strip()))

    # ------------------------------------------------------------------
    def _choose_video(self) -> None:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Ouvrir une vidéo", "", "Video Files (*.mp4 *.avi *.mkv)"
        )
        if path:
            self.source_selected.emit(VideoFileSource(path))
            print(("video", path))

    # ------------------------------------------------------------------
    def _list_cameras(self) -> None:
        available = []
        for i in range(5):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available.append(f"{i} - Caméra {i}")
                cap.release()
        return available
