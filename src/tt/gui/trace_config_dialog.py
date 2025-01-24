from PySide6.QtWidgets import QComboBox, QLabel
from pytide6 import Dialog, VBoxLayout, HBoxPanel, CheckBox, LineTextInput, VBoxPanel
from pytide6.buttons import PushButton
from pytide6.inputs import FloatTextInput
from pytide6.widget_wrapper import W

from tt.data.overlays import OverlaySavitzkyGolay, OverlayLowpass, OverlayNone

LEGEND_LOCATIONS = [
    "Best", "Upper Right", "Upper Left", "Lower Left", "Lower Right", "Right", "Center Left",
    "Center Right", "Lower Center", "Upper Center", "Center"
]


class TraceConfigDialog(Dialog):
    def __init__(self, plot_figure):
        super().__init__(parent = plot_figure, windowTitle = f"Config for [{plot_figure.original_trace.label}]",
                         modal = True)

        from tt.gui.figure import PlotFigure
        self.figure: PlotFigure = plot_figure

        legend_location = QComboBox()
        legend_location.setMinimumWidth(150)
        legend_location.addItems(LEGEND_LOCATIONS)
        current_legend_location = self.figure.original_trace.legend_location.lower()
        idx = [i[0] for i in enumerate(LEGEND_LOCATIONS) if current_legend_location == i[1].lower()]
        if len(idx) > 0:
            legend_location.setCurrentIndex(idx[0])
        legend_location.currentTextChanged.connect(self.figure.set_legend_location)

        filter_name = QComboBox()
        filter_name.addItem("None")
        filter_name.addItem("Savitzky–Golay")
        filter_name.addItem("Lowpass")
        # filter_name.addItem("Bandstop")
        filter_name.currentTextChanged.connect(self.process_filter_change)

        self.savgol_window_input = LineTextInput("window", on_text_change = self.process_savgol_parameters_change)
        self.savgol_window_input.setVisible(False)

        self.lowpass_freq_cutoff = LineTextInput("Cutoff Frequency", on_text_change = self.process_lowpass_param_change)
        self.lowpass_freq_cutoff.setVisible(False)

        self.bandstop_freq_1 = LineTextInput("From Freq.")
        self.bandstop_freq_1.setVisible(False)

        self.bandstop_freq_2 = LineTextInput("To Freq.")
        self.bandstop_freq_2.setVisible(False)

        match self.figure.original_trace.overlay:
            case OverlaySavitzkyGolay(window_length, _):
                self.savgol_window_input.setText(window_length)
                self.savgol_window_input.setVisible(True)
                filter_name.setCurrentIndex(1)
            case OverlayLowpass():
                self.lowpass_freq_cutoff.setText(f"{self.figure.original_trace.overlay.frequency}")
                filter_name.setCurrentIndex(2)
            case _:
                filter_name.setCurrentIndex(0)

        self.setLayout(VBoxLayout([
            LineTextInput("Figure title", self.figure.original_trace.title, on_text_change = self.figure.set_title),
            HBoxPanel([
                CheckBox("", checked = self.figure.original_trace.show_legend, on_change = self.figure.set_show_legend),
                QLabel("Show legend"),
                W(HBoxPanel(), stretch = 1)
            ]),
            HBoxPanel([QLabel("Legend location"), legend_location, W(HBoxPanel(), stretch = 1)]),
            LineTextInput("X-axis label", self.figure.original_trace.x_label, on_text_change = self.figure.set_x_label),
            LineTextInput("Y-axis label", self.figure.original_trace.y_label, on_text_change = self.figure.set_y_label),
            HBoxPanel([
                CheckBox("", checked = self.figure.original_trace.show_grid, on_change = self.figure.set_show_grid),
                QLabel("Show grid"),
                W(HBoxPanel(), stretch = 1)
            ]),
            HBoxPanel([
                QLabel("Linear transform. Y' = "),
                FloatTextInput(label = None, text = f"{self.figure.original_trace.y_scale}",
                               on_text_change = self.figure.set_y_scale),
                QLabel(" × Y + "),
                FloatTextInput(label = None, text = f"{self.figure.original_trace.y_offset}",
                               on_text_change = self.figure.set_y_offset)
            ]),
            HBoxPanel([
                QLabel("Overlay filtered signal"),
                filter_name,
                self.savgol_window_input,
                self.lowpass_freq_cutoff,
                self.bandstop_freq_1,
                self.bandstop_freq_2,
                # CheckBox("", checked = figure.original_trace.show_grid, on_change = figure.set_show_grid),
                W(HBoxPanel(), stretch = 1)
            ]),
            W(VBoxPanel(), stretch = 1),
            HBoxPanel([W(HBoxPanel(), stretch = 1), PushButton("Ok", on_clicked = self.close)]),
        ]))

    def process_lowpass_param_change(self, freq_value: str) -> None:
        try:
            self.figure.original_trace.overlay.set_cutoff_frequency(freq_value)
            self.figure.replot_main_trace()
            self.figure.original_trace.persist()
        except:
            pass

    def process_savgol_parameters_change(self, window_value: str) -> None:
        try:
            if window_value.endswith("%"):
                new_window_value = int(window_value.replace("%", "").strip())
                self.figure.original_trace.overlay.set_window_length(
                    f"{new_window_value}%")  # pyright: ignore [reportAttributeAccessIssue]
            else:
                new_window_value = int(window_value.strip())
                self.figure.original_trace.overlay.set_window_length(
                    f"{new_window_value}")  # pyright: ignore [reportAttributeAccessIssue]
            self.figure.replot_main_trace()
            self.figure.original_trace.persist()
        except:
            pass

    def process_filter_change(self, filter_name: str) -> None:
        match filter_name:
            case "Savitzky–Golay":
                self.lowpass_freq_cutoff.setVisible(False)
                self.bandstop_freq_1.setVisible(False)
                self.bandstop_freq_2.setVisible(False)
                self.savgol_window_input.setVisible(True)

                if not isinstance(self.figure.original_trace.overlay, OverlaySavitzkyGolay):
                    filter = OverlaySavitzkyGolay.default()
                    self.figure.set_overlay(filter)
                    self.savgol_window_input.setText(filter.window_length)

            case "Lowpass":
                self.lowpass_freq_cutoff.setVisible(True)
                self.bandstop_freq_1.setVisible(False)
                self.bandstop_freq_2.setVisible(False)
                self.savgol_window_input.setVisible(False)

                if not isinstance(self.figure.original_trace.overlay, OverlayLowpass):
                    filter = OverlayLowpass.default()
                    self.figure.set_overlay(filter)
                    self.lowpass_freq_cutoff.setText(f"{filter.frequency}")

            case "Bandstop":
                self.lowpass_freq_cutoff.setVisible(False)
                self.bandstop_freq_1.setVisible(True)
                self.bandstop_freq_2.setVisible(True)
                self.savgol_window_input.setVisible(False)

            case _:
                self.lowpass_freq_cutoff.setVisible(False)
                self.bandstop_freq_1.setVisible(False)
                self.bandstop_freq_2.setVisible(False)
                self.savgol_window_input.setVisible(False)
                self.figure.set_overlay(OverlayNone())
