from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QMenuBar, QWidget

from tt.gui.app import App


class WindowsMenu(QMenu):
    def __init__(self, parent: QMenuBar, app: App):
        super().__init__("&Window", parent)

        app.register_window = self.add_window
        app.unregister_window = self.remove_window
        app.close_all_plots = self.close_all_windows

        self.win_actions: dict[str, QAction] = {}
        self.windows: dict[str, QWidget] = {}

    def get_win_id(self, win: QWidget) -> str:
        win_id_property = win.property("win_id")
        return win.windowTitle() if win_id_property is None else f"{win_id_property}"

    def add_window(self, win: QWidget) -> None:
        action: QAction = self.addAction(  # pyright: ignore [reportAssignmentType]
            win.windowTitle(), lambda: (win.raise_(), win.isMinimized() and win.showNormal())
        )
        win_id = self.get_win_id(win)
        self.win_actions[win_id] = action
        self.windows[win_id] = win

    def remove_window(self, win: QWidget) -> None:
        win_id = self.get_win_id(win)
        if win_id in self.win_actions:
            self.removeAction(self.win_actions[win_id])
            del self.windows[win_id]

    def close_all_windows(self) -> None:
        # To be called when the whole application is closing
        for win_id in list(self.windows.keys()).copy():
            self.windows[win_id].close()
