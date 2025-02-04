from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QMenuBar, QWidget

from tt.gui.app import App
from tt.gui.project_management.new_project_dialog import CreateNewProject
from tt.gui.project_management.open_existing_project_dialog import OpenProjectDialog
from tt.gui.settings.settings_dialog import SettingsDialog
from tt.gui.views.create_view_dialog import mk_create_new_view


class FileMenu(QMenu):
    def __init__(self, parent: QMenuBar, app: App, dialogs_parent: QWidget):
        super().__init__("&File", parent)

        def create_new_project():
            new_project_dialog = CreateNewProject(parent, app)
            new_project_dialog.show()

        self.addAction("&New Project", create_new_project)

        def open_existing_project():
            open_project_dialog = OpenProjectDialog(parent, app)
            open_project_dialog.show()

        self.addAction("&Open Project", open_existing_project)

        def reload_traces_from_source():
            assert app.project is not None
            if app.project.load_traces():
                # traces were reloaded
                app.set_showing_version_label(f"Traces Version #{app.project.latest_traces_version}")

        # noinspection PyTypeChecker
        reload_trs_action: QAction = self.addAction("&Reload traces from source",
                                                    reload_traces_from_source)  # pyright: ignore [reportAssignmentType]

        reload_trs_action.setEnabled(False)
        app.reload_traces_menu_enable = lambda: reload_trs_action.setEnabled(True)
        app.reload_traces_menu_disable = lambda: reload_trs_action.setEnabled(False)

        def delete_opened_project():
            pass

        # noinspection PyTypeChecker
        delete_project_action: QAction = self.addAction("&Delete Project",
                                                        delete_opened_project)  # pyright: ignore [reportAssignmentType]
        delete_project_action.setEnabled(False)

        self.addSeparator()

        create_view_action: QAction = self.addAction(
            "Create &View",
            mk_create_new_view(parent, app)
        )  # pyright: ignore [reportAssignmentType]
        create_view_action.setEnabled(False)

        self.addAction("Create Derivative &Trace", ).setEnabled(False)

        app.project_opened_menus_enabled = lambda: (
            delete_project_action.setEnabled(False), create_view_action.setEnabled(True)
        )
        app.project_opened_menus_disable = lambda: (
            delete_project_action.setEnabled(False), create_view_action.setEnabled(False)
        )

        self.addSeparator()

        def show_settings_window():
            settings_dialog = SettingsDialog(parent, app)
            settings_dialog.show()

        self.addAction("&Settings", show_settings_window)

        self.addSeparator()
        self.addAction("&Quit", lambda: app.exit_application())
