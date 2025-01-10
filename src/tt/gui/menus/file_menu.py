from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QMenuBar, QWidget

from tt.gui.app import App
from tt.gui.project_management.new_project_dialog import CreateNewProject
from tt.gui.project_management.open_existing_project_dialog import OpenProjectDialog


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
            open_project_dialog = OpenProjectDialog(parent, app)
            open_project_dialog.show()

        self.addAction("&Open Project", open_existing_project)

        def delete_opened_project():
            pass

        delete_opened_project_action: QAction = self.addAction(
            "&Delete Project", delete_opened_project
        )  # pyright: ignore [reportAssignmentType]
        delete_opened_project_action.setEnabled(False)
        app.delete_opened_project_menu_enable = lambda: delete_opened_project_action.setEnabled(True)
        app.delete_opened_project_menu_disable = lambda: delete_opened_project_action.setEnabled(False)

        self.addSeparator()
        self.addAction("&Quit", lambda: app.exit_application())
