from typing import List, Callable, Self

from PySide6.QtCore import QMargins
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QComboBox, QLabel, QMenu, QHBoxLayout, QFrame, QWidget
from pytide6 import Dialog, VBoxLayout, HBoxPanel, CheckBox, LineTextInput, VBoxPanel, Layout
from pytide6.buttons import PushButton
from pytide6.inputs import FloatTextInput
from pytide6.widget_wrapper import W

from tt.data.legends import LEGEND_LOCATIONS
from tt.data.overlays import OverlaySavitzkyGolay, OverlayLowpass, OverlayNone

STAT_FUNC_NAME_2_LABEL = {
    "min": r"Y_{-}",
    "max": r"Y^{+}",
    "range": r"\Delta",
    "mean": r"\overline{Y}",
    "stdev": r"\sigma",
}


class StatFuncLabel(QFrame):
    def __init__(self, fname: str, remove_action: Callable[[Self], None]):
        super().__init__()
        self.fname = fname
        self.remove_action = remove_action
        layout = Layout(QHBoxLayout(), spacing = 2, margins = 2)
        self.setLayout(layout)
        self.setObjectName("StatFuncLabel")
        fname_label = QLabel(fname)
        fname_label.setStyleSheet("QLabel { font-weight: bold; }")
        layout.addWidget(fname_label)
        del_label = QLabel("✕")
        del_label.setStyleSheet(
            "QLabel {border: 1px solid black;}\n"
            "QLabel::hover{ background:black; color:white; }"
        )

        def remove_label(ev: QMouseEvent) -> None:
            self.remove_action(self)
            self.setParent(None)

        del_label.mousePressEvent = remove_label
        layout.addWidget(del_label)
        self.setStyleSheet("QFrame#StatFuncLabel {border: 1px solid black;}")


class TraceConfigDialog(Dialog):
    def __init__(self, plot_figure):
        super().__init__(parent = plot_figure, windowTitle = f"Config for [{plot_figure.original_trace.label}]",
                         modal = True)
        self.suppress_change_processing = True
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

        self.stat_func_labels: List[StatFuncLabel] = []

        filter_name = QComboBox()
        filter_name.addItems(["None", "Savitzky–Golay", "Lowpass"])
        filter_name.currentTextChanged.connect(self.process_filter_change)

        self.savgol_window_input = LineTextInput("window", on_text_change = self.process_savgol_parameters_change)
        self.savgol_window_input.setVisible(False)

        self.lowpass_freq_cutoff = LineTextInput("Cutoff Frequency", on_text_change = self.process_lowpass_param_change)
        self.lowpass_freq_cutoff.setVisible(False)

        self.bandstop_freq_1 = LineTextInput("From Freq.")
        self.bandstop_freq_1.setVisible(False)

        self.bandstop_freq_2 = LineTextInput("To Freq.")
        self.bandstop_freq_2.setVisible(False)

        ovr = self.figure.original_trace.overlay
        if isinstance(ovr, OverlaySavitzkyGolay):
            self.savgol_window_input.setText(ovr.window_length)
            self.savgol_window_input.setVisible(True)
            filter_name.setCurrentIndex(1)
        elif isinstance(ovr, OverlayLowpass):
            self.lowpass_freq_cutoff.setText(f"{ovr.frequency}")
            filter_name.setCurrentIndex(2)
        else:
            filter_name.setCurrentIndex(0)

        self.add_function_label = QLabel("＋", parent = self)
        self.add_function_label.setContentsMargins(QMargins(2, 2, 2, 2))
        self.add_function_label.styleSheet()
        self.add_function_label.setStyleSheet(
            "QLabel::hover{ background:black; color:white; }\n"
            "QLabel { border: 1px solid black; font-weight: bold; }"
        )
        self.add_function_label.mousePressEvent = self.show_add_stat_function_menu
        functions_panel_elements: list[QWidget | W] = [QLabel("Stat. functions: ")]

        for fname in self.figure.original_trace.stat_functions:
            sfl = StatFuncLabel(fname, self.remove_stat_function)
            functions_panel_elements.append(sfl)
            self.stat_func_labels.append(sfl)

        functions_panel_elements.append(self.add_function_label)
        functions_panel_elements.append(W(HBoxPanel(), stretch = 1))
        self.functions_panel = HBoxPanel(functions_panel_elements)  # pyright: ignore [reportArgumentType]

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
                W(HBoxPanel(), stretch = 1)
            ]),
            self.functions_panel,
            W(VBoxPanel(), stretch = 1),
            HBoxPanel([W(HBoxPanel(), stretch = 1), PushButton("Ok", on_clicked = self.close)]),
        ]))
        self.suppress_change_processing = False

    def process_lowpass_param_change(self, freq_value: str) -> None:
        if self.suppress_change_processing:
            return
        try:
            assert isinstance(self.figure.original_trace.overlay, OverlayLowpass)
            self.figure.original_trace.overlay.set_cutoff_frequency(freq_value)
            self.figure.replot_traces()
            self.figure.original_trace.persist()
        except:
            pass

    def process_savgol_parameters_change(self, window_value: str) -> None:
        if self.suppress_change_processing:
            return
        try:
            assert isinstance(self.figure.original_trace.overlay, OverlaySavitzkyGolay)
            if window_value.endswith("%"):
                new_window_value = int(window_value.replace("%", "").strip())
                self.figure.original_trace.overlay.set_window_length(
                    f"{new_window_value}%")  # pyright: ignore [reportAttributeAccessIssue]
            else:
                new_window_value = int(window_value.strip())
                self.figure.original_trace.overlay.set_window_length(
                    f"{new_window_value}")  # pyright: ignore [reportAttributeAccessIssue]
            self.figure.replot_traces()
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

    def show_add_stat_function_menu(self, ev: QMouseEvent):
        p = self.add_function_label.mapToGlobal(ev.pos())
        menu = QMenu()
        menu.addAction("min")
        menu.addAction("max")
        menu.addAction("range")
        menu.addAction("mean")
        menu.addAction("stdev")
        action = menu.exec_(p)
        if action is not None:
            new_labels = [sfl for sfl in self.stat_func_labels if sfl.fname != action.text()]
            new_labels.append(StatFuncLabel(action.text(), self.remove_stat_function))
            for sfl in self.stat_func_labels:
                self.functions_panel.layout().removeWidget(sfl)
                sfl.setParent(None)

            self.stat_func_labels.clear()
            for i, sfl in enumerate(new_labels):
                self.functions_panel.layout().insertWidget(i + 1, sfl)
                self.stat_func_labels.append(sfl)
            self.figure.set_stat_functions([sfl.fname for sfl in new_labels])

    def remove_stat_function(self, sfl: StatFuncLabel) -> None:
        self.stat_func_labels.remove(sfl)
        self.functions_panel.layout().removeWidget(sfl)
        self.figure.set_stat_functions([sfl.fname for sfl in self.stat_func_labels])
