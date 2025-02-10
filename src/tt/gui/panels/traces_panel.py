import re
from functools import cache
from typing import override, Any

from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex, QPersistentModelIndex
from PySide6.QtGui import QContextMenuEvent, QColor
from PySide6.QtWidgets import QTableView, QHeaderView, QAbstractItemView, QMenu, QSpacerItem, QMessageBox
from pytide6 import VBoxPanel, Dialog, VBoxLayout, HBoxPanel, LineTextInput, RichTextLabel
from pytide6.buttons import PushButton
from pytide6.widget_wrapper import W

from tt.data.trace import TraceState, Trace, Traces
from tt.gui.app import App
from tt.gui.trace.create_new_trace_dialog import CreateNewTraceDialog

INTERNAL_CHANGE_ID: int = 1


class SelectTracesVersionsDialg(Dialog):
    def __init__(self, parent, app: App, trace_name: str):
        super().__init__(parent, windowTitle = "Select traces version", modal = True)

        trace_versions_to_plot = LineTextInput("Pick trace versions to plot", "1,-1")

        def on_ok():
            version_str = trace_versions_to_plot.text().strip()
            try:
                assert app.project is not None
                versions = [int(vs) for vs in version_str.split(",")]
                if len([v for v in versions if v == 0]) > 0:
                    app.show_error("Trace versions start from 1.")
                    return

                all_traces: list[list[Trace]] = [app.project.traces(v, trace_name = trace_name) for v in versions]
                traces: list[Trace] = [t[0] for t in all_traces if t != []]
                self.close()
                Traces(traces).show_in_new_window(app.project)
            except ValueError:
                app.show_error("Invalid trace versions format")

        self.setLayout(VBoxLayout([
            trace_versions_to_plot,
            HBoxPanel([
                QSpacerItem, PushButton("Ok", on_clicked = on_ok), PushButton("Cancel", on_clicked = self.close)
            ])
        ]))


TRACE_LABEL_VALID_REGEX = re.compile("^[a-zA-Z0-9\\[\\]_\\-+. ]+$")


class TraceLabelChangeDialog(Dialog):
    def __init__(self, parent, app: App, trace: Trace):
        super().__init__(parent, windowTitle = "Change trace label", modal = True)

        trace_label_input = LineTextInput(None, trace.label)

        def on_ok():
            assert app.project is not None
            new_trace_label = trace_label_input.text().strip()
            if new_trace_label == "":
                app.show_error("Please enter a trace label")
            elif new_trace_label in [t.label for t in app.project.traces(-1)]:
                app.show_error("Trace with this label already exists. Please pick a different label.")
            elif TRACE_LABEL_VALID_REGEX.match(new_trace_label) is None:
                app.show_error(
                    "Trace label must contain only letters, numbers, space and \"[\", \"]\", \"_\", \"-\", \"+\", \".\"")
            else:
                trace.label = new_trace_label
                app.notify_tables_require_change()
                self.close()

        ok_button = PushButton("Ok", on_clicked = on_ok)
        self.setLayout(VBoxLayout([
            RichTextLabel(f"Change trace label for trace <em>{trace.name}</em>"),
            trace_label_input,
            HBoxPanel([W(HBoxPanel(), stretch = 1), ok_button, PushButton("Cancel", on_clicked = self.close)])
        ]))


class TracesFrameModel(QAbstractTableModel):
    DERIVATIVE_TRACE_COLOR = QColor("red")

    def __init__(self, app: App, trace_state: TraceState):
        super().__init__()
        self.app = app
        self.trace_state = trace_state

    @override
    def headerData(self, section: int, orientation: Qt.Orientation, role = ...) -> Any:
        return "Trace Label"

    @cache
    def __prc(self, pname: str, change_id: int) -> int:
        assert self.app.project is not None
        return len([t for t in self.app.project.traces(-1) if t.state == self.trace_state])

    @override
    def rowCount(self, parent = ...) -> int:
        if self.app.project is None:
            return 0
        else:
            return self.__prc(self.app.project.name, self.app.taces_views_change_id)

    @override
    def columnCount(self, parent = ...) -> int:
        return 1

    @cache
    def __data(self, project_name: str, trace_version: int, change_id: int) -> Any:
        assert self.app.project is not None
        return [t.label for t in self.app.project.traces(-1) if t.state == self.trace_state]

    @cache
    def __tdata(self, project_name: str, trace_version: int, change_id: int) -> Any:
        assert self.app.project is not None
        return [t for t in self.app.project.traces(-1) if t.state == self.trace_state]

    @override
    def data(self, index: QModelIndex | QPersistentModelIndex, role: int = 1) -> Any:
        if self.app.project is not None:
            if role == Qt.ItemDataRole.DisplayRole:
                return self.__data(
                    self.app.project.name, self.app.project.latest_traces_version, self.app.taces_views_change_id
                )[index.row()]
            elif role == Qt.ItemDataRole.ForegroundRole:
                d = self.__tdata(self.app.project.name, self.app.project.latest_traces_version,
                                 self.app.taces_views_change_id)[index.row()]
                return TracesFrameModel.DERIVATIVE_TRACE_COLOR if d.is_derivative else None
            else:
                return None


