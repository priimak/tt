# from matplotlib.backends.backend_qt import FigureCanvasQT, NavigationToolbar2QT
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QVBoxLayout, QWidget, QComboBox, QLabel
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.legend import Legend
from matplotlib.lines import Line2D

from tt.gui.trace_config_dialog import TraceConfigDialog


class PlotFigure(QWidget):
    def __init__(self, main_window, raw_trace, app):
        from tt.gui.app import App
        self.app: App = app
        super().__init__(main_window)
        self.setWindowFlags(Qt.WindowType.Window)
        from tt.data.trace import Trace
        self.original_trace: Trace = raw_trace
        self.trace: Trace = raw_trace
        self.trace_1: Trace | None = None
        self.trace_name = raw_trace.name

        self.setWindowTitle(f"Trace: {self.trace.label}")

        layout = QVBoxLayout()

        self.canvas = FigureCanvas(Figure())
        toolbar = NavigationToolbar(self.canvas, self)

        v1 = QComboBox(self)
        v1.addItem("None")
        v1.addItems([f"{v}" for v in reversed(range(1, app.project.latest_traces_version + 1))])
        v1.setCurrentIndex(0)
        v1.currentTextChanged.connect(self.set_v1_version)
        toolbar.addWidget(v1)
        toolbar.addWidget(QLabel(" <> "))

        v2 = QComboBox(self)
        v2.addItem("None")
        v2.addItems([f"{v}" for v in reversed(range(1, app.project.latest_traces_version + 1))])
        v2.setCurrentIndex(app.project.latest_traces_version - self.trace.version + 1)
        v2.currentTextChanged.connect(self.set_v2_version)
        toolbar.addWidget(v2)

        settings_png = Path(__file__).parent / "settings.png"
        action = QAction(QIcon(f"{settings_png.absolute()}"), "Trace Config", self)
        action.triggered.connect(self.show_config)
        toolbar.addAction(action)

        layout.addWidget(toolbar)

        self.setLayout(layout)

        layout.addWidget(self.canvas, stretch = 1)
        self.ax = self.canvas.figure.subplots()
        self.ax.set_title(self.trace.title)
        self.ax.grid(self.trace.show_grid)
        self.ax.set_xlabel(self.trace.x_label)
        self.ax.set_ylabel(self.trace.y_label)
        x, y = self.trace.xy
        self.plt1: Line2D | None = None
        self.plt2: Line2D = self.ax.plot(x, y, "-", label = self.trace.label)
        self.legend: Legend = self.ax.legend()
        self.legend.set_loc(self.trace.legend_location.lower())
        self.legend.set_visible(self.trace.show_legend)
        self.canvas.figure.tight_layout()

    def show_config(self):
        TraceConfigDialog(self).show()

    def set_show_grid(self, show_grid: bool) -> None:
        self.original_trace.set_show_grid(show_grid)
        self.ax.grid(show_grid)
        self.canvas.draw()

    def set_show_legend(self, show_legend: bool) -> None:
        self.original_trace.set_show_legend(show_legend)
        self.legend.set_visible(show_legend)
        self.canvas.draw()

    def set_x_label(self, label: str) -> None:
        self.ax.set_xlabel(label)
        self.original_trace.set_x_label(label)
        self.canvas.figure.tight_layout()
        self.canvas.draw()

    def set_y_label(self, label: str) -> None:
        self.ax.set_ylabel(label)
        self.original_trace.set_y_label(label)
        self.canvas.figure.tight_layout()
        self.canvas.draw()

    def set_title(self, title: str) -> None:
        self.ax.set_title(title)
        self.original_trace.set_title(title)
        self.canvas.figure.tight_layout()
        self.canvas.draw()

    def set_legend_location(self, legend_location: str) -> None:
        self.original_trace.set_legend_location(legend_location)
        self.legend.set_loc(legend_location.lower())
        if self.legend.get_visible():
            self.canvas.draw()

    def set_y_scale(self, y_scale: str) -> None:
        try:
            self.original_trace.set_y_scale(y_scale)
            if self.trace is not None:
                self.trace.set_y_scale(y_scale)
            if self.trace_1 is not None:
                self.trace_1.set_y_scale(y_scale)

            self.replot_main_trace()
        except:
            pass

    def set_y_offset(self, y_offset: str) -> None:
        try:
            self.original_trace.set_y_offset(y_offset)
            if self.trace is not None:
                self.trace.set_y_offset(y_offset)
            if self.trace_1 is not None:
                self.trace_1.set_y_offset(y_offset)
            self.replot_main_trace()
        except:
            pass

    def replot_main_trace(self) -> None:
        self.ax.clear()
        self.ax.set_title(self.original_trace.title)
        self.ax.grid(self.original_trace.show_grid)
        self.ax.set_xlabel(self.original_trace.x_label)
        self.ax.set_ylabel(self.original_trace.y_label)

        if self.trace_1 is not None:
            x, y = self.trace_1.xy

            if self.trace is None:
                self.plt1 = self.ax.plot(x, y, "-", label = f"{self.trace_1.label}")
            else:
                self.plt1 = self.ax.plot(x, y, "-", label = f"{self.trace_1.label} # {self.trace_1.version}")

        if self.trace is not None:
            x, y = self.trace.xy
            if self.trace_1 is None:
                self.plt2 = self.ax.plot(x, y, "-", label = self.trace.label)
            else:
                self.plt2 = self.ax.plot(x, y, "-", label = f"{self.trace.label} # {self.trace.version}")

        if self.trace_1 is not None and self.trace is not None:
            self.legend: Legend = self.ax.legend()
            self.legend.set_loc(self.original_trace.legend_location.lower())
            self.legend.set_visible(self.original_trace.show_legend)
            self.canvas.figure.tight_layout()
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

    def set_v2_version(self, new_version: str) -> None:
        if self.plt2 is not None:
            self.plt2.pop(0).remove()
        if new_version == "None":
            self.trace = None
            self.plt2 = None
        else:
            assert self.app.project is not None
            self.trace = self.app.project.traces(version = int(new_version), trace_name = self.trace_name)[0]
        self.replot_main_trace()

    def set_v1_version(self, new_version: str) -> None:
        if self.plt1 is not None:
            self.plt1.pop(0).remove()
        if new_version == "None":
            self.trace_1 = None
            self.plt1 = None
        else:
            assert self.app.project is not None
            self.trace_1 = self.app.project.traces(version = int(new_version), trace_name = self.trace_name)[0]
        self.replot_main_trace()
