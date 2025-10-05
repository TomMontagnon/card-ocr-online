import cv2
from PySide6 import QtWidgets, QtCore
from core.api.interfaces import IFrameSource
from core.io.sources import RtspSource, CameraSource, VideoFileSource

class SourceSelector(QtWidgets.QWidget):
    source_selected = QtCore.Signal(IFrameSource)  # Émet la source choisie

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Choisir la source")
        layout = QtWidgets.QVBoxLayout(self)

        # Camera
        cam_btn = QtWidgets.QPushButton("Camera")
        cam_btn.clicked.connect(self._choose_camera)
        layout.addWidget(cam_btn)

        # RTSP
        rtsp_btn = QtWidgets.QPushButton("RTSP")
        rtsp_btn.clicked.connect(self._choose_rtsp)
        layout.addWidget(rtsp_btn)

        # Video File
        video_btn = QtWidgets.QPushButton("Fichier vidéo")
        video_btn.clicked.connect(self._choose_video)
        layout.addWidget(video_btn)

    def _choose_camera(self):
        cameras = self._list_cameras()
        if not cameras:
            QtWidgets.QMessageBox.warning(
                self, "Aucune caméra", "Aucune caméra détectée"
            )
            return

        cam, ok = QtWidgets.QInputDialog.getItem(
            self, "Choisir une caméra", "Caméras disponibles:", cameras, 0, False
        )
        if ok:
            index = int(cam.split()[0])  # "0 - Logitech"
            source = CameraSource(index)
            self.source_selected.emit(source)
            print(("camera", index))
            self.close()

    def _choose_rtsp(self):
        text, ok = QtWidgets.QInputDialog.getText(self, "RTSP", "Adresse RTSP:")
        if ok and text:
            source = RtspSource(text)
            self.source_selected.emit(source)
            print(("rtsp", text))
            self.close()

    def _choose_video(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Ouvrir une vidéo", "", "Video Files (*.mp4 *.avi *.mkv)"
        )
        if path:
            source = VideoFileSource(path)
            self.source_selected.emit(source)
            print(("video", path))
            self.close()

    def _list_cameras(self):
        """Teste les indices de caméra et renvoie la liste disponible"""
        available = []
        for i in range(5):  # teste les 5 premières caméras
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available.append(f"{i} - Camera {i}")
                cap.release()
        return available
