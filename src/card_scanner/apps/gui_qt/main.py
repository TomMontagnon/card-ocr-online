import sys
from PySide6 import QtWidgets, QtGui
from card_scanner.core.api import Expansion
from card_scanner.apps.gui_qt.widgets import (
    HistoryWidget,
    SourceSelectorWidget,
    ExportWidget,
    VariantSelectorWidget,
    SettingsWidget,
    VideoView,
)
from card_scanner.apps.gui_qt.controller import AppController
from card_scanner.core.pipeline import (
    Pipeline,
    OcrExtractTextStage,
    OcrPreprocessStage,
    OcrProcessStage,
    OcrMeanYield,
    CardWarpStage,
    CardCropStage,
    CardDetectorStage,
    EdgeExtractionStage,
)
from card_scanner.apps.gui_qt.qt_ui_sink import QtUISink


def main() -> None:
    app = QtWidgets.QApplication(sys.argv)

    screen_geometry = app.primaryScreen().availableGeometry()
    screen_width = screen_geometry.width()
    _screen_height = screen_geometry.height()

    default_width = int(screen_width * 0.9)
    side_panel_width = int(default_width // 5)

    default_height = int((default_width - side_panel_width) * 9 / 16)
    side_panel_height = int(default_height)

    win = QtWidgets.QMainWindow()
    win.setWindowTitle("Starwars Unlimited cards detector 1.0")

    # ====================
    # Main Widgets
    # ====================
    main_cam_view = VideoView()
    card_id_zoom_view = VideoView()
    card_artwork_widget = VariantSelectorWidget()
    card_artwork_view = card_artwork_widget.view
    settings_widget = SettingsWidget(Expansion)
    history_widget = HistoryWidget()

    # ====================
    # Toolbar
    # ====================
    toolbar = QtWidgets.QToolBar("Controls")
    btn_start = QtGui.QAction("Start", win)
    btn_stop = QtGui.QAction("Stop", win)
    toolbar.addAction(btn_start)
    toolbar.addAction(btn_stop)
    win.addToolBar(toolbar)

    selector_widget = SourceSelectorWidget()
    toolbar.addWidget(selector_widget)

    export_widget = ExportWidget()
    toolbar.addWidget(export_widget)

    # ====================
    # Side panel
    # ====================
    side_box_layout = QtWidgets.QVBoxLayout()
    side_box_layout.addWidget(card_id_zoom_view, 1)
    side_box_layout.addWidget(settings_widget, 1)
    side_box_layout.addWidget(card_artwork_widget, 3)
    side_box_layout.addWidget(history_widget, 1)

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

    pipelines = {
        "pipeline_main": Pipeline([EdgeExtractionStage(), CardDetectorStage()]),
        "pipeline_side": Pipeline([CardWarpStage(), CardCropStage()]),
        "pipeline_ocr": Pipeline(
            [
                OcrPreprocessStage(),
                OcrProcessStage(),
                OcrExtractTextStage(),
                OcrMeanYield(),
            ]
        ),
    }
    sinks = {
        "sink_main": QtUISink(),
        "sink_side": QtUISink(),
        "sink_artwork": QtUISink(),
    }
    ctrl = AppController(pipelines, sinks)

    # WIRING
    sinks["sink_main"].connect(main_cam_view.set_frame)
    sinks["sink_side"].connect(card_id_zoom_view.set_frame)
    sinks["sink_artwork"].connect(card_artwork_view.set_frame)
    ctrl.worker.card_detected.connect(settings_widget.set_value_auto)
    ctrl.worker2.arts_ready.connect(card_artwork_widget.set_variants)
    card_artwork_widget.pre_selected.connect(sinks["sink_artwork"].push)
    settings_widget.settings_changed.connect(ctrl.worker2.get_arts)
    card_artwork_widget.locked.connect(history_widget.set_current_card)
    btn_start.triggered.connect(ctrl.start)
    btn_stop.triggered.connect(ctrl.stop)
    app.aboutToQuit.connect(ctrl.quit)
    selector_widget.source_selected.connect(ctrl.set_source)
    export_widget.export_requested.connect(history_widget.export_csv)

    sys.exit(app.exec())
    # app.exec()

if __name__ == "__main__":
    main()
