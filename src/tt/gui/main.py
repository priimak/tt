import sys

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication
from sprats.config import AppPersistence

from src.tt.gui.main_window import TTMainWindow


def main():
    app = QApplication(sys.argv)

    # Will init main window size to be some fraction of the screen size
    # unless defined elsewhere
    screen_dim: QSize = app.primaryScreen().size()
    screen_width, screen_height = screen_dim.width(), screen_dim.height()

    persistence = AppPersistence(
        app_name = "tt",
        init_config_data = {
            "max_last_opened_files": 10,
            "open_last_opened_file_on_load": False,
            "first_time_run": True
        }
    )
    win = TTMainWindow(screen_dim = (screen_width, screen_height), app_persistence = persistence)
    win.show()
    # win.app.reopen_last_opened_file()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
