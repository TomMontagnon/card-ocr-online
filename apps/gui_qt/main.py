import sys
from PySide6 import QtWidgets, QtGui
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

    # UI
    win = QtWidgets.QMainWindow()
    main_cam_view = VideoView()
    card_id_zoom_view = VideoView()
    card_artwork_view = VideoView()
    toolbar = QtWidgets.QToolBar("Controls")
    settings_widget = SettingsWidget(Expansion)
    add_card_widget = AddHistoryWidget()
    btn_start = QtGui.QAction("Start", win)
    btn_stop = QtGui.QAction("Stop", win)
    toolbar.addAction(btn_start)
    toolbar.addAction(btn_stop)
    win.addToolBar(toolbar)

    side_box = QtWidgets.QVBoxLayout()
    side_box.addWidget(card_id_zoom_view, 1)
    side_box.addWidget(settings_widget, 1)
    side_box.addWidget(card_artwork_view, 3)
    side_box.addWidget(add_card_widget, 1)

    central_panel = QtWidgets.QWidget()
    main_box = QtWidgets.QHBoxLayout(central_panel)
    main_box.addWidget(main_cam_view, 3)
    main_box.addLayout(side_box, 1)

    win.setCentralWidget(central_panel)
    win.resize(1080, 720)
    win.setWindowTitle("OpenCV + PySide (core découplé)")
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
