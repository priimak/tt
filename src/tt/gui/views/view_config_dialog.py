from PySide6.QtCore import QAbstractItemModel, Qt, Signal
from PySide6.QtGui import QStandardItemModel, QStandardItem, QMouseEvent, QIntValidator
from PySide6.QtWidgets import QTreeView, QAbstractItemView, QFrame, QHBoxLayout, QLabel, QGridLayout, QWidget, \
    QTableWidget, QTableWidgetItem, QHeaderView, QLayoutItem
from pytide6 import Dialog, VBoxLayout, W, HBoxPanel, PushButton, Layout, ComboBox, CheckBox, VBoxPanel
from pytide6.inputs import LineEdit, LineTextInput
from typing_extensions import override

from tt.data.legends import LEGEND_LOCATIONS
from tt.data.view import SubPlot, TraceSpec, AxisLean
from tt.gui.app import App


class TModel(QAbstractItemModel):
    def __init__(self):
        super().__init__()

    def data(self, index, role = ...):
        print(index)
        return super().data(index, role)

    def columnCount(self, parent = ...):
        return 1

    def rowCount(self, parent = ...):
        return 10


def SI(text: str) -> QStandardItem:
    item = QStandardItem(text)
    item.setEditable(False)
    return item


# class ID(QAbstractItemDelegate):
#     def __init__(self, parent = None):
#         super().__init__(parent)
#
#     def setModelData(self, editor, model, index):
#         super().setModelData(editor, model, index)


class ViewConfigDialogOld(Dialog):
    def __init__(self, view_window):
        super().__init__(parent = view_window, windowTitle = f"Config for [{view_window.view_spec.name}]")
        from tt.gui.views.view_window import ViewWindow
        self.view_win: ViewWindow = view_window

        tview = QTreeView(self)
        tview.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        tview.setUniformRowHeights(True)
        tview.doubleClicked.connect(self.edit_item)

        model = QStandardItemModel()
        model.setColumnCount(2)

        model.appendRow([SI("View Name"), SI(self.view_win.view_spec.name)])
        self.title = SI(self.view_win.view_spec.title)
        # self.title.
        model.appendRow([SI("View Title"), self.title])

        model.appendRow([SI("Rows"), SI(f"{self.view_win.view_spec.num_rows}")])

        model.appendRow([SI("Columns"), SI(f"{self.view_win.view_spec.num_columns}")])

        subplots = SI("Subplots")
        model.appendRow(subplots)
        for row in range(self.view_win.view_spec.num_rows):
            for column in range(self.view_win.view_spec.num_columns):
                row_and_column_item = QStandardItem(f"{row} X {column}")
                row_and_column_item.setEditable(False)
                subplots.appendRow(row_and_column_item)

                row_and_column_item.appendRow([SI("Traces")])

        tview.setModel(model)
        tview.expandAll()

        self.setLayout(VBoxLayout([
            W(tview, stretch = 1),
            HBoxPanel([W(HBoxPanel(), stretch = 1), PushButton("Ok", on_clicked = self.close)]),
        ]))

    def edit_item(self, item):
        print(item)


class AddTraceDialog(Dialog):
    def __init__(self, parent):
        super().__init__(parent, windowTitle = "Add trace")

        # noinspection PyTypeChecker
        self.subplot_dialog: EditSubplotDialog = parent

        trace_table = QTableWidget(self)
        trace_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        trace_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        trace_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        trace_table.setColumnCount(2)
        trace_table.setHorizontalHeaderLabels(["Name", "Label"])
        assert self.subplot_dialog.app.project is not None
        traces = self.subplot_dialog.app.project.traces(version = 1)
        trace_table.setRowCount(len(traces))
        for i, trace in enumerate(traces):
            item = QTableWidgetItem(trace.name)
            trace_table.setItem(i, 0, item)
            trace_table.setItem(i, 1, QTableWidgetItem(trace.label))

        def add_trace(event: QMouseEvent):
            trace = traces[trace_table.currentRow()]
            self.subplot_dialog.subplot.remove_trace_spec(trace.name, -1)
            self.subplot_dialog.subplot.add_trace_spec(TraceSpec(
                name = trace.name, trace_version = -1, on_axis = AxisLean.LEFT, color = "auto",
                show_filtered_trace = False, show_legends = False
            ))
            self.subplot_dialog.build_traces_panel()
            self.close()

        trace_table.mouseDoubleClickEvent = add_trace

        self.setLayout(VBoxLayout([
            QLabel(f"Add trace"),
            trace_table,
            HBoxPanel([W(HBoxPanel(), stretch = 1), PushButton("Ok", on_clicked = self.close)]),
        ]))


class HLine(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)


