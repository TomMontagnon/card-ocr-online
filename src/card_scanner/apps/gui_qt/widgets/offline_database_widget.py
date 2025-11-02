from PySide6 import QtWidgets, QtCore


class OfflineDBPopup(QtWidgets.QWidget):
    directory_selected = QtCore.Signal(str)
    download_clicked = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # --- Checkbox ---
        self.checkbox = QtWidgets.QCheckBox("Offline database")
        layout.addWidget(self.checkbox)

        # --- Champ de fichier + bouton ---
        file_layout = QtWidgets.QHBoxLayout()
        self.dir_line = QtWidgets.QLineEdit()
        self.dir_line.setPlaceholderText("Aucun fichier sélectionné")
        self.dir_line.setEnabled(False)
        self.browse_btn = QtWidgets.QToolButton()
        self.browse_btn.setText("📁")
        self.browse_btn.setEnabled(False)
        file_layout.addWidget(self.dir_line)
        file_layout.addWidget(self.browse_btn)
        layout.addLayout(file_layout)

        # --- Bouton d'export ---
        self.export_btn = QtWidgets.QPushButton("Télécharger")
        self.export_btn.setEnabled(False)
        layout.addWidget(self.export_btn)

        # --- Connexions ---
        self.checkbox.toggled.connect(self._on_checkbox_toggled)
        self.browse_btn.clicked.connect(self._on_browse_clicked)
        self.dir_line.textChanged.connect(self._on_file_changed)
        self.export_btn.clicked.connect(self._on_export_clicked)

    def _on_checkbox_toggled(self, checked: bool):
        self.dir_line.setEnabled(checked)
        self.browse_btn.setEnabled(checked)
        if checked:
            self.export_btn.setEnabled(bool(self.dir_line.text().strip()))
        else:
            self.export_btn.setEnabled(False)

    def _on_browse_clicked(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Choisir un dossier pour la basede données offline",
        )
        if path:
            self.dir_line.setText(path)
            self.directory_selected.emit(path)

    def _on_file_changed(self, text: str):
        self.export_btn.setEnabled(bool(text.strip()))

    def _on_export_clicked(self):
        if self.dir_line.text().strip():
            self.download_clicked.emit(self.dir_line.text().strip())


class OfflineDBWidget(QtWidgets.QToolButton):
    export_requested = QtCore.Signal(str)  # emit le chemin du fichier

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("Offline Database")
        self.setPopupMode(QtWidgets.QToolButton.InstantPopup)

        # Menu personnalisé
        popup = OfflineDBPopup()
        popup.download_clicked.connect(self.export_requested.emit)

        # Crée un QWidgetAction pour afficher le widget dans un QMenu
        action = QtWidgets.QWidgetAction(self)
        action.setDefaultWidget(popup)

        menu = QtWidgets.QMenu(self)
        menu.addAction(action)
        self.setMenu(menu)
