# from matplotlib.backends.backend_qt import FigureCanvasQT, NavigationToolbar2QT
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QDialog, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.legend import Legend
from matplotlib.lines import Line2D

from tt.gui.trace_config_dialog import TraceConfigDialog


class PlotFigure(QDialog):
    def __init__(self, main_window, raw_trace):
        super().__init__(main_window)

        from tt.data.trace import Trace
        self.trace: Trace = raw_trace

        self.setWindowTitle(f"Trace: {self.trace.label}")
        self.setModal(False)

        layout = QVBoxLayout()

        self.canvas = FigureCanvas(Figure())
        toolbar = NavigationToolbar(self.canvas, self)
        action = QAction(QIcon("settings.png"), "Trace Config", self)
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
        self.plt1: Line2D = self.ax.plot(x, y, "-", label = self.trace.label)
        self.legend: Legend = self.ax.legend()
        self.legend.set_loc(self.trace.legend_location.lower())
        self.legend.set_visible(self.trace.show_legend)
        self.canvas.figure.tight_layout()

    def show_config(self):
        TraceConfigDialog(self).show()

    def set_show_grid(self, show_grid: bool) -> None:
        self.trace.set_show_grid(show_grid)
        self.ax.grid(show_grid)
        self.canvas.draw()

    def set_show_legend(self, show_legend: bool) -> None:
        self.trace.set_show_legend(show_legend)
        self.legend.set_visible(show_legend)
        self.canvas.draw()

    def set_x_label(self, label: str) -> None:
        self.ax.set_xlabel(label)
        self.trace.set_x_label(label)
        self.canvas.figure.tight_layout()
        self.canvas.draw()

    def set_y_label(self, label: str) -> None:
        self.ax.set_ylabel(label)
        self.trace.set_y_label(label)
        self.canvas.figure.tight_layout()
        self.canvas.draw()

    def set_title(self, title: str) -> None:
        self.ax.set_title(title)
        self.trace.set_title(title)
        self.canvas.figure.tight_layout()
        self.canvas.draw()

    def set_legend_location(self, legend_location: str) -> None:
        self.trace.set_legend_location(legend_location)
        self.legend.set_loc(legend_location.lower())
        if self.legend.get_visible():
            self.canvas.draw()

    def set_y_scale(self, y_scale: str) -> None:
        try:
            self.trace.set_y_scale(y_scale)
            self.plt1.pop(0).remove()

            x, y = self.trace.xy
            self.plt1 = self.ax.plot(x, y, "-", label = self.windowTitle())

            self.ax.relim()
            self.ax.autoscale_view()
            self.canvas.draw()
        except:
            pass

    def set_y_offset(self, y_offset: str) -> None:
        try:
            self.trace.set_y_offset(y_offset)
            self.plt1.pop(0).remove()

            x, y = self.trace.xy
            self.plt1 = self.ax.plot(x, y, "-", label = self.windowTitle())

            self.ax.relim()
            self.ax.autoscale_view()
            self.canvas.draw()
        except:
            pass
