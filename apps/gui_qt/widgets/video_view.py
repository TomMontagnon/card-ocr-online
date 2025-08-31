from PySide6 import QtWidgets, QtGui, QtCore

class VideoView(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScaledContents(True)
        self.setMinimumSize(320, 240)

    @QtCore.Slot(QtGui.QImage)
    def set_frame(self, qimg: QtGui.QImage):
        self.setPixmap(QtGui.QPixmap.fromImage(qimg))
