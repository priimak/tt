from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.axes import Axes
from matplotlib.backends.backend_qtagg import FigureCanvas  # pyright: ignore [reportAttributeAccessIssue]
from matplotlib.backends.backend_qtagg import \
    NavigationToolbar2QT as NavigationToolbar  # pyright: ignore [reportPrivateImportUsage]
from matplotlib.figure import Figure
from matplotlib.legend import Legend
from typing_extensions import override

from tt.data.punits import dt
from tt.data.trace import Trace
from tt.data.view import ViewSpec, SubPlot, AxisLean
from tt.gui.trace.figure import PlotFigure
from tt.gui.trace.trace_config_dialog import STAT_FUNC_NAME_2_LABEL
from tt.gui.views.view_config_dialog import ViewConfigDialog


class ViewWindow(QWidget):
    replot_signal = Signal()
    show_config_dialog = Signal()

    def __init__(self, main_window, app, view_name: str):
        super().__init__(None)
        from tt.gui.app import App
        self.app: App = app

        self.view_spec: ViewSpec = app.project.views.get_view_spec(view_name)

        self.setWindowFlags(Qt.WindowType.Window)
        PlotFigure.NEXT_PLOT_ID += 1
        self.setProperty("win_id", f"{PlotFigure.NEXT_PLOT_ID}")
        self.setWindowTitle(f"View: {view_name}")

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.canvas = FigureCanvas(Figure())
        toolbar = NavigationToolbar(self.canvas, self)

        settings_png = Path(__file__).parent.parent / "settings.png"
        config_action = QAction(QIcon(f"{settings_png.absolute()}"), "View Config", self)
        config_action.triggered.connect(self.show_config)
        toolbar.addAction(config_action)

        layout.addWidget(toolbar)
        layout.addWidget(self.canvas, stretch = 1)
        subplots = self.canvas.figure.subplots(
            nrows = self.view_spec.num_rows, ncols = self.view_spec.num_columns, sharex = True
        )
        self.ax = [subplots] if isinstance(subplots, Axes) else subplots
        self.canvas.figure.suptitle(self.view_spec.title)
        self.plot()

        self.replot_signal.connect(self.plot)
        self.show_config_dialog.connect(self.show_config)

    def get_ax(self, row: int, column: int) -> Axes:
        if self.view_spec.num_rows == 1:
            return self.ax[column]
        elif self.view_spec.num_columns == 1:
            return self.ax[row]
        else:
            return self.ax[row][column]  # pyright: ignore [reportIndexIssue]

    def plot(self):
        self.canvas.figure.clear()

        subplots = self.canvas.figure.subplots(
            nrows = self.view_spec.num_rows, ncols = self.view_spec.num_columns, sharex = True
        )
        self.ax = [subplots] if isinstance(subplots, Axes) else subplots

        project = self.app.project
        assert project is not None

        self.canvas.figure.suptitle(self.view_spec.title)

        for row in range(self.view_spec.num_rows):
            for col in range(self.view_spec.num_columns):
                axes = self.get_ax(row, col)

                subplot: SubPlot = self.view_spec.get_subplot(row, col)

                x_axis_label = subplot.x_axis_label
                if x_axis_label != "":
                    axes.set_xlabel(f"{x_axis_label} [{project.dt_unit}]")

                on_axis: set[AxisLean] = {ts.on_axis for ts in subplot.get_trace_specs()}
                have_plots_on_left_axis = AxisLean.LEFT in on_axis
                have_plots_on_right_axis = AxisLean.RIGHT in on_axis
                left_axis = axes
                right_axis = axes.twinx()

                if have_plots_on_left_axis and subplot.left_axis_label.strip() != "":
                    left_axis.set_ylabel(subplot.left_axis_label)
                if have_plots_on_right_axis and subplot.right_axis_label.strip() != "":
                    right_axis.set_ylabel(subplot.right_axis_label)

                if subplot.show_grid:
                    if have_plots_on_left_axis:
                        left_axis.grid(True)
                    if have_plots_on_right_axis:
                        right_axis.grid(True)

                left_axis.yaxis.set_visible(have_plots_on_left_axis)
                right_axis.yaxis.set_visible(have_plots_on_right_axis)
                lines = []
                for ts in subplot.get_trace_specs():
                    traces: list[Trace] = project.traces(version = ts.trace_version, trace_name = ts.name)
                    if traces != []:
                        trace = traces[0]
                        x, y = trace.xy(self.app.project)
                        target_axis: Axes = left_axis if ts.on_axis == AxisLean.LEFT else right_axis  # pyright: ignore [reportAssignmentType]
                        if ts.color == "auto":
                            plt = target_axis.plot(x, y, "-", label = "None")
                        else:
                            plt = target_axis.plot(x, y, "-", color = ts.color, label = "None")

                        lines.extend(plt)

                        # plot overlays
                        if ts.show_filtered_trace:
                            y_filtered = trace.overlay.apply(dt(f"{project.implied_dt} {project.dt_unit}"), x, y)
                            if y_filtered is not None:
                                target_axis.plot(x, y_filtered, "-")

                        # compute stat functions if any
                        if ts.show_legends:
                            altered_label: str = f"{trace.label} V:{trace.version}"
                            for fname in trace.stat_functions:
                                stat_value = project.apply_stat_function(
                                    function_name = fname,
                                    trace_name = trace.name,
                                    trace_version = trace.version,
                                    scaling_factor = trace.y_scale,
                                    offset = trace.y_offset
                                )
                                v = float(f"{stat_value:.2g}")
                                altered_label += f", ${STAT_FUNC_NAME_2_LABEL[fname]}={v}$"
                            plt[0].set_label(altered_label)

                lines_and_labels = [(l, f"{label}") for l in lines if (label := l.get_label()) != "None"]
                if lines_and_labels != []:
                    lines_with_labels, labels = zip(*lines_and_labels)
                    self.legend: Legend = right_axis.legend(
                        lines_with_labels, labels,
                        edgecolor = "black", facecolor = "whitesmoke", framealpha = 0.8
                    )

                    self.legend.set_zorder(100)
                    if subplot.legend_location != "None":
                        self.legend.set_loc(subplot.legend_location.lower())
                        self.legend.set_visible(True)
                    else:
                        self.legend.set_visible(False)

                try:
                    self.canvas.figure.tight_layout()
                except:
                    pass

        self._redraw()

    def show_config(self) -> None:
        ViewConfigDialog(self).exec()

    def closeEvent(self, event):
        super().closeEvent(event)
        self.app.unregister_window(self)

    def set_title(self, title: str) -> None:
        self.view_spec.title = title
        # self.canvas.figure.suptitle(self.view_spec.title)
        # self.canvas.figure.tight_layout()
        # self.canvas.draw()

    def _redraw(self):
        try:
            self.canvas.figure.tight_layout()
            self.canvas.draw()
            self.repaint()
        except:
            pass

    def _get_right_axis(self, ax: Axes) -> Axes:
        return ax._twinned_axes.get_siblings(ax)[1]  # pyright: ignore [reportAttributeAccessIssue]

    def set_grid_on_subplot(self, row: int, column: int) -> None:
        show_grid_p = self.view_spec.get_subplot(row, column).show_grid

        ax = self.get_ax(row, column)
        ax.grid(show_grid_p)
        self._get_right_axis(ax).grid(show_grid_p)

        self._redraw()

    def update_ylabels_on_subplot(self, row: int, column: int) -> None:
        subplot = self.view_spec.get_subplot(row, column)

        ax = self.get_ax(row, column)
        if ax.yaxis.get_visible():
            ax.yaxis.set_label_text(subplot.left_axis_label)

        ax = self._get_right_axis(ax)
        if ax.yaxis.get_visible():
            ax.yaxis.set_label_text(subplot.right_axis_label)

        self._redraw()

    def update_xlabel_on_subplot(self, row: int, column: int) -> None:
        x_axis_label = self.view_spec.get_subplot(row, column).x_axis_label
        assert self.app.project is not None
        if x_axis_label == "":
            self.get_ax(row, column).set_xlabel(None)
        else:
            self.get_ax(row, column).set_xlabel(f"{x_axis_label} [{self.app.project.dt_unit}]")
        self._redraw()

    def update_legends_on_subplot(self, row: int, column: int) -> None:
        # legend = self.get_ax(row, column).legend_
        legend = self._get_right_axis(self.get_ax(row, column)).legend_

        if legend is not None:
            subplot = self.view_spec.get_subplot(row, column)
            if subplot.legend_location != "None":
                legend.set_loc(subplot.legend_location.lower())
                legend.set_visible(True)
            else:
                legend.set_visible(False)
            self._redraw()

    @override
    def keyPressEvent(self, event):
        super().keyPressEvent(event)

        if event.key() == Qt.Key.Key_Escape:
            self.close()
