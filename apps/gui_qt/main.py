import sys
from PySide6 import QtWidgets, QtGui, QtCore
from apps.gui_qt.widgets.video_view import VideoView
from apps.gui_qt.widgets.settings_widget import SettingsWidget
from core.api.types import Expansion
from apps.gui_qt.widgets.add_cards_widget import AddHistoryWidget

from apps.gui_qt.controller import AppController
from core.io.sources import RtspSource, CameraSource, VideoFileSource
from core.pipeline.base import Pipeline
from core.pipeline.stages.card_detector import CardDetectorStage, EdgeExtractionStage
from core.pipeline.stages.card_format import CardWarpStage, CardCropStage
from core.pipeline.stages.optic_char_recog import (
    OcrExtractTextStage,
    OcrPreprocessStage,
    OcrPrintResultsStage,
    OcrProcessStage,
)
from apps.gui_qt.qt_ui_sink import QtUISink


def main() -> None:
    app = QtWidgets.QApplication(sys.argv)

    screen_geometry = app.primaryScreen().availableGeometry()
    screen_width = screen_geometry.width()
    screen_height = screen_geometry.height()

    default_width = int(screen_width * 0.9)
    side_panel_width = int(default_width // 5)

    default_height = int(((default_width-side_panel_width) * 9 / 16))
    side_panel_height = int(default_height)

    win = QtWidgets.QMainWindow()
    win.setWindowTitle("OpenCV + PySide (core découplé)")

    # ====================
    # Main Widgets
    # ====================
    main_cam_view = VideoView()
    card_id_zoom_view = VideoView()
    card_artwork_view = VideoView()
    settings_widget = SettingsWidget(Expansion)
    add_card_widget = AddHistoryWidget()

    # ====================
    # Toolbar
    # ====================
    toolbar = QtWidgets.QToolBar("Controls")
    btn_start = QtGui.QAction("Start", win)
    btn_stop = QtGui.QAction("Stop", win)
    toolbar.addAction(btn_start)
    toolbar.addAction(btn_stop)
    win.addToolBar(toolbar)

    # ====================
    # Side panel
    # ====================
    side_box_layout = QtWidgets.QVBoxLayout()
    side_box_layout.addWidget(card_id_zoom_view, 1)
    side_box_layout.addWidget(settings_widget, 1)
    side_box_layout.addWidget(card_artwork_view, 3)
    side_box_layout.addWidget(add_card_widget, 1)

    side_box_widget = QtWidgets.QWidget()
    side_box_widget.setLayout(side_box_layout)
    side_box_widget.setFixedWidth(side_panel_width)
    side_box_widget.setMinimumHeight(side_panel_height)

    # ====================
    # Layout central
    # ====================
    central_panel = QtWidgets.QWidget()
    main_layout = QtWidgets.QHBoxLayout(central_panel)
    main_layout.addWidget(main_cam_view)
    main_layout.addWidget(side_box_widget)

    win.setCentralWidget(central_panel)

    # ====================
    # Taille par défaut
    # ====================
    win.resize(default_width, default_height)

    win.show()

    # APP CONTROLLER
    # source = CameraSource(0)
    source = VideoFileSource("videos/video1.mp4")
    # source = RtspSource("http://10.170.225.45:8080/video/mjpeg")

    pipelines = {
        "pipeline_main": Pipeline([EdgeExtractionStage(), CardDetectorStage()]),
        "pipeline_side": Pipeline([CardWarpStage(), CardCropStage()]),
        "pipeline_ocr": Pipeline(
            [
                # OcrPreprocessStage(),
                # OcrProcessStage(),
                # OcrExtractTextStage(),
                # OcrPrintResultsStage(),
            ]
        ),
    }
    sinks = {
        "sink_main": QtUISink(),
        "sink_side": QtUISink(),
        "sink_artwork": QtUISink(),
    }
    ctrl = AppController(source, pipelines, sinks)

    # WIRING
    sinks["sink_main"].connect(main_cam_view.set_frame)
    sinks["sink_side"].connect(card_id_zoom_view.set_frame)
    sinks["sink_artwork"].connect(card_artwork_view.set_frame)
    ctrl.worker.card_detected.connect(settings_widget.set_value)
    settings_widget.settings_changed.connect(ctrl.worker2.emit_card_from_name)
    btn_start.triggered.connect(ctrl.start)
    btn_stop.triggered.connect(ctrl.stop)
    app.aboutToQuit.connect(ctrl.stop)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
