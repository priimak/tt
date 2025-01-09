from PySide6.QtWidgets import QHBoxLayout, QLabel
from pytide6 import Panel

from tt.gui.app import App


class InfoPanel(Panel[QHBoxLayout]):
    def __init__(self, app: App):
        super().__init__(QHBoxLayout())
        self.opened_project_label = QLabel("")
        self.showing_version_label = QLabel("")

        self.layout().addWidget(self.opened_project_label)
        self.layout().addStretch(stretch = 1)
        self.layout().addWidget(self.showing_version_label)

        # connect dispatching methods in App to relevant functions
        app.set_opened_project_label = self.opened_project_label.setText
        app.set_showing_version_label = self.showing_version_label.setText
