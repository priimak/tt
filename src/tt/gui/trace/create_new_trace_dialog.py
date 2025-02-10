from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QGridLayout, QStackedLayout, QLayoutItem
from pytide6 import Dialog, VBoxLayout, W, ComboBox, LineTextInput, HBoxPanel, PushButton, Panel

from tt.data.function import Functions
from tt.data.punits import Frequency
from tt.data.trace import Trace
from tt.gui.app import App
from tt.gui.elemental import HLine
from tt.gui.trace.trace_picker import mk_show_trace_picker


class CreateNewTraceDialog(Dialog):
    def __init__(self, parent, app: App, trace: Trace | None = None):
        super().__init__(
            parent,
            windowTitle = "Create New Derivative Trace" if trace is None else "Edit Derivative Trace",
            modal = True
        )

        project = app.project
        assert project is not None

        config_panel: Panel[QStackedLayout] = Panel(QStackedLayout())
        config_panel_layout = config_panel.layout()

        def clear_layout(layout, start_index: int):
            for _ in range(start_index, layout.count()):
                w: QLayoutItem = layout.takeAt(1)
                w.widget().setParent(None)
                layout.removeItem(w)

            layout.update()

        ################ add
        self.panel_add: Panel[QGridLayout] = Panel(QGridLayout())
        self.panel_add.setObjectName("Add")
        traces_adding = []

        def mk_delete_trace_from_adding(label: str):
            def delete_trace_from_adding():
                new_traces = [t for t in traces_adding if t.label != label]
                traces_adding.clear()
                traces_adding.extend(new_traces)
                clear_layout(self.panel_add.layout(), 1)
                build_traces_adding_layout()

            return delete_trace_from_adding

        def build_traces_adding_layout():
            for i, tr in enumerate(traces_adding):
                self.panel_add.layout().addWidget(QLabel(f"<em><b>{tr.label}</b></em>"), i + 1, 0)
                self.panel_add.layout().addWidget(
                    PushButton("Delete", on_clicked = mk_delete_trace_from_adding(tr.label)), i + 1, 1
                )

        def add_trace(label: str):
            # First, remove all elements from the layout
            clear_layout(self.panel_add.layout(), 1)

            trs = project.traces(-1, trace_name = label)
            if trs != []:
                trace = trs[0]
                new_traces = [t for t in traces_adding if t.label != label]
                new_traces.append(trace)
                traces_adding.clear()
                traces_adding.extend(new_traces)

                build_traces_adding_layout()

        self.panel_add.layout().addWidget(
            PushButton("Add Trace", on_clicked = mk_show_trace_picker(self, app, add_trace)),
            0, 0, 1, 2
        )
        config_panel_layout.addWidget(self.panel_add)

        ################ subtract
        self.panel_subtract: Panel[QGridLayout] = Panel(QGridLayout())
        self.panel_subtract.setObjectName("Subtract")

        trace_1_subtract = QLabel("")
        self.subtract_trace_1 = ""
        self.subtract_trace_2 = ""
        trace_2_subtract = QLabel("")
        self.panel_subtract.layout().addWidget(trace_1_subtract, 0, 0, 1, 2)
        self.panel_subtract.layout().addWidget(trace_2_subtract, 1, 0, 1, 2)

        def set_trace_1_subtract(label: str):
            trace_1_subtract.setText(f"<em>Trace: <b>{label}</b></em>")
            self.subtract_trace_1 = label.strip()

        def set_trace_2_subtract(label: str):
            trace_2_subtract.setText(f"<em>Trace: <b>{label}</b></em>")
            self.subtract_trace_2 = label.strip()

        self.panel_subtract.layout().addWidget(
            PushButton("Pick First Trace", on_clicked = mk_show_trace_picker(self, app, set_trace_1_subtract)), 2, 0
        )
        self.panel_subtract.layout().addWidget(
            PushButton("Pick Second Trace", on_clicked = mk_show_trace_picker(self, app, set_trace_2_subtract)), 2, 1
        )

        config_panel_layout.addWidget(self.panel_subtract)

        ############### multiply
        traces_multiplying = []

        self.panel_multiply: Panel[QGridLayout] = Panel(QGridLayout())
        self.panel_multiply.setObjectName("Multiply")

        def mk_delete_trace_from_mult(label: str):
            def delete_trace_from_mult():
                new_traces = [t for t in traces_multiplying if t.label != label]
                traces_multiplying.clear()
                traces_multiplying.extend(new_traces)
                clear_layout(self.panel_multiply.layout(), 1)
                build_traces_mult_layout()

            return delete_trace_from_mult

        def build_traces_mult_layout():
            for i, tr in enumerate(traces_multiplying):
                self.panel_multiply.layout().addWidget(QLabel(f"<em><b>{tr.label}</b></em>"), i + 1, 0)
                self.panel_multiply.layout().addWidget(
                    PushButton("Delete", on_clicked = mk_delete_trace_from_mult(tr.label)), i + 1, 1
                )

        def mult_trace(label: str):
            # First, remove all elements from the layout
            clear_layout(self.panel_multiply.layout(), 1)

            trs = project.traces(-1, trace_name = label)
            if trs != []:
                trace = trs[0]
                new_traces = [t for t in traces_multiplying if t.label != label]
                new_traces.append(trace)
                traces_multiplying.clear()
                traces_multiplying.extend(new_traces)

                build_traces_mult_layout()

        self.panel_multiply.layout().addWidget(
            PushButton("Add Trace", on_clicked = mk_show_trace_picker(self, app, mult_trace)),
            0, 0, 1, 2
        )
        config_panel_layout.addWidget(self.panel_multiply)

        ############### divide
        self.panel_divide: Panel[QGridLayout] = Panel(QGridLayout())
        self.panel_divide.setObjectName("Divide")

        trace_1_divide = QLabel("")
        self.divide_trace_1 = ""
        trace_2_divide = QLabel("")
        self.divide_trace_2 = ""
        self.panel_divide.layout().addWidget(trace_1_divide, 0, 0, 1, 2)
        self.panel_divide.layout().addWidget(trace_2_divide, 1, 0, 1, 2)

        def set_trace_1_divide(label: str):
            trace_1_divide.setText(f"<em>Trace: <b>{label}</b></em>")
            self.divide_trace_1 = label.strip()

        def set_trace_2_divide(label: str):
            trace_2_divide.setText(f"<em>Trace: <b>{label}</b></em>")
            self.divide_trace_2 = label.strip()

        self.panel_divide.layout().addWidget(
            PushButton("Pick First Trace", on_clicked = mk_show_trace_picker(self, app, set_trace_1_divide)), 2, 0
        )
        self.panel_divide.layout().addWidget(
            PushButton("Pick Second Trace", on_clicked = mk_show_trace_picker(self, app, set_trace_2_divide)), 2, 1
        )
        config_panel_layout.addWidget(self.panel_divide)

        ############### lowpass
        self.panel_lowpass: Panel[QGridLayout] = Panel(QGridLayout())
        self.panel_lowpass.setObjectName("Lowpass Filter")
        lowpass_trace_label = QLabel("")
        self.lowpass_trace = ""

        def trace_for_lowpass(label: str):
            lowpass_trace_label.setText(f"<em>Trace: <b>{label}</b></em>")
            self.lowpass_trace = label.strip()

        self.panel_lowpass.layout().addWidget(
            PushButton("Pick Trace", on_clicked = mk_show_trace_picker(self, app, trace_for_lowpass)), 0, 0
        )
        self.cutoff_freq_input = LineTextInput("Cutoff Frequency", "")
        self.panel_lowpass.layout().addWidget(self.cutoff_freq_input, 1, 0)
        self.panel_lowpass.layout().addWidget(HBoxPanel([lowpass_trace_label]))
        config_panel_layout.addWidget(self.panel_lowpass)

        def set_function_name(name: str) -> None:
            match name:
                case "Add":
                    config_panel_layout.setCurrentIndex(0)
                case "Subtract":
                    config_panel_layout.setCurrentIndex(1)
                case "Multiply":
                    config_panel_layout.setCurrentIndex(2)
                case "Divide":
                    config_panel_layout.setCurrentIndex(3)
                case "Lowpass Filter":
                    config_panel_layout.setCurrentIndex(4)

        self.help_button = app.mk_help_tool_button()

        trace_name_input = LineTextInput("Trace Name", min_width = 100)
        if trace is not None:
            trace_name_input.setText(trace.label)
            trace_name_input.setEnabled(False)

        def update_existing_trace_definition():
            assert trace is not None
            match config_panel_layout.currentWidget().objectName():
                case "Add":
                    if len(traces_adding) < 2:
                        app.show_error("Please add at least 2 traces.")
                        return
                    trace_names = [t.name for t in traces_adding]
                    project.update_derivative_trace(trace.name, Functions.Add(project, trace_names))

                case "Subtract":
                    if self.subtract_trace_1 == "":
                        app.show_error("Please enter a trace to subtract from.")
                        return
                    if self.subtract_trace_2 == "":
                        app.show_error("Please enter a trace to subtract.")
                        return
                    project.update_derivative_trace(
                        trace.name,
                        Functions.Subtract(project, [self.subtract_trace_1, self.subtract_trace_2])
                    )

                case "Multiply":
                    if len(traces_multiplying) < 2:
                        app.show_error("Please add at least 2 traces.")
                        return
                    trace_names = [t.name for t in traces_multiplying]
                    project.update_derivative_trace(trace.name, Functions.Multiply(project, trace_names))

                case "Divide":
                    if self.divide_trace_1 == "":
                        app.show_error("Please enter a dividend trace.")
                        return
                    if self.divide_trace_2 == "":
                        app.show_error("Please enter a divisor trace.")
                        return
                    project.update_derivative_trace(
                        trace.name,
                        Functions.Divide(project, [self.divide_trace_1, self.divide_trace_2])
                    )

                case "Lowpass Filter":
                    if self.lowpass_trace == "":
                        app.show_error("Please enter a trace name to filter")
                        return
                    try:
                        freq = Frequency.value_of(self.cutoff_freq_input.text())
                        project.update_derivative_trace(
                            trace.name,
                            Functions.LowpassFilter(project, [self.lowpass_trace], freq)
                        )
                    except:
                        app.show_error("Please enter a valid frequency.")
                        return

            self.close()

        def define_new_trace():
            if trace is not None:
                update_existing_trace_definition()
                return

            new_trace_name = trace_name_input.text().strip()
            if new_trace_name == "":
                app.show_error("Please enter a new trace name.")
                return

            if project.traces(-1, trace_name = new_trace_name) != []:
                app.show_error("Trace under this name already exists. Please pick another name.")
                return

            match config_panel_layout.currentWidget().objectName():
                case "Add":
                    if len(traces_adding) < 2:
                        app.show_error("Please add at least 2 traces.")
                        return
                    trace_names = [t.name for t in traces_adding]
                    project.add_derivative_trace(new_trace_name, Functions.Add(project, trace_names))
                    app.notify_tables_require_change()
                    self.close()

                case "Subtract":
                    if self.subtract_trace_1 == "":
                        app.show_error("Please enter a trace to subtract from.")
                        return
                    if self.subtract_trace_2 == "":
                        app.show_error("Please enter a trace to subtract.")
                        return
                    project.add_derivative_trace(
                        new_trace_name,
                        Functions.Subtract(project, [self.subtract_trace_1, self.subtract_trace_2])
                    )
                    app.notify_tables_require_change()
                    self.close()

                case "Multiply":
                    if len(traces_multiplying) < 2:
                        app.show_error("Please add at least 2 traces.")
                        return
                    trace_names = [t.name for t in traces_multiplying]
                    project.add_derivative_trace(new_trace_name, Functions.Multiply(project, trace_names))
                    app.notify_tables_require_change()
                    self.close()

                case "Divide":
                    if self.divide_trace_1 == "":
                        app.show_error("Please enter a dividend trace.")
                        return
                    if self.divide_trace_2 == "":
                        app.show_error("Please enter a divisor trace.")
                        return
                    project.add_derivative_trace(
                        new_trace_name,
                        Functions.Divide(project, [self.divide_trace_1, self.divide_trace_2])
                    )
                    app.notify_tables_require_change()
                    self.close()

                case "Lowpass Filter":
                    if self.lowpass_trace == "":
                        app.show_error("Please enter a trace name to filter")
                        return
                    try:
                        freq = Frequency.value_of(self.cutoff_freq_input.text())
                        project.add_derivative_trace(
                            new_trace_name,
                            Functions.LowpassFilter(project, [self.lowpass_trace], freq)
                        )
                    except:
                        app.show_error("Please enter a valid frequency.")
                        return
                    app.notify_tables_require_change()
                    self.close()

        header_title = "Create New Derivative Trace" if trace is None else "Edit Derivative Trace Definition"

        function_selector = ComboBox(items = Functions.NAMES, on_text_change = set_function_name, min_width = 150)
        if trace is not None:
            function = trace.get_function(project)
            fname = function.name()
            function_selector.setCurrentText(Functions.CONF_NAMES_2_NAME[fname])
            match fname:
                case "add":
                    for trace_name in function.source_traces:
                        add_trace(trace_name)

                case "subtract":
                    set_trace_1_subtract(function.source_traces[0])
                    set_trace_2_subtract(function.source_traces[1])

                case "multiply":
                    for trace_name in function.source_traces:
                        mult_trace(trace_name)

                case "divide":
                    set_trace_1_divide(function.source_traces[0])
                    set_trace_2_divide(function.source_traces[1])

                case "lowpass_filter":
                    trace_for_lowpass(function.source_traces[0])
                    self.cutoff_freq_input.setText(function.params()["cutoff_frequency"])

        self.setLayout(VBoxLayout([
            # W(self.help_button, alignment = Qt.AlignmentFlag.AlignRight),
            W(QLabel(header_title), stretch = 1, alignment = Qt.AlignmentFlag.AlignCenter),
            HLine(),
            trace_name_input,
            HBoxPanel([
                QLabel("Function"),
                function_selector
            ]),
            config_panel,
            HBoxPanel([
                W(HBoxPanel(), stretch = 1),
                PushButton("Ok", auto_default = True, on_clicked = define_new_trace),
                PushButton("Cancel", on_clicked = self.close)
            ])
        ]))


def mk_new_trace_dialog(parent, app: App) -> Callable[[], None]:
    def show_new_trace_dialog() -> None:
        win = CreateNewTraceDialog(parent, app)
        win.adjustSize()
        win.exec()

    return show_new_trace_dialog
