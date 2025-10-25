from __future__ import annotations
from apps.gui_qt.widgets.toggle_button_widget import ToggleButton

from PySide6 import QtCore, QtWidgets


class HistoryItemWidget(QtWidgets.QWidget):
    """Widget affiché pour chaque entrée de l'historique, avec compteur et bouton -"""

    remove_requested = QtCore.Signal(QtWidgets.QListWidgetItem)

    def __init__(self, text: str, item: QtWidgets.QListWidgetItem, parent=None) -> None:
        super().__init__(parent)
        self.item = item
        self.count = 1
        self.label_text = QtWidgets.QLabel(text)
        self.label_count = QtWidgets.QLabel(f"x{self.count}")
        self.label_count.setStyleSheet("color: gray; margin-left: 4px;")

        self.btn_remove = QtWidgets.QPushButton("-")
        self.btn_remove.setFixedSize(20, 20)
        self.btn_remove.clicked.connect(self._on_remove_clicked)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.label_text)
        layout.addWidget(self.label_count)
        layout.addStretch(1)
        layout.addWidget(self.btn_remove)
        layout.setContentsMargins(4, 0, 4, 0)

    def increment(self) -> None:
        self.count += 1
        self.label_count.setText(f"x{self.count}")
        self.btn_remove.setVisible(True)

    def decrement(self) -> None:
        self.count -= 1
        self.label_count.setText(f"x{self.count}")
        if self.count <= 0:
            self.remove_requested.emit(self.item)

    def _on_remove_clicked(self) -> None:
        self.decrement()


class HistoryWidget(QtWidgets.QWidget):
    # Signals
    auto_changed = QtCore.Signal(bool)
    item_added = QtCore.Signal(str)

    def __init__(self, max_items: int | None = None, parent=None) -> None:
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

        self._current_card = None

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

        # Timer démo auto
        self._demo_timer = QtCore.QTimer(self)
        self._demo_timer.setInterval(1000)
        self._demo_timer.timeout.connect(self._auto_add_tick)

        # Initial state
        self._apply_auto_state(self._toggle_auto.isChecked())

    # -------------------------------------------------------------------------
    def _apply_auto_state(self, auto: bool) -> None:
        # self._btn_add.setEnabled(not auto)
        if hasattr(self._demo_timer, "setRunning"):
            self._demo_timer.setRunning(auto)
        elif auto:
            self._demo_timer.start()
        else:
            self._demo_timer.stop()

    @QtCore.Slot(bool)
    def _on_auto_toggled(self, state: bool) -> None:
        self._apply_auto_state(state)
        self.auto_changed.emit(state)

    @QtCore.Slot()
    def _on_add_clicked(self) -> None:
        """Ajout manuel — avec compteur"""
        text = self.format(self._current_card)
        if not text:
            return

        # Si la dernière entrée est la même → incrémenter compteur
        if self._list_history.count() > 0:
            first_item = self._list_history.item(0)
            widget = self._list_history.itemWidget(first_item)
            if widget and widget.label_text.text() == text:
                widget.increment()
                return

        # Sinon, nouvelle entrée
        item = QtWidgets.QListWidgetItem()
        widget = HistoryItemWidget(text, item)
        widget.remove_requested.connect(self._remove_item)
        self._list_history.insertItem(0, item)
        self._list_history.setItemWidget(item, widget)

        if self._max_items and self._list_history.count() > self._max_items:
            self._list_history.takeItem(self._list_history.count() - 1)

        self.item_added.emit(text)

    def _remove_item(self, item: QtWidgets.QListWidgetItem) -> None:
        row = self._list_history.row(item)
        self._list_history.takeItem(row)

    @QtCore.Slot()
    def _auto_add_tick(self) -> None:
        if not self.is_auto():
            return

        current_text = self.format(self._current_card)

        if (
            self._list_history.count() == 0
            or self._list_history.itemWidget(
                self._list_history.item(0)
            ).label_text.text()
            != current_text
        ):
            self._on_add_clicked()

    @QtCore.Slot()
    def set_current_card(self, dico: dict) -> None:
        self._current_card = dico

    def format(self, dico: dict) -> str:
        if not dico:
            return ""
        return f"{dico['exp']} | {dico['card_id']}"

    # -------------------------------------------------------------------------
    def is_auto(self) -> bool:
        return self._toggle_auto.isChecked()

    def set_auto(self, *, enabled: bool) -> None:
        self._toggle_auto.setChecked(enabled)

    def history(self) -> list[str]:
        result = []
        for i in range(self._list_history.count()):
            w = self._list_history.itemWidget(self._list_history.item(i))
            if w:
                result.append(f"{w.label_text.text()} X{w.count}")
        return result