class TracesView(QTableView):
    def __init__(self, parent, app: App, trace_state: TraceState):
        super().__init__(parent)
        self.app = app
        self.trace_state = trace_state
        self.table_model = TracesFrameModel(app, trace_state)
        self.setModel(self.table_model)

    @override
    def contextMenuEvent(self, arg__1: QContextMenuEvent) -> None:
        menu = QMenu(self)

        menu.addAction("Plot latest version of the trace", self.render_latest_trace)
        menu.addAction("Plot latest and previous version of the trace", self.render_latest_and_previous_trace)
        menu.addAction("Plot specific versions of the trace", self.render_specific_versions_of_a_trace)

        menu.addSeparator()
        menu.addAction("Rename trace label", self.rename_trace)
        if self.trace_state == TraceState.ACTIVE:
            menu.addAction("Mark as inactive", self.mark_as_inactive)
        else:
            menu.addAction("Mark as active", self.mark_as_active)

        selection = self.selectedIndexes()
        if selection != [] and self.app.project is not None:
            tr = self.app.project.traces(-1, self.trace_state)[selection[0].row()]
            if tr.is_derivative:
                menu.addAction("Delete", self.delete_trace)
                menu.addAction("Edit Definition", self.edit_derivative_trace_definition)

        menu.popup(arg__1.globalPos())

    def render_latest_trace(self) -> None:
        selection = self.selectedIndexes()
        if selection != [] and self.app.project is not None:
            self.app.project.traces(-1, self.trace_state)[selection[0].row()].show_in_new_window(
                self.app.main_window(), self.app.super_parent()
            )

    def render_latest_and_previous_trace(self) -> None:
        selection = self.selectedIndexes()
        if selection != [] and self.app.project is not None:
            if self.app.project.latest_traces_version == 1:
                self.app.show_error("There is only one version for this trace. Hence previous version cannot be shown")
            else:
                trace_latest: Trace = self.app.project.traces(-1, self.trace_state)[selection[0].row()]
                trace_prev: Trace = self.app.project.traces(-2, self.trace_state)[selection[0].row()]
                Traces([trace_latest, trace_prev]).show_in_new_window(self.app.project)

    def render_specific_versions_of_a_trace(self):
        selection = self.selectedIndexes()
        if selection != [] and self.app.project is not None:
            trace_latest: Trace = self.app.project.traces(-1, self.trace_state)[selection[0].row()]
            SelectTracesVersionsDialg(self, self.app, trace_latest.name).show()

    def delete_trace(self) -> None:
        selection = self.selectedIndexes()
        if selection != [] and self.app.project is not None:
            trace = self.app.project.traces(-1, self.trace_state)[selection[0].row()]

            ret = QMessageBox.question(self, f"Delete trace {trace.label}?", f"Delete trace {trace.label}?",
                                       QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No)
            if ret == QMessageBox.StandardButton.Yes:
                self.app.project.delete_derivative_trace(trace.name)
                self.app.notify_tables_require_change()

    def edit_derivative_trace_definition(self) -> None:
        selection = self.selectedIndexes()
        if selection != [] and self.app.project is not None:
            trace = self.app.project.traces(-1, self.trace_state)[selection[0].row()]
            win = CreateNewTraceDialog(self, self.app, trace)
            win.adjustSize()
            win.exec()

    def rename_trace(self) -> None:
        selection = self.selectedIndexes()
        if selection != [] and self.app.project is not None:
            trace_label_change_dialog = TraceLabelChangeDialog(
                self,
                self.app,
                self.app.project.traces(-1, self.trace_state)[selection[0].row()]
            )
            trace_label_change_dialog.show()

    def mark_as_inactive(self) -> None:
        selection = self.selectedIndexes()
        if selection != [] and self.app.project is not None:
            self.app.project.traces(-1, TraceState.ACTIVE)[selection[0].row()].state = TraceState.INACTIVE
            self.app.notify_tables_require_change()

    def mark_as_active(self) -> None:
        selection = self.selectedIndexes()
        if selection != [] and self.app.project is not None:
            self.app.project.traces(-1, TraceState.INACTIVE)[selection[0].row()].state = TraceState.ACTIVE
            self.app.notify_tables_require_change()


class TracesPanel(VBoxPanel):
    def __init__(self, app: App, trace_state: TraceState):
        super().__init__(margins = 0)
        self.app = app
        self.traces_view = TracesView(self, app, trace_state)
        self.traces_view.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.traces_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.layout().addWidget(self.traces_view)
        parent_change = app.notify_tables_require_change

        def notifier():
            self.app.taces_views_change_id += 1
            parent_change()
            self.traces_view.table_model.layoutChanged.emit()
            self.traces_view.resizeColumnsToContents()

        app.notify_tables_require_change = notifier

        self.traces_view.doubleClicked.connect(self.traces_view.render_latest_trace)
