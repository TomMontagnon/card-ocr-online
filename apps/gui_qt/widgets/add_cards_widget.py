from __future__ import annotations
from datetime import datetime, UTC
from apps.gui_qt.widgets.toggle_button_widget import ToggleButton

from PySide6 import QtCore, QtWidgets


class AddHistoryWidget(QtWidgets.QWidget):
    # Signals
    auto_changed = QtCore.Signal(bool)
    item_added = QtCore.Signal(str)

    def __init__(
        self,
        parent: QtWidgets.QWidget | None = None,
        max_items: int | None = None,
    ) -> None:
        super().__init__(parent)
        self._max_items = max_items  # None = unlimited

        # Widgets
        self._label_auto = QtWidgets.QLabel("Auto-add")
        self._toggle_auto = ToggleButton(checked=False)
        self._btn_add = QtWidgets.QPushButton("Add")
        self._btn_add.setDefault(True)

        self._list_history = QtWidgets.QListWidget()
        self._list_history.setAlternatingRowColors(True)
        self._list_history.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self._list_history.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self._list_history.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self._list_history.setWordWrap(True)
        self._list_history.setUniformItemSizes(False)

        # Layout
        top = QtWidgets.QHBoxLayout()
        top.addWidget(self._label_auto)
        top.addWidget(self._toggle_auto)
        top.addStretch(1)
        top.addWidget(self._btn_add)

        lay = QtWidgets.QVBoxLayout(self)
        lay.addLayout(top)
        lay.addWidget(self._list_history, 1)

        # Connexions
        self._toggle_auto.toggled_changed.connect(self._on_auto_toggled)
        self._btn_add.clicked.connect(self._on_add_clicked)

        # Optional: small auto-add simulator (demo only)
        self._demo_timer = QtCore.QTimer(self)
        self._demo_timer.setInterval(1000)
        self._demo_timer.timeout.connect(self._auto_add_tick)

        # Initial state
        self._apply_auto_state(self._toggle_auto.isChecked())

    # Slots / internals --------------------------------------------------------

    def _apply_auto_state(self, auto: bool) -> None:
        # When auto-add is ON, disable manual "Add"
        self._btn_add.setEnabled(not auto)
        # Start/stop demo timer if requested
        self._demo_timer.setRunning(auto) if hasattr(
            self._demo_timer, "setRunning"
        ) else (self._demo_timer.start() if auto else self._demo_timer.stop())

    @QtCore.Slot(bool)
    def _on_auto_toggled(self, state: bool) -> None:
        self._apply_auto_state(state)
        self.auto_changed.emit(state)

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
        return self._toggle_auto.isChecked()

    def set_auto(self, *, enabled: bool) -> None:
        self._toggle_auto.setChecked(enabled)

    def add_entry(self, text: str) -> None:
        """Add an entry to history. Newest goes to the top."""
        if not text:
            return
        item = QtWidgets.QListWidgetItem(text)
        # Insert at top
        self._list_history.insertItem(0, item)
        # Optional cap
        if self._max_items is not None and self._list_history.count() > self._max_items:
            self._list_history.takeItem(self._list_history.count() - 1)
        # Ensure it's visible at top
        self._list_history.scrollToItem(item, QtWidgets.QAbstractItemView.PositionAtTop)
        self.item_added.emit(text)

    def history(self) -> list[str]:
        return [
            self._list_history.item(i).text() for i in range(self._list_history.count())
        ]
