from PySide6 import QtWidgets, QtGui, QtCore

class VideoView(QtWidgets.QLabel):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.setScaledContents(False)
        self._orig_pixmap = None

        # ⚙️ Permet le redimensionnement libre (up ET down)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Ignored,
            QtWidgets.QSizePolicy.Policy.Ignored
        )

    @QtCore.Slot(QtGui.QImage)
    def set_frame(self, qimg: QtGui.QImage) -> None:
        self._orig_pixmap = QtGui.QPixmap.fromImage(qimg)
        self._update_display()

    def resizeEvent(self, event):
        self._update_display()
        super().resizeEvent(event)

    def _update_display(self):
        if not self._orig_pixmap:
            self.clear()
            return

        scaled = self._orig_pixmap.scaled(
            self.size(),
            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(scaled)
