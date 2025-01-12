from PySide6.QtCore import Signal
from PySide6.QtWidgets import QMessageBox, QVBoxLayout, QTabWidget
from pytide6 import MainWindow, set_geometry, VBoxPanel, Panel
from sprats.config import AppPersistence

from src.tt.gui.app import App
from tt.gui.menus.menu_bar import MainMenuBar
from tt.gui.panels.info_panel import InfoPanel


class TTMainWindow(MainWindow):
    signal_show_error = Signal(str)

    def __init__(self, screen_dim: tuple[int, int], app_persistence: AppPersistence):
        super().__init__(objectName = "MainWindow", windowTitle = "Trace Tool")

        self.app = App(app_persistence)
        set_geometry(app_state = app_persistence.state, widget = self, screen_dim = screen_dim)

        self.signal_show_error.connect(self.show_error)

        self.app.exit_application = self.close
        self.app.show_error = self.signal_show_error.emit

        self.main_menu_bar = self.setMenuBar(MainMenuBar(self.app, dialogs_parent = self))

        main_widget = QTabWidget()
        # noinspection PyTypeChecker
        main_widget.addTab(Panel(QVBoxLayout()), "Active Traces")
        main_widget.addTab(Panel(QVBoxLayout()), "Inactive Traces")
        main_widget.addTab(Panel(QVBoxLayout()), "Views")

        self.setCentralWidget(
            VBoxPanel(
                spacing = 0, margins = (5, 5, 5, 1)
            ).addWidget(
                main_widget,
                stretch = 1
            ).addWidget(
                InfoPanel(self.app)
            )
        )

    def show_error(self, message: str) -> None:
        QMessageBox.critical(self, "Error", message)
