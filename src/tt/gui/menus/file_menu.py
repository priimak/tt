from PySide6.QtWidgets import QMenu, QMenuBar, QWidget

from tt.gui.app import App
from tt.gui.new_project_dialog import CreateNewProject


# from csv_vaql_browser.app_context import AppContext
# from csv_vaql_browser.settings_dialog import SettingsDialog
# from csv_vaql_browser.tools.recenetly_opened_files import init_recently_opened_menu


class FileMenu(QMenu):
    def __init__(self, parent: QMenuBar, app: App, dialogs_parent: QWidget):
        super().__init__("&File", parent)

        def create_new_project():
            new_project_dialog = CreateNewProject(parent, app)
            new_project_dialog.show()

        # New Project - menu item
        self.addAction("&New Project", create_new_project)

        def open_existing_project():
            print(app.pm.list_project_names())

        self.addAction("&Open Project", open_existing_project)

        self.addSeparator()
        self.addAction("&Quit", lambda: app.exit_application())
