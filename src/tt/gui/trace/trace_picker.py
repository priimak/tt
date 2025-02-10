from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QTableWidget, QAbstractItemView, QHeaderView, QTableWidgetItem, QLabel, QLineEdit
from pytide6 import Dialog, VBoxLayout, HBoxPanel, W, PushButton

from tt.gui.app import App


class FilterLineEdit(QLineEdit):
    def keyPressEvent(self, arg__1: QKeyEvent):
        if arg__1.key() == Qt.Key.Key_Escape:
            self.setText("")
        else:
            super().keyPressEvent(arg__1)


class TracePicker(Dialog):
    def __init__(self, parent, app: App, selected_trace_callback: Callable[[str], None]):
        super().__init__(parent, windowTitle = "Pick Trace")

        trace_table = QTableWidget(self)
        trace_table.setMinimumWidth(310)
        trace_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        trace_table.verticalHeader().setVisible(False)
        trace_table.horizontalHeader().setVisible(False)
        trace_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        trace_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        trace_table.setColumnCount(1)

        project = app.project
        assert project is not None

        traces = project.traces(version = -1)
        trace_table.setRowCount(len(traces))
        trace_lables = []

        for i, trace in enumerate(traces):
            item = QTableWidgetItem(trace.label)
            trace_table.setItem(i, 0, item)
            trace_lables.append(trace.label.lower())

        def select_and_close() -> None:
            items = trace_table.selectedItems()
            if items != []:
                trs = project.traces(-1, trace_name = trace_table.currentItem().text())
                if trs != []:
                    selected_trace_callback(trs[0].label)
            self.close()

        trace_table.doubleClicked.connect(select_and_close)

        def filter_list(filter: str):
            filter_lower = filter.strip().lower()
            for i, label in enumerate(trace_lables):
                if filter_lower in label:
                    trace_table.showRow(i)
                else:
                    trace_table.hideRow(i)

        filter_input = FilterLineEdit("")
        filter_input.textChanged.connect(filter_list)

        self.setLayout(VBoxLayout([
            QLabel(f"Pick Trace"),
            filter_input,
            trace_table,
            HBoxPanel([
                W(HBoxPanel(), stretch = 1),
                PushButton("Ok", on_clicked = select_and_close),
                PushButton("Cancel", on_clicked = lambda: self.close())
            ]),
        ]))
        filter_input.setFocus()


def mk_show_trace_picker(parent, app: App, selected_trace_callback: Callable[[str], None]):
    def __show_trace_picker():
        win = TracePicker(parent, app, selected_trace_callback)
        win.exec()

    return __show_trace_picker
