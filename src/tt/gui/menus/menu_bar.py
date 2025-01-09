from PySide6.QtWidgets import QMenuBar, QWidget

from tt.gui.app import App
from tt.gui.menus.file_menu import FileMenu


class MainMenuBar(QMenuBar):
    def __init__(self, app: App, dialogs_parent: QWidget):
        super().__init__(None)

        self.file_menu = FileMenu(self, app, dialogs_parent)
        self.addMenu(self.file_menu)
        # self.addMenu(HelpMenu(self, dialogs_parent))
