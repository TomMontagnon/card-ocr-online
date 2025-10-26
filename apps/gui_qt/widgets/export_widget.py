from PySide6 import QtWidgets, QtCore
from core.api.types import Database


class ExportWidget(QtWidgets.QToolButton):
    # Signal qui envoie l'enum choisie
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
