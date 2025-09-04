from enum import Enum
from typing import Any
from apps.gui_qt.widgets.toggle_button_widget import ToggleButton
from PySide6 import QtWidgets, QtCore


# Exemple d'énumération Python
class Mode(Enum):
    RAPIDE = 1
    PRECIS = 2
    PERSONNALISE = 3


class SettingsWidget(QtWidgets.QWidget):
    # Signal émis quand une valeur change
    changed = QtCore.Signal()

    def __init__(self, enum_type: type[Enum] = Mode, parent=None):
        super().__init__(parent)
        self.enum_type = enum_type

        # Widgets
        self.label_auto = QtWidgets.QLabel("Auto-detect")
        self.toggle = ToggleButton(checked=False)

        self.label_enum = QtWidgets.QLabel("Expansion")
        self.combo_enum = QtWidgets.QComboBox()

        self.label_int = QtWidgets.QLabel("Id Card")
        self.spin_int = QtWidgets.QSpinBox()
        self.spin_int.setRange(-10_000_000, 10_000_000)
        self.spin_int.setValue(10)

        # Remplir le combo avec l'Enum
        self._populate_enum(self.enum_type)

        # Layout
        grid = QtWidgets.QGridLayout(self)
        grid.setColumnStretch(1, 1)

        # Ligne Auto-detect
        grid.addWidget(self.label_auto, 0, 0)
        grid.addWidget(self.toggle, 0, 1)

        # Ligne Enum
        grid.addWidget(self.label_enum, 1, 0)
        grid.addWidget(self.combo_enum, 1, 1)

        # Ligne Int
        grid.addWidget(self.label_int, 2, 0)
        grid.addWidget(self.spin_int, 2, 1)

        # Connexions
        self.toggle.toggledChanged.connect(self._on_auto_changed)
        self.combo_enum.currentIndexChanged.connect(lambda *_: self.changed.emit())
        self.spin_int.valueChanged.connect(lambda *_: self.changed.emit())

        # État initial
        self._apply_auto_state(self.toggle.isChecked())

    def _populate_enum(self, enum_type: type[Enum]) -> None:
        self.combo_enum.clear()
        for member in enum_type:
            # Texte lisible, valeur stockée en UserRole
            self.combo_enum.addItem(member.name.title(), member)

    def _on_auto_changed(self, *, state: bool) -> None:
        self._apply_auto_state(state)
        self.changed.emit()

    def _apply_auto_state(self, *, auto: bool) -> None:
        # Désactiver les champs quand Auto-detect est actif
        self.combo_enum.setEnabled(not auto)
        self.spin_int.setEnabled(not auto)

    # API pratique
    def is_auto(self) -> bool:
        return self.toggle.isChecked()

    def selected_enum(self) -> Enum | None:
        idx = self.combo_enum.currentIndex()
        if idx < 0:
            return None
        return self.combo_enum.itemData(idx)

    def integer_value(self) -> int:
        return self.spin_int.value()

    def value(self) -> dict[str, Any]:
        return {
            "auto_detect": self.is_auto(),
            "mode": self.selected_enum(),
            "seuil": self.integer_value(),
        }

    def set_value(self, auto_detect: bool, mode: Enum | None, seuil: int):
        self.toggle.setChecked(auto_detect)
        if mode is not None:
            # rechercher l'index porteur de ce member
            for i in range(self.combo_enum.count()):
                if self.combo_enum.itemData(i) == mode:
                    self.combo_enum.setCurrentIndex(i)
                    break
        self.spin_int.setValue(seuil)
