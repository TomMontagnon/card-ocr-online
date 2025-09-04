from __future__ import annotations
import sys
from PySide6 import QtWidgets, QtGui, QtCore
from core.io.sources import CameraSource
from core.pipeline.base import Pipeline
from core.pipeline.stages.canny import CannyStage
from .widgets.video_view import VideoView
from .controller import AppController

def main() -> None:
    app = QtWidgets.QApplication(sys.argv)

    # UI
    win = QtWidgets.QMainWindow()
    left_view = VideoView()
    right_view = VideoView()
    right_view1 = VideoView()
    right_view2 = VideoView()
    toolbar = QtWidgets.QToolBar("Controls")
    btn_start = QtGui.QAction("Start", win)
    btn_stop  = QtGui.QAction("Stop", win)
    toolbar.addAction(btn_start); toolbar.addAction(btn_stop)
    win.addToolBar(toolbar)


    right_top_panel = QtWidgets.QWidget()
    right_top_vbox  = QtWidgets.QVBoxLayout(right_top_panel)
    right_top_vbox.setContentsMargins(0, 0, 0, 0)
    right_top_vbox.setSpacing(6)
    right_top_vbox.addWidget(right_view)


    right_middle_panel = QtWidgets.QWidget()
    right_middle_vbox  = QtWidgets.QVBoxLayout(right_middle_panel)
    right_middle_vbox.setContentsMargins(0, 0, 0, 0)
    right_middle_vbox.setSpacing(6)
    right_middle_vbox.addWidget(right_view1)

    right_bottom_panel = QtWidgets.QWidget()
    right_bottom_vbox  = QtWidgets.QVBoxLayout(right_bottom_panel)
    right_bottom_vbox.setContentsMargins(0, 0, 0, 0)
    right_bottom_vbox.setSpacing(6)
    right_bottom_vbox.addWidget(right_view2)

    right_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
    right_splitter.addWidget(right_top_panel)
    right_splitter.addWidget(right_middle_panel)
    right_splitter.addWidget(right_bottom_panel)
    right_splitter.setChildrenCollapsible(False)
    right_splitter.setHandleWidth(6)
    right_splitter.setStretchFactor(0, 1)
    right_splitter.setStretchFactor(1, 3)
    right_splitter.setStretchFactor(2, 3)

    # Splitter horizontal: gauche 3/4, droite 1/4
    splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
    splitter.addWidget(left_view)
    splitter.addWidget(right_splitter)
    splitter.setChildrenCollapsible(False)
    splitter.setHandleWidth(6)
    # Indice 0 = gauche, 1 = droite
    splitter.setStretchFactor(0, 3)
    splitter.setStretchFactor(1, 1)

    
    win.setCentralWidget(splitter)
    win.resize(960, 720)
    win.setWindowTitle("OpenCV + PySide (core découplé)")
    win.show()

    # Wiring
    source = CameraSource(0)
    pipeline = Pipeline([CannyStage()])
    ctrl = AppController(source, pipeline)
    ctrl.main_sink.connect(left_view.set_frame)
    ctrl.side_sink.connect(right_view.set_frame)
    ctrl.side_sink.connect(right_view1.set_frame)
    ctrl.side_sink.connect(right_view2.set_frame)

    btn_start.triggered.connect(ctrl.start)
    btn_stop.triggered.connect(ctrl.stop)
    app.aboutToQuit.connect(ctrl.stop)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
