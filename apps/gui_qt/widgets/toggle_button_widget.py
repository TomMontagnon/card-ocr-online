from PySide6 import QtWidgets, QtCore


class ToggleButton(QtWidgets.QPushButton):
    toggled_changed = QtCore.Signal(bool)

    def __init__(self, parent: QtWidgets.QWidget = None, checked: bool = False) -> None:
        super().__init__(parent)
        self.setCheckable(True)
        self.setChecked(checked)
        self._update_text()
        self.toggled.connect(self._on_toggled)

        # (Optionnel) style "switch"
        self.setStyleSheet("""
            QPushButton {
                border: 1px solid #bbb; border-radius: 12px; padding: 2px 10px;
                background: #eee; color: #333; min-width: 48px;
            }
            QPushButton:checked {
                background: #4caf50; color: white;
            }
        """)

    def _on_toggled(self, state: bool) -> None:
        self._update_text()
        self.toggled_changed.emit(state)

    def _update_text(self) -> None:
        self.setText("On" if self.isChecked() else "Off")
