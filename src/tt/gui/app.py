from pathlib import Path
from typing import Callable, Optional

from sprats.config import AppPersistence

from tt.data.project import ProjectManager, Project


class App:
    def __init__(self, app_persistence: AppPersistence):
        self.pm = ProjectManager(Path.home() / ".tt" / "projects")
        self.app_persistence = app_persistence
        self.config = app_persistence.config
        self.state = app_persistence.state
        self.project: Optional[Project] = None

        self.exit_application: Callable[[], bool] = lambda: True
        self.show_error: Callable[[str], None] = lambda _: None
        self.set_opened_project_label: Callable[[str], None] = lambda _: None
        self.set_showing_version_label: Callable[[str], None] = lambda _: None

        self.rename_opened_project_menu_enable: Callable[[], None] = lambda: None
        self.rename_opened_project_menu_disable: Callable[[], None] = lambda: None
        self.delete_opened_project_menu_enable: Callable[[], None] = lambda: None
        self.delete_opened_project_menu_disable: Callable[[], None] = lambda: None

    def set_new_open_project(self, project: Project) -> None:
        self.project = project
        self.set_opened_project_label(
            f"Project <em><b>{project.name}</b></em> tracking file <em><b>{project.trace_source.uri()}</b></em>"
        )
        self.set_showing_version_label(f"Traces Version #{project.latest_traces_version}")
        self.delete_opened_project_menu_enable()
        self.rename_opened_project_menu_enable()
