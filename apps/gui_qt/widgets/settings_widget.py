from enum import Enum
from apps.gui_qt.widgets.toggle_button_widget import ToggleButton
from PySide6 import QtWidgets, QtCore


class SettingsWidget(QtWidgets.QWidget):
    settings_changed = QtCore.Signal(dict)

    def __init__(self, enum_type: type[Enum], parent: QtWidgets.QWidget = None) -> None:
        super().__init__(parent)
        self._enum_type = enum_type

        # Widgets
        self._label_auto = QtWidgets.QLabel("Auto-detect")
        self._toggle_auto = ToggleButton(checked=False)

        self._label_enum = QtWidgets.QLabel("Expansion")
        self._combo_enum = QtWidgets.QComboBox()
        self._populate_enum()

        self._label_int = QtWidgets.QLabel("Id Card")
        self._spin_int = QtWidgets.QSpinBox()
        self._spin_int.setRange(0, 1_000)
        self._spin_int.setValue(1)

        # Layout
        grid = QtWidgets.QGridLayout(self)
        grid.setColumnStretch(1, 1)

        grid.addWidget(self._label_auto, 0, 0)
        grid.addWidget(self._toggle_auto, 0, 1)

        grid.addWidget(self._label_enum, 1, 0)
        grid.addWidget(self._combo_enum, 1, 1)

        grid.addWidget(self._label_int, 2, 0)
        grid.addWidget(self._spin_int, 2, 1)

        # Connexions
        self._toggle_auto.toggled_changed.connect(self._on_auto_changed)
        self._combo_enum.currentIndexChanged.connect(
            lambda *_: self.settings_changed.emit(self.value())
        )
        self._spin_int.valueChanged.connect(
            lambda *_: self.settings_changed.emit(self.value())
        )

        # Initial state
        self._apply_auto_state(self._toggle_auto.isChecked())

    # Slots / internals --------------------------------------------------------

    def _populate_enum(self) -> None:
        self._combo_enum.clear()
        for member in self._enum_type:
            # Texte lisible, valeur stockée en UserRole
            self._combo_enum.addItem(member.name, member)

    @QtCore.Slot(bool)
    def _on_auto_changed(self, state: bool) -> None:
        self._apply_auto_state(state)
        self.settings_changed.emit(self.value())

    def _apply_auto_state(self, auto: bool) -> None:
        # Désactiver les champs quand Auto-detect est actif
        self._combo_enum.setEnabled(not auto)
        self._spin_int.setEnabled(not auto)

    # Public API ---------------------------------------------------------------

    def is_auto(self) -> bool:
        return self._toggle_auto.isChecked()

    def selected_enum(self) -> Enum | None:
        idx = self._combo_enum.currentIndex()
        if idx < 0:
            return None
        return self._combo_enum.itemData(idx)

    def integer_value(self) -> int:
        return self._spin_int.value()

    def value(self) -> dict[str, str]:
        return {
            "auto_detect": self.is_auto(),
            "exp": self.selected_enum(),
            "card_id": str(self.integer_value()),
        }

    def set_value_auto(self, expansion: Enum, id_card: int) -> None:
        if self.is_auto():
            for i in range(self._combo_enum.count()):
                if self._combo_enum.itemData(i) == expansion:
                    self._combo_enum.setCurrentIndex(i)
                    break
            self._spin_int.setValue(id_card)
