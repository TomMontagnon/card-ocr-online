import cv2
from PySide6 import QtWidgets, QtCore
from core.api.interfaces import IFrameSource
from core.io.sources import RtspSource, CameraSource, VideoFileSource


class SourceSelector(QtWidgets.QWidget):
    source_selected = QtCore.Signal(IFrameSource)  # Émet la source choisie

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Source")
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

    def _choose_camera(self) -> None:
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
            index = int(cam.split()[0])
            source = CameraSource(index)
            self.source_selected.emit(source)
            print(("camera", index))
            self.close()

    def _choose_rtsp(self) -> None:
        # Crée une boîte de dialogue personnalisée plus flexible
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Entrer l'adresse RTSP / MJPEG")

        layout = QtWidgets.QVBoxLayout(dialog)

        label = QtWidgets.QLabel("Adresse RTSP / MJPEG :")
        layout.addWidget(label)

        # Champ de saisie avec valeur par défaut et largeur augmentée
        line_edit = QtWidgets.QLineEdit(dialog)
        line_edit.setText("http://:8080/video/mjpeg")
        line_edit.setMinimumWidth(300)
        layout.addWidget(line_edit)

        # Boutons OK / Annuler
        btns = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        layout.addWidget(btns)

        btns.accepted.connect(dialog.accept)
        btns.rejected.connect(dialog.reject)

        # Exécute le dialogue
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            text = line_edit.text().strip()
            if text:
                source = RtspSource(text)
                self.source_selected.emit(source)
                print(("rtsp", text))
                self.close()

    def _choose_video(self) -> None:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Ouvrir une vidéo", "", "Video Files (*.mp4 *.avi *.mkv)"
        )
        if path:
            source = VideoFileSource(path)
            self.source_selected.emit(source)
            print(("video", path))
            self.close()

    def _list_cameras(self) -> list:
        """Teste les indices de caméra et renvoie la liste disponible"""
        available = []
        for i in range(5):  # teste les 5 premières caméras
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available.append(f"{i} - Camera {i}")
                cap.release()
        return available
