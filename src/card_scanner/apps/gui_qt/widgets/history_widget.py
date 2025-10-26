from __future__ import annotations
from .toggle_button_widget import ToggleButton
from card_scanner.core.api import Database
from pathlib import Path
import csv
from PySide6 import QtCore, QtWidgets


class HistoryItemWidget(QtWidgets.QWidget):
    """Widget affiché pour chaque entrée de l'historique, avec compteur et bouton -"""

    remove_requested = QtCore.Signal(QtWidgets.QListWidgetItem)

    def __init__(
        self, dico: dict, item: QtWidgets.QListWidgetItem, count: int = 1, parent=None
    ) -> None:
        super().__init__(parent)
        self.item = item
        self.dico = dico
        self.count = count
        self.label_text = QtWidgets.QLabel(self.format(dico))
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

    def format(self, dico: dict) -> str:
        if not dico:
            return ""
        return f"{dico['exp'].name} | {dico['card_id']} | {dico['variant']}"

    def is_equal(self, dico: dict) -> bool:
        return dico == self.dico


class HistoryWidget(QtWidgets.QWidget):
    # Signals
    auto_changed = QtCore.Signal(bool)

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
        self._cards_index = {}

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
        if not self._current_card:
            return

        key = (
            self._current_card["exp"],
            self._current_card["card_id"],
            self._current_card["variant"],
        )

        if key in self._cards_index:
            # Incrémenter le compteur
            old_widget = self._cards_index[key]
            old_widget.increment()

            # Supprimer l'ancien item et widget
            old_item = old_widget.item
            row = self._list_history.row(old_item)
            self._list_history.takeItem(row)

            # Recréer un nouvel item et widget pour remonter en haut
            new_item = QtWidgets.QListWidgetItem()
            new_widget = HistoryItemWidget(old_widget.dico, new_item, old_widget.count)
            new_widget.remove_requested.connect(self._remove_item)

            # Ajouter au début de la liste
            self._list_history.insertItem(0, new_item)
            self._list_history.setItemWidget(new_item, new_widget)

            # Mettre à jour le dictionnaire
            self._cards_index[key] = new_widget
            return

        # Sinon, nouvelle entrée
        item = QtWidgets.QListWidgetItem()
        widget = HistoryItemWidget(self._current_card, item)
        widget.remove_requested.connect(self._remove_item)
        self._list_history.insertItem(0, item)
        self._list_history.setItemWidget(item, widget)

        # Ajouter au dictionnaire
        self._cards_index[key] = widget

        # Respecter le max_items
        if self._max_items and self._list_history.count() > self._max_items:
            removed_item = self._list_history.takeItem(self._list_history.count() - 1)
            removed_widget = self._list_history.itemWidget(removed_item)
            if removed_widget:
                removed_key = (
                    removed_widget.dico["exp"],
                    removed_widget.dico["card_id"],
                    removed_widget.dico["variant"],
                )
                self._cards_index.pop(removed_key, None)

    def _remove_item(self, item: QtWidgets.QListWidgetItem) -> None:
        widget = self._list_history.itemWidget(item)
        if widget:
            # Supprimer la carte du dictionnaire
            key = (
                widget.dico["exp"],
                widget.dico["card_id"],
                widget.dico["variant"],
            )
            self._cards_index.pop(key, None)
        row = self._list_history.row(item)
        self._list_history.takeItem(row)

    @QtCore.Slot()
    def _auto_add_tick(self) -> None:
        if not self.is_auto():
            return

        if self._list_history.count() == 0 or not self._list_history.itemWidget(
            self._list_history.item(0)
        ).is_equal(self._current_card):
            self._on_add_clicked()

    @QtCore.Slot()
    def set_current_card(self, dico: dict) -> None:
        self._current_card = dico

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

    def export_csv(self, db: Database) -> None:
        if db is Database.SWUDB:
            print(f"HistoryWidget1 export: {db.value}")
            self.export_history_to_csv()
        elif db is Database.DATABASE2:
            print(f"HistoryWidget2 export: {db.value}")

        else:
            m = "Unknown value of database"
            raise ValueError(m)
        # Ici, tu mets ton code réel pour exporter la CSV

    def export_history_to_csv(self) -> None:
        with Path.open("EXPORT.csv", mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(["Set", "CardNumber", "Count", "IsFoil"])

            for index in range(self._list_history.count()):
                item = self._list_history.item(index)
                widget = self._list_history.itemWidget(item)
                if widget:
                    dico = widget.dico
                    count = widget.count
                    writer.writerow(
                        [
                            dico.get("exp", "").name.split("_")[0],
                            dico.get("card_id", ""),
                            count,
                            dico.get("is_foil", False),
                        ]
                    )
