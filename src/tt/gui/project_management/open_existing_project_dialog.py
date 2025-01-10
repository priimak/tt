from typing import override, Any

from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from PySide6.QtWidgets import QTableView, QSpacerItem, QAbstractItemView
from pytide6 import Dialog, VBoxLayout, HBoxPanel
from pytide6.buttons import PushButton

from tt.gui.app import App


class ProjectsTableModel(QAbstractTableModel):
    def __init__(self, app: App):
        super().__init__()
        self.project_names = app.pm.list_project_names()

    @override
    def headerData(self, section: int, orientation: Qt.Orientation, role = ...) -> Any:
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return ["Project"]
        else:
            return None

    @override
    def rowCount(self, parent = ...) -> int:
        return len(self.project_names)

    @override
    def columnCount(self, parent = ...) -> int:
        return 1

    @override
    def data(self, index, role = ...):
        if role == Qt.ItemDataRole.DisplayRole:
            return self.project_names[index.row()]
        else:
            return None

    # # @override
    # def data2(self, index: QModelIndex, role: int = ...) -> Any:
    #     if role == Qt.ItemDataRole.DisplayRole:
    #         return self.project_names[index.row()]
    #     else:
    #         return None


class OpenProjectDialog(Dialog):
    def __init__(self, parent, app: App):
        super().__init__(parent, windowTitle = "Open Existing Project", modal = True)

        table_view = QTableView(self)
        table_view.horizontalHeader().setVisible(False)
        table_view.verticalScrollBar().setVisible(True)
        model = ProjectsTableModel(app)
        table_view.setModel(model)
        table_view.resizeColumnsToContents()
        table_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        def open_project_by_row(row: int):
            try:
                project_name = model.project_names[row]
                project = app.pm.open_existing_project(project_name)
                app.set_new_open_project(project)
                self.close()
            except Exception as ex:
                app.show_error(f"Failed to open project\n{ex}")

        def open_project_by_name(index: QModelIndex):
            open_project_by_row(index.row())

        table_view.doubleClicked.connect(open_project_by_name)

        def open_project():
            indexes: list[QModelIndex] = table_view.selectedIndexes()
            if indexes != []:
                open_project_by_row(indexes[0].row())

        self.setLayout(VBoxLayout([
            table_view,
            HBoxPanel([
                QSpacerItem,
                PushButton("Ok", on_clicked = open_project, auto_default = True),
                PushButton("Cancel", on_clicked = lambda: self.close())
            ])
        ]))

        self.setMinimumWidth(300)
