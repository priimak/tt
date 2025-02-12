import sys
from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from sprats.config import AppPersistence

from tt.gui.main_window import TTMainWindow


def main():
    app = QApplication(sys.argv)
    tt_png = Path(__file__).parent / "tt.png"
    app.setWindowIcon(QIcon(f"{tt_png.absolute()}"))

    # Will init main window size to be some fraction of the screen size unless defined elsewhere
    screen_dim: QSize = app.primaryScreen().size()
    screen_width, screen_height = screen_dim.width(), screen_dim.height()

    persistence = AppPersistence(
        app_name = "tt",
        init_config_data = {
            "max_last_opened_files": 10,
            "open_last_opened_project_on_load": True,
            "watch_for_source_changes": True,
            "last_opened_project": ""
        }
    )
    win = TTMainWindow(screen_dim = (screen_width, screen_height), app_persistence = persistence)
    win.show()
    win.activateWindow()
    win.raise_()

    if persistence.config.get_value("open_last_opened_project_on_load", bool):
        last_opened_project_name = persistence.config.get_value("last_opened_project", str)
        if last_opened_project_name is not None and last_opened_project_name.strip() != "":
            try:
                project = win.app.pm.open_existing_project(last_opened_project_name)
                win.app.set_new_open_project(project)
            except Exception as ex:
                win.app.show_error(f"Filed to re-open project. {ex}")

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
