from pathlib import Path
from typing import Callable, Optional

from PySide6.QtWidgets import QWidget
from pytide6 import MainWindow
from sprats.config import AppPersistence

from tt.data.project import ProjectManager, Project


class App:
    def __init__(self, app_persistence: AppPersistence):
        self.pm = ProjectManager(Path.home() / ".tt" / "projects")
        self.app_persistence = app_persistence
        self.config = app_persistence.config
        self.state = app_persistence.state
        self.project: Optional[Project] = None
        self.__ref_change_id: float | None = None

        self.exit_application: Callable[[], bool] = lambda: True
        self.show_error: Callable[[str], None] = lambda _: None
        self.set_opened_project_label: Callable[[str], None] = lambda _: None
        self.set_showing_version_label: Callable[[str], None] = lambda _: None

        self.reload_traces_menu_enable: Callable[[], None] = lambda: None
        self.reload_traces_menu_disable: Callable[[], None] = lambda: None
        self.delete_opened_project_menu_enable: Callable[[], None] = lambda: None
        self.delete_opened_project_menu_disable: Callable[[], None] = lambda: None
        self.notify_tables_require_change: Callable[[], None] = lambda: None
        self.notify_project_panel_on_project_load: Callable[[], None] = lambda: None

        self.main_window: Callable[[], MainWindow] = lambda: None  # pyright: ignore [reportAttributeAccessIssue]
        self.super_parent: Callable[[], QWidget] = lambda: None  # pyright: ignore [reportAttributeAccessIssue]

    def set_new_open_project(self, project: Project) -> None:
        self.project = project
        self.set_opened_project_label(
            f"Project <em><b>{project.name}</b></em> tracking file <em><b>{project.trace_source.uri()}</b></em>"
        )
        self.set_showing_version_label(f"Traces Version #{project.latest_traces_version}")
        self.notify_tables_require_change()
        self.notify_project_panel_on_project_load()
        self.reload_traces_menu_enable()
        self.set_reference_change_id(project.trace_source.change_id())
        self.app_persistence.config.set_value("last_opened_project", project.name)

    def set_reference_change_id(self, change_id: float) -> None:
        self.__ref_change_id = change_id

    def get_reference_change_id(self) -> float | None:
        return self.__ref_change_id