class EditSubplotDialog(Dialog):
    def __init__(self, parent, subplot_label, subplot: SubPlot, app: App, view_conf_dialog):
        super().__init__(parent, windowTitle = f"SubPlot at (row: {subplot.row}, col: {subplot.column})")

        self.view_conf_dialog: ViewConfigDialog = view_conf_dialog
        self.subplot_label: SubplotLabel = subplot_label
        self.app = app
        self.subplot = subplot
        assert self.app.project is not None
        self.project = self.app.project

        self.traces_panel = QWidget()
        self.traces_layout = QGridLayout()
        self.traces_panel.setLayout(self.traces_layout)
        self.initial_cons = True
        self.build_traces_panel()
        self.initial_cons = False

        def update_show_grid(show_grid: bool):
            subplot.set_show_grid(show_grid)
            self.view_conf_dialog.view_win.set_grid_on_subplot(subplot.row, subplot.column)

        def update_left_axis_label(label: str):
            subplot.left_axis_label = label
            self.view_conf_dialog.view_win.update_ylabels_on_subplot(subplot.row, subplot.column)

        def update_right_axis_label(label: str):
            subplot.right_axis_label = label
            self.view_conf_dialog.view_win.update_ylabels_on_subplot(subplot.row, subplot.column)

        def update_x_axis_label(label: str):
            subplot.x_axis_label = label
            self.view_conf_dialog.view_win.update_xlabel_on_subplot(subplot.row, subplot.column)

        def update_legend_location(location: str):
            subplot.legend_location = location
            self.view_conf_dialog.view_win.update_legends_on_subplot(subplot.row, subplot.column)

        self.setLayout(VBoxLayout([
            VBoxPanel([
                LineTextInput(
                    "Left Y-Axis Label",
                    subplot.left_axis_label,
                    min_width = 100,
                    on_text_change = update_left_axis_label
                ),
                LineTextInput(
                    "Right Y-Axis Label",
                    subplot.right_axis_label,
                    min_width = 100,
                    on_text_change = update_right_axis_label
                ),
                LineTextInput(
                    "X-Axis Label",
                    subplot.x_axis_label,
                    min_width = 100,
                    on_text_change = update_x_axis_label
                ),
                CheckBox("Show Grid", checked = subplot.show_grid, on_change = update_show_grid),
                HBoxPanel(widgets = [
                    QLabel("Legends Location"),
                    ComboBox(
                        items = ["None"] + LEGEND_LOCATIONS,
                        current_selection = subplot.legend_location,
                        on_text_change = update_legend_location,
                        min_width = 150
                    ),
                    W(HBoxPanel(), stretch = 1)
                ])

            ]),
            HLine(),
            self.traces_panel,
            HBoxPanel([W(
                PushButton(
                    "+",
                    on_clicked = self.show_add_trace_dialog,
                    tool_tip = "Add another trace to subplot",
                    auto_default = False
                ),
                stretch = 1
            )]),
            HBoxPanel([W(HBoxPanel(), stretch = 1), PushButton("Ok", on_clicked = self.close, auto_default = True)]),
        ]))

    @override
    def close(self) -> bool:
        retval = super().close()
        self.subplot_label.resizeEverything()
        return retval

    def get_trace_label(self, spec: TraceSpec):
        trs = self.project.traces(-1, trace_name = spec.name)
        return spec.name if trs == [] else trs[0].label

    def build_traces_panel(self) -> None:
        # First, remove all elements from the layout
        for _ in range(self.traces_layout.count()):
            w: QLayoutItem = self.traces_layout.takeAt(0)
            w.widget().setParent(None)
            self.traces_layout.removeItem(w)

        self.traces_layout.update()

        self.traces_layout.addWidget(QLabel("<b>Trace</b>"), 0, 0)
        self.traces_layout.addWidget(QLabel("<b>Version</b>"), 0, 1)
        self.traces_layout.addWidget(QLabel("<b>Color</b>"), 0, 2)
        self.traces_layout.addWidget(QLabel("<b>On Axis</b>"), 0, 3)
        self.traces_layout.addWidget(QLabel("<b>Show Overlay</b>"), 0, 4)
        self.traces_layout.addWidget(QLabel("<b>Show Legends</b>"), 0, 5)
        self.traces_layout.addWidget(QLabel("<b>Action</b>"), 0, 6)
        self.traces_layout.setColumnStretch(7, 1)
        for row, ts in enumerate(self.subplot.get_trace_specs()):
            row += 1

            def mk_version_setter(s: TraceSpec):
                def set_version(version: str):
                    try:
                        s.trace_version = int(version)
                        self.subplot_label.update_label()
                    except ValueError:
                        pass

                return set_version

            def mk_color_setter(s: TraceSpec):
                def set_color(color: str):
                    s.color = color
                    # self.view_conf_dialog.view_win.update_legends_on_subplot(self.subplot.row, self.subplot.column)

                return set_color

            def mk_on_axis_setter(s: TraceSpec):
                def set_on_axis(axis: str):
                    s.on_axis = AxisLean.value_of(axis)

                return set_on_axis

            def mk_trace_deleter(s: TraceSpec):
                def deleter():
                    self.subplot.remove_trace_spec(s.name, s.trace_version)
                    self.build_traces_panel()

                return deleter

            def mk_filtered_setter(s: TraceSpec):
                def setter(value: bool):
                    s.show_filtered_trace = value

                return setter

            def mk_legends_setter(s: TraceSpec):
                def setter(value: bool):
                    s.show_legends = value

                return setter

            self.traces_layout.addWidget(QLabel(self.get_trace_label(ts)), row, 0)
            self.traces_layout.addWidget(
                LineEdit(
                    f"{ts.trace_version}",
                    min_width = 80, max_width = 80,
                    validator = QIntValidator(),
                    on_text_change = mk_version_setter(ts)
                ),
                row, 1
            )
            self.traces_layout.addWidget(
                ComboBox(
                    items = ["auto", "red", "green", "blue", "orange", "pink", "black"],
                    current_selection = ts.color,
                    on_text_change = mk_color_setter(ts)
                ),
                row, 2
            )
            self.traces_layout.addWidget(
                ComboBox(
                    items = ["left", "right"],
                    current_selection = ts.on_axis.value,
                    on_text_change = mk_on_axis_setter(ts)
                ),
                row, 3
            )
            self.traces_layout.addWidget(
                CheckBox(checked = ts.show_filtered_trace, on_change = mk_filtered_setter(ts)), row, 4
            )
            self.traces_layout.addWidget(
                CheckBox(checked = ts.show_legends, on_change = mk_legends_setter(ts)), row, 5
            )
            self.traces_layout.addWidget(
                PushButton("Delete", on_clicked = mk_trace_deleter(ts), auto_default = False), row, 6
            )

            self.traces_layout.update()
            self.adjustSize()

        if not self.initial_cons:
            self.subplot_label.update_label()

    def show_add_trace_dialog(self) -> None:
        AddTraceDialog(self).exec()


