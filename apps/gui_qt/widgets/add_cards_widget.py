from __future__ import annotations

import sys
from datetime import datetime
from typing import List, Optional
from apps.gui_qt.widgets.toggle_button_widget import ToggleButton

from PySide6 import QtCore, QtWidgets


class AddHistoryWidget(QtWidgets.QWidget):
    # Signals
    autoChanged = QtCore.Signal(bool)
    itemAdded = QtCore.Signal(str)

    def __init__(self, parent=None, max_items: Optional[int] = None, simulate_auto_in_demo=False):
        super().__init__(parent)
        self.max_items = max_items  # None = unlimited
        self.simulate_auto_in_demo = simulate_auto_in_demo

        # Controls
        self.label_auto = QtWidgets.QLabel("Auto-add")
        self.chk_auto = ToggleButton(checked=False)
        self.btn_add = QtWidgets.QPushButton("Add")
        self.btn_add.setDefault(True)

        self.list_history = QtWidgets.QListWidget()
        self.list_history.setAlternatingRowColors(True)
        self.list_history.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.list_history.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.list_history.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.list_history.setWordWrap(True)
        self.list_history.setUniformItemSizes(False)

        # Layout
        top = QtWidgets.QHBoxLayout()
        top.addWidget(self.label_auto)
        top.addWidget(self.chk_auto)
        top.addStretch(1)
        top.addWidget(self.btn_add)

        lay = QtWidgets.QVBoxLayout(self)
        lay.addLayout(top)
        lay.addWidget(self.list_history, 1)

        # Connections
        self.chk_auto.toggled.connect(self._on_auto_toggled)
        self.btn_add.clicked.connect(self._on_add_clicked)

        # Initial state
        self._apply_auto_state(self.chk_auto.isChecked())

        # Optional: small auto-add simulator (demo only)
        self._demo_timer = QtCore.QTimer(self)
        self._demo_timer.setInterval(1000)
        self._demo_timer.timeout.connect(self._auto_add_tick)

    # Public API ---------------------------------------------------------------
    def is_auto(self) -> bool:
        return self.chk_auto.isChecked()

    def set_auto(self, enabled: bool) -> None:
        self.chk_auto.setChecked(enabled)

    def add_entry(self, text: str) -> None:
        """Add an entry to history. Newest goes to the top."""
        if not text:
            return
        item = QtWidgets.QListWidgetItem(text)
        # Insert at top
        self.list_history.insertItem(0, item)
        # Optional cap
        if self.max_items is not None and self.list_history.count() > self.max_items:
            self.list_history.takeItem(self.list_history.count() - 1)
        # Ensure it’s visible at top
        self.list_history.scrollToItem(item, QtWidgets.QAbstractItemView.PositionAtTop)
        self.itemAdded.emit(text)

    def history(self) -> List[str]:
        return [self.list_history.item(i).text() for i in range(self.list_history.count())]

    # Slots / internals --------------------------------------------------------
    def _apply_auto_state(self, auto: bool) -> None:
        # When auto-add is ON, disable manual "Add"
        self.btn_add.setEnabled(not auto)
        # Start/stop demo timer if requested
        if self.simulate_auto_in_demo:
            self._demo_timer.setRunning(auto) if hasattr(self._demo_timer, "setRunning") else (
                self._demo_timer.start() if auto else self._demo_timer.stop()
            )

    @QtCore.Slot(bool)
    def _on_auto_toggled(self, state: bool) -> None:
        self._apply_auto_state(state)
        self.autoChanged.emit(state)

    @QtCore.Slot()
    def _on_add_clicked(self) -> None:
        # Default behavior: add a timestamped line.
        # Replace this with your real "add" action as needed.
        self.add_entry(f"Manual add @ {datetime.now().strftime('%H:%M:%S')}")

    def _auto_add_tick(self) -> None:
        if self.is_auto():
            self.add_entry(f"Auto add @ {datetime.now().strftime('%H:%M:%S')}")


# Demo / standalone run --------------------------------------------------------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = AddHistoryWidget(max_items=200, simulate_auto_in_demo=True)
    w.setWindowTitle("Auto-add / Add / History")
    w.resize(420, 300)
    w.show()
    sys.exit(app.exec())

