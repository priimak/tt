from typing import override, Any

from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex, QPersistentModelIndex, QRect
from PySide6.QtGui import QContextMenuEvent
from PySide6.QtWidgets import QTableView, QHeaderView, QAbstractItemView, QMenu, QMessageBox
from pytide6 import VBoxPanel, Dialog, PushButton, VBoxLayout, RichTextLabel, HBoxPanel, W, LineTextInput

from tt.data.view import ViewSpec
from tt.gui.app import App
from tt.gui.views.view_window import ViewWindow


class ViewNameChangeDialog(Dialog):
    def __init__(self, parent, app: App, view_spec: ViewSpec):
        super().__init__(parent, windowTitle = "Change trace label", modal = True)

        view_name_input = LineTextInput(None, view_spec.name)

        def on_ok():
            assert app.project is not None
            new_view_name = view_name_input.text().strip()
            if new_view_name == view_spec.name:
                self.close()
            elif new_view_name == "":
                app.show_error("Please enter a trace label")
            elif new_view_name in app.project.views.get_view_spec_names():
                app.show_error("View with this name already exists. Please pick a different name.")
            else:
                view_spec.name = new_view_name
                self.close()

        ok_button = PushButton("Ok", on_clicked = on_ok)
        self.setLayout(VBoxLayout([
            RichTextLabel(f"Change name for view <em>{view_spec.name}</em>"),
            view_name_input,
            HBoxPanel([W(HBoxPanel(), stretch = 1), ok_button, PushButton("Cancel", on_clicked = self.close)])
        ]))


class ViewsFrameModel(QAbstractTableModel):
    def __init__(self, app: App):
        super().__init__()
        self.app = app

    @override
    def headerData(self, section: int, orientation: Qt.Orientation, role = ...) -> Any:
        return "View"

    @override
    def rowCount(self, parent = ...) -> int:
        if self.app.project is None:
            return 0
        else:
            return len(self.app.project.views.get_view_spec_names())

    @override
    def columnCount(self, parent = ...) -> int:
        return 1

    @override
    def data(self, index: QModelIndex | QPersistentModelIndex, role: int = 1) -> Any:
        if role == Qt.ItemDataRole.DisplayRole and self.app.project is not None:
            return self.app.project.views.get_view_spec_names()[index.row()]
        else:
            return None


class ViewsView(QTableView):
    def __init__(self, parent, app: App):
        super().__init__(parent)
        self.app = app
        self.table_model = ViewsFrameModel(app)
        self.setModel(self.table_model)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.doubleClicked.connect(self.render_view)

    def render_view(self) -> ViewWindow:
        selection = self.selectedIndexes()
        view_name = self.table_model.data(selection[0], Qt.ItemDataRole.DisplayRole)
        main_window = self.app.main_window()
        main_window_geometry = main_window.geometry()
        win = ViewWindow(main_window, self.app, view_name)
        win.show()
        figure_geometry: QRect = win.geometry()

        win.move(
            main_window_geometry.center().x() - int(figure_geometry.width() / 2),
            main_window_geometry.center().y() - int(figure_geometry.height() / 2)
        )
        main_window.app.register_window(win)  # pyright: ignore [reportAttributeAccessIssue]
        return win

    def edit_view(self):
        self.render_view().show_config_dialog.emit()

    @override
    def contextMenuEvent(self, arg__1: QContextMenuEvent) -> None:
        menu = QMenu(self)

        menu.addAction("Show View", self.render_view)
        menu.addAction("Rename View", self.rename_view)
        menu.addAction("Edit View", self.edit_view)
        menu.addAction("Delete View", self.delete_view)
        menu.popup(arg__1.globalPos())

    def rename_view(self) -> None:
        selection = self.selectedIndexes()
        view_name = self.table_model.data(selection[0], Qt.ItemDataRole.DisplayRole)
        assert self.app.project is not None
        view_spec: ViewSpec | None = self.app.project.views.get_view_spec(view_name)
        if view_spec is not None:
            ViewNameChangeDialog(self, app = self.app, view_spec = view_spec).exec()
            self.table_model.layoutChanged.emit()
            self.resizeColumnsToContents()

    def delete_view(self) -> None:
        selection = self.selectedIndexes()
        view_name = self.table_model.data(selection[0], Qt.ItemDataRole.DisplayRole)
        ret = QMessageBox.question(self, f"Delete view [{view_name}]?", f"Delete view [{view_name}]?",
                                   QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No)
        if ret == QMessageBox.StandardButton.Yes:
            assert self.app.project is not None
            self.app.project.views.delete_view(view_name)
            self.table_model.layoutChanged.emit()
            self.resizeColumnsToContents()


class ViewsPanel(VBoxPanel):
    def __init__(self, app: App):
        super().__init__(margins = 0)
        self.app = app
        self.views_view = ViewsView(self, app)
        self.views_view.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.views_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.layout().addWidget(self.views_view)
        parent_change = app.notify_views_require_change

        def notifier():
            parent_change()
            self.views_view.table_model.layoutChanged.emit()
            self.views_view.resizeColumnsToContents()

        app.notify_views_require_change = notifier

        def show_edit_view(view_name: str) -> None:
            assert self.app.project is not None
            row = self.app.project.views.get_view_spec_names().index(view_name)
            self.views_view.selectRow(row)
            self.views_view.edit_view()

        app.edit_view = show_edit_view