class SubplotLabel(QFrame):
    def __init__(self, parent, subplot: SubPlot, app: App):
        super().__init__(parent)

        self.setToolTip(f"Subplot at position ({subplot.row}, {subplot.column})")

        self.subplot = subplot

        # noinspection PyTypeChecker
        self.view_conf_dialog: ViewConfigDialog = parent
        assert self.view_conf_dialog.view_win.app.project is not None
        self.project = self.view_conf_dialog.view_win.app.project

        self.label = QLabel("+")
        self.update_label()
        self.label.setStyleSheet(
            "QLabel {border: 1px solid black;}\n"
            "QLabel::hover{ background:black; color:white; }"
        )

        def show_edit_subplot_dialog(ev: QMouseEvent) -> None:
            EditSubplotDialog(
                parent,
                subplot_label = self,
                subplot = subplot,
                app = app,
                view_conf_dialog = self.view_conf_dialog
            ).exec()

        self.label.mousePressEvent = show_edit_subplot_dialog

        self.setLayout(Layout(QHBoxLayout(), spacing = 2, margins = 2, widgets = [self.label]))

    def get_trace_label(self, spec: TraceSpec):
        trs = self.project.traces(-1, trace_name = spec.name)
        return spec.name if trs == [] else trs[0].label

    def update_label(self):
        trace_specs = self.subplot.get_trace_specs()
        if len(trace_specs) > 0:
            self.label.setText("\n".join([f"{self.get_trace_label(ts)} :: {ts.trace_version}" for ts in trace_specs]))
        else:
            self.label.setText("")

    def setText(self, text: str) -> None:
        self.label.setText(text)

    def resizeEverything(self) -> None:
        self.parent().adjustSize()  # pyright: ignore [reportAttributeAccessIssue]
        self.parent().ensurePolished()  # pyright: ignore [reportAttributeAccessIssue]
        self.parent().repaint()  # pyright: ignore [reportAttributeAccessIssue]
        self.updateGeometry()
        self.view_conf_dialog.updGeo.emit()


class ViewConfigDialog(Dialog):
    updGeo = Signal()

    def __init__(self, view_window):
        super().__init__(parent = view_window, windowTitle = f"Config for view [{view_window.view_spec.name}]")
        from tt.gui.views.view_window import ViewWindow
        self.view_win: ViewWindow = view_window

        grid_widget = QWidget()
        grid = QGridLayout()
        grid_widget.setLayout(grid)

        for row in range(self.view_win.view_spec.num_rows):
            for column in range(self.view_win.view_spec.num_columns):
                subplot: SubPlot = self.view_win.view_spec.get_subplot(row, column)
                grid.addWidget(SubplotLabel(self, subplot, self.view_win.app), row, column)

        self.setLayout(VBoxLayout([
            W(
                LineEdit(
                    view_window.view_spec.title,
                    min_width = 300,
                    on_text_change = self.view_win.set_title,
                    tooltip = "View title",
                    alignment = Qt.AlignmentFlag.AlignCenter
                ),
                alignment = Qt.AlignmentFlag.AlignCenter
            ),
            W(grid_widget, stretch = 1),
            HBoxPanel([W(HBoxPanel(), stretch = 1), PushButton("Ok", on_clicked = self.close)]),
        ]))

        self.updGeo.connect(self.childrenChanged)

    @override
    def close(self) -> bool:
        retval = super().close()
        self.view_win.replot_signal.emit()
        return retval

    def childrenChanged(self):
        self.ensurePolished()
        self.update()
        self.updateGeometry()
        self.repaint()
