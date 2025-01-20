from PySide6.QtWidgets import QComboBox, QLabel
from pytide6 import Dialog, VBoxLayout, HBoxPanel, CheckBox, LineTextInput
from pytide6.buttons import PushButton
from pytide6.inputs import FloatTextInput
from pytide6.widget_wrapper import W

LEGEND_LOCATIONS = [
    "Best", "Upper Right", "Upper Left", "Lower Left", "Lower Right", "Right", "Center Left",
    "Center Right", "Lower Center", "Upper Center", "Center"
]


class TraceConfigDialog(Dialog):
    def __init__(self, plot_figure):
        super().__init__(parent = plot_figure, windowTitle = f"Config for [{plot_figure.trace.label}]", modal = True)

        from tt.gui.figure import PlotFigure
        figure: PlotFigure = plot_figure

        legend_location = QComboBox()
        legend_location.setMinimumWidth(150)
        legend_location.addItems(LEGEND_LOCATIONS)
        current_legend_location = figure.trace.legend_location.lower()
        idx = [i[0] for i in enumerate(LEGEND_LOCATIONS) if current_legend_location == i[1].lower()]
        if len(idx) > 0:
            legend_location.setCurrentIndex(idx[0])
        legend_location.currentTextChanged.connect(figure.set_legend_location)

        self.setLayout(VBoxLayout([
            LineTextInput("Figure title", figure.trace.title, on_text_change = figure.set_title),
            HBoxPanel([
                CheckBox("", checked = figure.trace.show_legend, on_change = figure.set_show_legend),
                QLabel("Show legend"),
                W(HBoxPanel(), stretch = 1)
            ]),
            HBoxPanel([QLabel("Legend location"), legend_location, W(HBoxPanel(), stretch = 1)]),
            LineTextInput("X-axis label", figure.trace.x_label, on_text_change = figure.set_x_label),
            LineTextInput("Y-axis label", figure.trace.y_label, on_text_change = figure.set_y_label),
            HBoxPanel([
                CheckBox("", checked = figure.trace.show_grid, on_change = figure.set_show_grid),
                QLabel("Show grid"),
                W(HBoxPanel(), stretch = 1)
            ]),
            HBoxPanel([
                QLabel("Linear transform. Y' = "),
                FloatTextInput(label = None, text = f"{figure.trace.y_scale}", on_text_change = figure.set_y_scale),
                QLabel(" × Y + "),
                FloatTextInput(label = None, text = f"{figure.trace.y_offset}", on_text_change = figure.set_y_offset)
            ]),
            HBoxPanel([W(HBoxPanel(), stretch = 1), PushButton("Ok", on_clicked = self.close)])
        ]))
