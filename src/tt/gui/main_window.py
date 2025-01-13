from PySide6.QtCore import Signal, QTimer
from PySide6.QtWidgets import QMessageBox, QVBoxLayout, QTabWidget
from pytide6 import MainWindow, set_geometry, VBoxPanel, Panel, Dialog
from pytide6.panel_widget import W
from sprats.config import AppPersistence

from src.tt.gui.app import App
from tt.data.trace import TraceState
from tt.gui.menus.menu_bar import MainMenuBar
from tt.gui.panels.info_panel import InfoPanel
from tt.gui.panels.project_panel import ProjectPanel
from tt.gui.panels.traces_panel import TracesPanel


class TracesChangedDialog(Dialog):
    def __init__(self, parent, app: App):
        super().__init__(parent)


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
        main_widget.addTab(TracesPanel(self.app, TraceState.ACTIVE), "Active Traces")
        main_widget.addTab(TracesPanel(self.app, TraceState.INACTIVE), "Inactive Traces")
        main_widget.addTab(Panel(QVBoxLayout()), "Views")
        main_widget.addTab(ProjectPanel(self.app), "Project")

        self.setCentralWidget(
            VBoxPanel(
                widgets = [W(main_widget, stretch = 1), InfoPanel(self.app)],
                spacing = 0, margins = (5, 5, 5, 1)
            )
        )

        self.scanner_timer = QTimer()
        self.scanner_timer.timeout.connect(self.scan_for_traces_change)
        self.scanner_timer.setSingleShot(False)
        self.scanner_timer.setInterval(1000)
        self.scanner_timer.start()

    def show_error(self, message: str) -> None:
        QMessageBox.critical(self, "Error", message)

    # def show_traces_changed(self) -> None:
    #     QMessageBox.

    def scan_for_traces_change(self) -> None:
        print("scan_for_traces_change")
        try:
            watch_for_source_changes = self.app.config.get_value("watch_for_source_changes", bool) or False
            if watch_for_source_changes and self.app.project is not None:
                self.app.project.trace_source.has_changed()

        except:
            pass
