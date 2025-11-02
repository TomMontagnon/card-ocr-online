from __future__ import annotations
from PySide6 import QtWidgets, QtCore, QtGui
from .video_view import VideoView
from card_scanner.core.api import Frame, Meta
from importlib import resources


class ClickableArea(QtWidgets.QWidget):
    clicked = QtCore.Signal()

    def __init__(self, parent=None, color=None, icon_path=None, icon_size=32) -> None:
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, False)
        if color:
            self.setStyleSheet(f"background-color: {color};")
        else:
            self.setStyleSheet("background-color: transparent;")

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(QtCore.Qt.AlignCenter)

        # Si un pictogramme est fourni
        if not icon_path:
            print(f"Impossible de charger le pictogramme : {icon_path}")
            return

        icon_label = QtWidgets.QLabel()
        icon_label.setStyleSheet("background: transparent;")
        pixmap = QtGui.QPixmap(icon_path)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(
                QtCore.QSize(icon_size, icon_size),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation,
            )
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(icon_label)

    def mousePressEvent(self, event) -> None:
        self.clicked.emit()


class VariantSelectorWidget(QtWidgets.QWidget):
    locked = QtCore.Signal(dict)
    pre_selected = QtCore.Signal(Frame, Meta)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.view = VideoView()
        self.label = QtWidgets.QLabel("No variant", alignment=QtCore.Qt.AlignCenter)
        self.label.setStyleSheet("color: black; font-weight: bold;")

        # Container pour superposition
        self.stack_container = QtWidgets.QWidget()
        self.stack_layout = QtWidgets.QStackedLayout(self.stack_container)
        self.stack_layout.addWidget(self.view)

        # Zones cliquables
        with resources.path(
            "card_scanner.apps.gui_qt.assets.pictos", "left_arrow.png"
        ) as p:
            self.left_area = ClickableArea(
                self.stack_container, "rgba(255,0,0,0.3)", str(p)
            )
        with resources.path(
            "card_scanner.apps.gui_qt.assets.pictos", "right_arrow.png"
        ) as p:
            self.right_area = ClickableArea(
                self.stack_container, "rgba(0,255,0,0.3)", str(p)
            )
        with resources.path("card_scanner.apps.gui_qt.assets.pictos", "lock.png") as p:
            self.lock_area = ClickableArea(
                self.stack_container, "rgba(0,0,255,0.3)", str(p)
            )

        for area in [self.left_area, self.right_area, self.lock_area]:
            area.setGeometry(0, 0, 0, 0)  # sera mis à jour dans resizeEvent
            area.show()

        self.left_area.clicked.connect(self.prev_variant)
        self.right_area.clicked.connect(self.next_variant)
        self.lock_area.clicked.connect(self.lock)

        # Layout principal
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.label)
        main_layout.addWidget(self.stack_container)

        # Variantes
        self.dico = None
        self.variants = []
        self.current_index = 0
        self.is_locked = False

    def resizeEvent(self, event) -> None:
        """Place les zones cliquables aux bons endroits"""
        w, h = self.stack_container.width(), self.stack_container.height()
        area_width = w * 0.15
        area_height = h * 0.25

        self.left_area.setGeometry(
            0, (h / 2) - (area_height / 2), area_width, area_height
        )
        self.right_area.setGeometry(
            w - area_width, (h / 2) - (area_height / 2), area_width, area_height
        )
        self.lock_area.setGeometry(
            (w / 2) - (area_height / 2), h - area_width, area_height, area_width
        )

        super().resizeEvent(event)

    # --- logique d'affichage ---
    def set_variants(self, dico: dict, variants: list) -> None:
        """variants: list of (variant_name, np_frame)"""
        self.variants = variants
        self.dico = dico
        self.current_index = 0
        if len(self.variants) == 1:
            self.lock()
        else:
            self.unlock()
        self.update_view()

    def update_view(self) -> None:
        if not self.variants:
            self.label.setText("No variants available")
            # self.view.clear()
            return
        variant_name, frame = self.variants[self.current_index]
        self.label.setText(variant_name)
        self.pre_selected.emit(frame, Meta(0))

    def prev_variant(self) -> None:
        if self.is_locked or not self.variants:
            return
        self.current_index = (self.current_index - 1) % len(self.variants)
        self.update_view()

    def next_variant(self) -> None:
        if self.is_locked or not self.variants:
            return
        self.current_index = (self.current_index + 1) % len(self.variants)
        self.update_view()

    def unlock(self) -> None:
        self.is_locked = False
        self.left_area.show()
        self.right_area.show()
        self.lock_area.show()

    def lock(self) -> None:
        if not self.variants:
            return
        self.is_locked = True
        self.left_area.hide()
        self.right_area.hide()
        self.lock_area.hide()

        name, _ = self.variants[self.current_index]
        self.dico["variant"] = name
        self.locked.emit(self.dico)
