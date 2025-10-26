from PySide6 import QtWidgets, QtCore
from card_scanner.core.api import Database


class ExportWidget(QtWidgets.QToolButton):
    export_requested = QtCore.Signal(Database)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setText("Export")
        self.setPopupMode(QtWidgets.QToolButton.InstantPopup)

        menu = QtWidgets.QMenu(self)

        # Crée une action pour chaque valeur de l'enum
        for db in Database:
            action = menu.addAction(db.value)
            action.triggered.connect(
                lambda _, db=db: self.export_requested.emit(db)
            )

        self.setMenu(menu)
