from __future__ import annotations
import sys
from PySide6 import QtWidgets, QtGui
from core.io.sources import CameraSource
from core.pipeline.base import Pipeline
from core.pipeline.stages.canny import CannyStage
from .widgets.video_view import VideoView
from .widgets.settings_widget import SettingsWidget
from .widgets.add_cards_widget import AddHistoryWidget
from .controller import AppController
from enum import Enum


# Exemple d'énumération Python
class Mode(Enum):
    RAPIDE = 1
    PRECIS = 2
    PERSONNALISE = 3

def main() -> None:
    app = QtWidgets.QApplication(sys.argv)

    # UI
    win = QtWidgets.QMainWindow()
    main_cam_view = VideoView()
    card_id_zoom_view = VideoView()
    card_artwork_view = VideoView()
    toolbar = QtWidgets.QToolBar("Controls")
    setting_widget = SettingsWidget(Mode)
    add_card_widget = AddHistoryWidget()
    btn_start = QtGui.QAction("Start", win)
    btn_stop  = QtGui.QAction("Stop", win)
    toolbar.addAction(btn_start)
    toolbar.addAction(btn_stop)
    win.addToolBar(toolbar)


    side_box = QtWidgets.QVBoxLayout()
    side_box.addWidget(card_id_zoom_view,1)
    side_box.addWidget(setting_widget,1)
    side_box.addWidget(card_artwork_view,3)
    side_box.addWidget(add_card_widget,1)
    # side_box.addWidget(QtWidgets.QLabel(),3)

    # Splitter horizontal: gauche 3/4, droite 1/4
    central_panel = QtWidgets.QWidget()
    main_box = QtWidgets.QHBoxLayout(central_panel)
    main_box.addWidget(main_cam_view,3)
    main_box.addLayout(side_box,1)

    win.setCentralWidget(central_panel)
    win.resize(1080, 720)
    win.setWindowTitle("OpenCV + PySide (core découplé)")
    win.show()

    # Wiring
    source = CameraSource(0)
    pipeline = Pipeline([CannyStage()])
    ctrl = AppController(source, pipeline)
    ctrl.main_cam_sink.connect(main_cam_view.set_frame)
    ctrl.card_id_zoom_sink.connect(card_id_zoom_view.set_frame)
    ctrl.card_artwork_sink.connect(card_artwork_view.set_frame)

    btn_start.triggered.connect(ctrl.start)
    btn_stop.triggered.connect(ctrl.stop)
    app.aboutToQuit.connect(ctrl.stop)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
