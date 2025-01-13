from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLineEdit, QTextEdit, QLabel
from pytide6 import VBoxPanel, HBoxPanel, Label, Dialog, LineTextInput, VBoxLayout
from pytide6.buttons import PushButton
from pytide6.widget_wrapper import W

from tt.gui.app import App


class ChangeDTDialog(Dialog):
    def __init__(self, parent, app: App):
        super().__init__(parent, windowTitle = "Change implied dT", modal = True)

        assert app.project is not None
        implied_dt_input = LineTextInput("Implied dT", f"{app.project.implied_dt}")

        def update_dt():
            try:
                new_implied_dt_value = float(implied_dt_input.text())
                if new_implied_dt_value <= 0:
                    app.show_error("dT value cannot be 0 or negative")
                else:
                    assert app.project is not None
                    app.project.implied_dt = new_implied_dt_value
                    app.notify_project_panel_on_project_load()
                    self.close()
            except ValueError:
                app.show_error("New implied dT value is not a valid float")

        self.setLayout(VBoxLayout([
            implied_dt_input,
            HBoxPanel([
                W(HBoxPanel(), stretch = 1),
                PushButton("Ok", on_clicked = update_dt, auto_default = True),
                PushButton("Cancel", on_clicked = lambda: self.close())
            ])
        ]))


class RenameProjectDialog(Dialog):
    def __init__(self, parent, app: App):
        super().__init__(parent, windowTitle = "Rename project", modal = True)

        assert app.project is not None
        name_input = LineTextInput("Project Name", f"{app.project.name}")

        def update_name():
            assert app.project is not None
            new_name = name_input.text().strip()
            if new_name == "":
                app.show_error("New name cannot be an empty string")
            elif new_name != app.project.name:
                if new_name in app.pm.list_project_names():
                    app.show_error("Project under this name already exists")
                else:
                    app.project.name = new_name
                    app.notify_project_panel_on_project_load()
                    self.close()

        self.setLayout(VBoxLayout([
            name_input,
            HBoxPanel([
                W(HBoxPanel(), stretch = 1),
                PushButton("Ok", on_clicked = update_name, auto_default = True),
                PushButton("Cancel", on_clicked = lambda: self.close())
            ])
        ]))


class ProjectPanel(VBoxPanel):
    def __init__(self, app: App):
        super().__init__(margins = 0)
        self.app = app

        project_name_line_edit = QLineEdit("")
        project_name_line_edit.setMinimumWidth(300)
        project_name_line_edit.setEnabled(False)
        rename_project_b = PushButton(
            "Rename",
            enabled = app.project is not None,
            on_clicked = lambda: RenameProjectDialog(self, self.app).show()
        )

        project_directory_line_edit = QLineEdit("")
        project_directory_line_edit.setMinimumWidth(500)
        project_directory_line_edit.setEnabled(False)

        dt_line_edit = QLineEdit("N/A")
        dt_line_edit.setMinimumWidth(80)
        dt_line_edit.setEnabled(False)
        change_dt_b = PushButton(
            "Change Value",
            enabled = app.project is not None,
            on_clicked = lambda: ChangeDTDialog(self, self.app).show()
        )

        self.description_edit = QTextEdit("")
        self.description_edit.textChanged.connect(self.record_change_in_description)
        self.description_edit.setEnabled(False)

        self.addWidgets(
            W(
                HBoxPanel([Label("Project Name"), project_name_line_edit, rename_project_b]),
                alignment = Qt.AlignmentFlag.AlignLeft
            ),
            W(
                HBoxPanel([Label("Project Directory"), project_directory_line_edit]),
                alignment = Qt.AlignmentFlag.AlignLeft
            ),
            W(
                HBoxPanel([Label("Implied time step"), dt_line_edit, change_dt_b]),
                alignment = Qt.AlignmentFlag.AlignLeft
            ),
            VBoxPanel([QLabel("Description"), self.description_edit]),
        )

        def project_changed():
            project_name_line_edit.setText("" if app.project is None else app.project.name)
            dt_line_edit.setText("1.0" if app.project is None else f"{app.project.implied_dt}")
            rename_project_b.setEnabled(app.project is not None)
            self.description_edit.setEnabled(app.project is not None)
            change_dt_b.setEnabled(app.project is not None)

            if app.project is not None:
                self.description_edit.setText(app.project.description)
                project_directory_line_edit.setText(f"{app.project.project_dir}")
                app.set_opened_project_label(
                    f"Project <em><b>{app.project.name}</b></em> tracking file "
                    f"<em><b>{app.project.trace_source.uri()}</b></em>"
                )

        app.notify_project_panel_on_project_load = project_changed

    def record_change_in_description(self) -> None:
        if self.app.project is not None:
            self.app.project.description = self.description_edit.toPlainText()
