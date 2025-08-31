from __future__ import annotations
import sys
from PySide6 import QtWidgets
from core.io.sources import CameraSource
from core.pipeline.base import Pipeline
from core.pipeline.stages.canny import CannyStage
from .widgets.video_view import VideoView
from .controller import AppController

def main():
    app = QtWidgets.QApplication(sys.argv)

    # UI
    win = QtWidgets.QMainWindow()
    view = VideoView()
    toolbar = QtWidgets.QToolBar("Controls")
    btn_start = QtWidgets.QAction("Start", win)
    btn_stop  = QtWidgets.QAction("Stop", win)
    toolbar.addAction(btn_start); toolbar.addAction(btn_stop)
    win.addToolBar(toolbar)
    win.setCentralWidget(view)
    win.resize(960, 720)
    win.setWindowTitle("OpenCV + PySide (core découplé)")
    win.show()

    # Wiring
    source = CameraSource(0)
    pipeline = Pipeline([CannyStage()])
    ctrl = AppController(source, pipeline)
    ctrl.sink.frame_ready.connect(view.set_frame)

    btn_start.triggered.connect(ctrl.start)
    btn_stop.triggered.connect(ctrl.stop)
    app.aboutToQuit.connect(ctrl.stop)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
