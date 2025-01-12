from PySide6 import QtCore
from PySide6.QtWidgets import QHBoxLayout, QSpacerItem
from pytide6 import Dialog, VBoxLayout, CheckBox, Panel
from pytide6.buttons import PushButton

from tt.gui.app import App


class SettingsDialog(Dialog):
    def __init__(self, parent, app: App):
        super().__init__(parent, windowTitle = "Settings", modal = True)

        open_last_opened_project_on_load_cb = CheckBox(
            "Automatically reopen last opened project when application starts",
            checked = app.config.get_value("open_last_opened_project_on_load", bool) or False
        )
        watch_for_source_changes_cb = CheckBox(
            "Watch source files (csv) for changes and notify user",
            checked = app.config.get_value("watch_for_source_changes", bool) or False
        )

        def on_ok():
            app.config.set_value(
                "open_last_opened_project_on_load",
                open_last_opened_project_on_load_cb.checkState() == QtCore.Qt.CheckState.Checked
            )
            app.config.set_value(
                "watch_for_source_changes",
                watch_for_source_changes_cb.checkState() == QtCore.Qt.CheckState.Checked
            )
            self.close()

        ok_button = PushButton("Ok", on_clicked = on_ok)
        self.setLayout(VBoxLayout([
            open_last_opened_project_on_load_cb,
            watch_for_source_changes_cb,
            Panel(QHBoxLayout(), [QSpacerItem, ok_button, PushButton("Cancel", on_clicked = self.close)])
        ]))
