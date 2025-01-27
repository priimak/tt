from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvas  # pyright: ignore [reportAttributeAccessIssue]
from matplotlib.backends.backend_qtagg import \
    NavigationToolbar2QT as NavigationToolbar  # pyright: ignore [reportPrivateImportUsage]
from matplotlib.figure import Figure


class PlotView(QWidget):
    def __init__(self, main_window, app):
        super().__init__(main_window)
        from tt.gui.app import App
        self.app: App = app

        self.setWindowFlags(Qt.WindowType.Window)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.canvas = FigureCanvas(Figure())
        toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(toolbar)

        layout.addWidget(self.canvas, stretch = 1)
        self.ax = self.canvas.figure.subplots(3, 1, sharex = True,
                                              gridspec_kw = {"wspace": 0, "hspace": 0.05, "height_ratios": [1, 2, 3]})
        self.ax[1].plot(range(10))
        self.ax[2].plot(range(15))
        self.ax[0].set_xticks([])
        self.ax[1].set_xticks([])

        # self.ax.relim()
        # self.ax.autoscale_view()
        self.canvas.draw()
