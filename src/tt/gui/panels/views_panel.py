from typing import override, Any

from PySide6.QtCore import QAbstractTableModel, Qt
from PySide6.QtWidgets import QTableView
from pytide6 import VBoxPanel

from tt.gui.app import App


class ViewsFrameModel(QAbstractTableModel):
    def __init__(self, app: App):
        super().__init__()
        self.app = app

    @override
    def headerData(self, section: int, orientation: Qt.Orientation, role = ...) -> Any:
        return "View Name"

    @override
    def columnCount(self, parent = ...) -> int:
        return 1


class ViewsView(QTableView):
    def __init__(self, parent, app: App):
        super().__init__(parent)
        self.app = app


class ViewsPanel(VBoxPanel):
    def __init__(self, app: App):
        super().__init__(margins = 0)
        self.app = app
