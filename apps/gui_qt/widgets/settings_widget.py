from enum import Enum
from apps.gui_qt.widgets.toggle_button_widget import ToggleButton
from PySide6 import QtWidgets, QtCore


class SettingsWidget(QtWidgets.QWidget):
    changed = QtCore.Signal()

    def __init__(self, enum_type: type[Enum], parent: QtWidgets.QWidget = None) -> None:
        super().__init__(parent)
        self.enum_type = enum_type

        # Widgets
        self.label_auto = QtWidgets.QLabel("Auto-detect")
        self.toggle_auto = ToggleButton(checked=False)

        self.label_enum = QtWidgets.QLabel("Expansion")
        self.combo_enum = QtWidgets.QComboBox()
        self._populate_enum()

        self.label_int = QtWidgets.QLabel("Id Card")
        self.spin_int = QtWidgets.QSpinBox()
        self.spin_int.setRange(0, 1_000)
        self.spin_int.setValue(1)


        # Layout
        grid = QtWidgets.QGridLayout(self)
        grid.setColumnStretch(1, 1)

        grid.addWidget(self.label_auto, 0, 0)
        grid.addWidget(self.toggle_auto, 0, 1)

        grid.addWidget(self.label_enum, 1, 0)
        grid.addWidget(self.combo_enum, 1, 1)

        grid.addWidget(self.label_int, 2, 0)
        grid.addWidget(self.spin_int, 2, 1)

        # Connexions
        self.toggle_auto.toggledChanged.connect(self._on_auto_changed)
        self.combo_enum.currentIndexChanged.connect(lambda *_: self.changed.emit())
        self.spin_int.valueChanged.connect(lambda *_: self.changed.emit())

        # Initial state
        self._apply_auto_state(self.toggle_auto.isChecked())


    # Slots / internals --------------------------------------------------------

    def _populate_enum(self) -> None:
        self.combo_enum.clear()
        for member in self.enum_type:
            # Texte lisible, valeur stockée en UserRole
            self.combo_enum.addItem(member.name.title(), member)

    @QtCore.Slot(bool)
    def _on_auto_changed(self, state: bool) -> None:
        self._apply_auto_state(state)
        self.changed.emit()

    def _apply_auto_state(self, auto: bool) -> None:
        # Désactiver les champs quand Auto-detect est actif
        self.combo_enum.setEnabled(not auto)
        self.spin_int.setEnabled(not auto)

    # Public API ---------------------------------------------------------------

    # def is_auto(self) -> bool:
    #     return self.toggle.isChecked()

    # def selected_enum(self) -> Enum | None:
    #     idx = self.combo_enum.currentIndex()
    #     if idx < 0:
    #         return None
    #     return self.combo_enum.itemData(idx)

    # def integer_value(self) -> int:
    #     return self.spin_int.value()

    # def value(self) -> dict[str, Any]:
    #     return {
    #         "auto_detect": self.is_auto(),
    #         "mode": self.selected_enum(),
    #         "seuil": self.integer_value(),
    #     }

    # def set_value(self, mode: Enum | None, seuil: int, *, auto_detect: bool) -> None:
    #     self.toggle.setChecked(auto_detect)
    #     if mode is not None:
    #         # rechercher l'index porteur de ce member
    #         for i in range(self.combo_enum.count()):
    #             if self.combo_enum.itemData(i) == mode:
    #                 self.combo_enum.setCurrentIndex(i)
    #                 break
    #     self.spin_int.setValue(seuil)
