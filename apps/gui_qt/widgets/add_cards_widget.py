from __future__ import annotations
from datetime import datetime, UTC
from apps.gui_qt.widgets.toggle_button_widget import ToggleButton

from PySide6 import QtCore, QtWidgets


class AddHistoryWidget(QtWidgets.QWidget):
    # Signals
    autoChanged = QtCore.Signal(bool)
    itemAdded = QtCore.Signal(str)

    def __init__(
        self,
        parent: QtWidgets.QWidget | None = None,
        max_items: int | None = None,
    ) -> None:
        super().__init__(parent)
        self.max_items = max_items  # None = unlimited

        # Widgets
        self.label_auto = QtWidgets.QLabel("Auto-add")
        self.toggle_auto = ToggleButton(checked=False)
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
        top.addWidget(self.toggle_auto)
        top.addStretch(1)
        top.addWidget(self.btn_add)

        lay = QtWidgets.QVBoxLayout(self)
        lay.addLayout(top)
        lay.addWidget(self.list_history, 1)

        # Connexions
        self.toggle_auto.toggledChanged.connect(self._on_auto_toggled)
        self.btn_add.clicked.connect(self._on_add_clicked)

        # Optional: small auto-add simulator (demo only)
        self._demo_timer = QtCore.QTimer(self)
        self._demo_timer.setInterval(1000)
        self._demo_timer.timeout.connect(self._auto_add_tick)

        # Initial state
        self._apply_auto_state(self.toggle_auto.isChecked())

    # Slots / internals --------------------------------------------------------

    def _apply_auto_state(self, auto: bool) -> None:
        # When auto-add is ON, disable manual "Add"
        self.btn_add.setEnabled(not auto)
        # Start/stop demo timer if requested
        self._demo_timer.setRunning(auto) if hasattr(
            self._demo_timer, "setRunning"
        ) else (self._demo_timer.start() if auto else self._demo_timer.stop())

    @QtCore.Slot(bool)
    def _on_auto_toggled(self, state: bool) -> None:
        self._apply_auto_state(state)
        self.autoChanged.emit(state)

    @QtCore.Slot()
    def _on_add_clicked(self) -> None:
        # Default behavior: add a timestamped line.
        # Replace this with your real "add" action as needed.
        self.add_entry(f"Manual add @ {datetime.now(tz=UTC).strftime('%H:%M:%S')}")

    @QtCore.Slot()
    def _auto_add_tick(self) -> None:
        if self.is_auto():
            self.add_entry(f"Auto add @ {datetime.now(tz=UTC).strftime('%H:%M:%S')}")

    # Public API ---------------------------------------------------------------
    
    def is_auto(self) -> bool:
        return self.toggle_auto.isChecked()

    def set_auto(self, *, enabled: bool) -> None:
        self.toggle_auto.setChecked(enabled)

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
        # Ensure it's visible at top
        self.list_history.scrollToItem(item, QtWidgets.QAbstractItemView.PositionAtTop)
        self.itemAdded.emit(text)

    def history(self) -> list[str]:
        return [
            self.list_history.item(i).text() for i in range(self.list_history.count())
        ]
