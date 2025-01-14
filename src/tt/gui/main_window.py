from PySide6.QtCore import Signal, QTimer, QMutex
from PySide6.QtWidgets import QMessageBox, QVBoxLayout, QTabWidget, QLabel
from pytide6 import MainWindow, set_geometry, VBoxPanel, Panel, Dialog, VBoxLayout
from pytide6.buttons import PushButton
from pytide6.panel_widget import W, HBoxPanel
from sprats.config import AppPersistence

from src.tt.gui.app import App
from tt.data.trace import TraceState
from tt.gui.menus.menu_bar import MainMenuBar
from tt.gui.panels.info_panel import InfoPanel
from tt.gui.panels.project_panel import ProjectPanel
from tt.gui.panels.traces_panel import TracesPanel


class TracesChangedDialog(Dialog):
    def __init__(self, parent: "TTMainWindow", app: App):
        super().__init__(parent, windowTitle = "Reload Traces", modal = True)

        def on_yes():
            try:
                assert app.project is not None
                traces_loaded, change_id = app.project.load_traces()
                if traces_loaded:
                    app.set_showing_version_label(f"Traces Version #{app.project.latest_traces_version}")
                    app.set_reference_change_id(change_id)
            finally:
                self.close()
                parent.unblock_scanner()

        def on_no():
            self.close()
            assert app.project is not None
            app.set_reference_change_id(app.project.trace_source.change_id(live = True))
            parent.unblock_scanner()

        yes_button = PushButton("Yes", on_clicked = on_yes)
        self.setLayout(VBoxLayout([
            QLabel("Traces source has changed.\nWould you like to load latest version of traces?"),
            HBoxPanel([W(HBoxPanel(), stretch = 1), yes_button, PushButton("No", on_clicked = on_no)])
        ]))


class TTMainWindow(MainWindow):
    signal_show_error = Signal(str)
    signal_prompt_user_to_reload_traces = Signal()

    def __init__(self, screen_dim: tuple[int, int], app_persistence: AppPersistence):
        super().__init__(objectName = "MainWindow", windowTitle = "Trace Tool")
        self.sync_mutex = QMutex()

        self.app = App(app_persistence)
        set_geometry(app_state = app_persistence.state, widget = self, screen_dim = screen_dim)

        self.signal_show_error.connect(self.show_error)
        self.signal_prompt_user_to_reload_traces.connect(self.show_prompt_for_trace_reload)

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
        self.__scanner_go = True

    def is_scanner_allowed(self) -> bool:
        self.sync_mutex.lock()
        try:
            return self.__scanner_go
        finally:
            self.sync_mutex.unlock()

    def block_scanner(self) -> None:
        self.sync_mutex.lock()
        try:
            self.__scanner_go = False
        finally:
            self.sync_mutex.unlock()

    def unblock_scanner(self) -> None:
        self.sync_mutex.lock()
        try:
            self.__scanner_go = True
        finally:
            self.sync_mutex.unlock()

    def show_error(self, message: str) -> None:
        QMessageBox.critical(self, "Error", message)

    def show_prompt_for_trace_reload(self) -> None:
        TracesChangedDialog(self, self.app).show()

    def scan_for_traces_change(self) -> None:
        try:
            watch_for_source_changes = self.app.config.get_value("watch_for_source_changes", bool) or False
            if (watch_for_source_changes and self.app.project is not None and self.is_scanner_allowed()
                    and self.app.project.trace_source.has_changed(change_id_ref = self.app.get_reference_change_id())):
                self.block_scanner()
                self.signal_prompt_user_to_reload_traces.emit()
        except:
            pass
