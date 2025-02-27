from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import Signal, QTimer, QMutex, QPoint
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMessageBox, QTabWidget, QLabel, QWidget
from pytide6 import MainWindow, set_geometry, VBoxPanel, Dialog, VBoxLayout
from pytide6.buttons import PushButton
from pytide6.panel_widget import W, HBoxPanel
from sprats.config import AppPersistence

from tt.data.trace import TraceState
from tt.gui.app import App
from tt.gui.help.help_window import HelpWindow
from tt.gui.menus.menu_bar import MainMenuBar
from tt.gui.panels.info_panel import InfoPanel
from tt.gui.panels.project_panel import ProjectPanel
from tt.gui.panels.traces_panel import TracesPanel
from tt.gui.panels.views_panel import ViewsPanel


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


@dataclass
class Icons:
    help: QIcon


class TTMainWindow(MainWindow):
    signal_show_error = Signal(str)
    signal_prompt_user_to_reload_traces = Signal()
    signal_show_help = Signal(QWidget, str, QPoint)

    def __init__(self, screen_dim: tuple[int, int], app_persistence: AppPersistence):
        super().__init__(objectName = "MainWindow", windowTitle = "Trace Tool")

        self.icons = Icons(help = QIcon(f"{(Path(__file__).parent / "icons" / "help.png").absolute()}"))
        self.screen_dim = screen_dim
        self.super_parent = QWidget()

        tt_png = Path(__file__).parent / "tt.png"
        self.setWindowIcon(QIcon(f"{tt_png.absolute()}"))
        self.sync_mutex = QMutex()

        self.app = App(app_persistence)
        self.app.main_window = lambda: self
        self.app.super_parent = lambda: self.super_parent

        set_geometry(app_state = app_persistence.state, widget = self, screen_dim = screen_dim)

        self.signal_show_error.connect(self.show_error)
        self.signal_prompt_user_to_reload_traces.connect(self.show_prompt_for_trace_reload)

        self.app.exit_application = self.close
        self.app.show_error = self.signal_show_error.emit

        self.signal_show_help.connect(self.show_help)

        self.main_menu_bar = self.setMenuBar(MainMenuBar(self.app, dialogs_parent = self))

        main_widget = QTabWidget()
        main_widget.addTab(TracesPanel(self.app, TraceState.ACTIVE), "Active Traces")
        main_widget.addTab(TracesPanel(self.app, TraceState.INACTIVE), "Inactive Traces")
        main_widget.addTab(ViewsPanel(self.app), "Views")
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

    def show_help(self, parent: QWidget, help_name: str, pos: QPoint) -> None:
        window = HelpWindow(parent, help_name)
        window.show()
        window.raise_()
        window.move(pos)
        win_geo = window.geometry()
        right_edge_x: int = win_geo.x() + win_geo.width()
        bottom_edge_y: int = win_geo.y() + win_geo.height()

        x_out = right_edge_x - self.screen_dim[0]
        if x_out > 0:
            pos.setX(pos.x() - x_out)

        y_out = bottom_edge_y - self.screen_dim[1]
        if y_out > 0:
            pos.setY(pos.y() - y_out)

        if x_out > 0 or y_out > 0:
            window.move(pos)

    def scan_for_traces_change(self) -> None:
        try:
            watch_for_source_changes = self.app.config.get_value("watch_for_source_changes", bool) or False
            if (watch_for_source_changes and self.app.project is not None and self.is_scanner_allowed()
                    and self.app.project.trace_source.has_changed(change_id_ref = self.app.get_reference_change_id())):
                self.block_scanner()
                self.signal_prompt_user_to_reload_traces.emit()
        except:
            pass

    def closeEvent(self, event):
        super().closeEvent(event)
        self.app.close_all_plots()
