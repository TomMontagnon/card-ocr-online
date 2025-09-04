from PySide6 import QtWidgets, QtGui, QtCore

class VideoView(QtWidgets.QLabel):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setScaledContents(True)
        self.setMinimumSize(32, 24)

    @QtCore.Slot(QtGui.QImage)
    def set_frame(self, qimg: QtGui.QImage) -> None:
        self.setPixmap(QtGui.QPixmap.fromImage(qimg))
