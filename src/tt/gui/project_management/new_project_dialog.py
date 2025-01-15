from pathlib import Path

from PySide6 import QtCore
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QLabel, QLineEdit, QFileDialog
from pytide6 import Dialog, VBoxLayout, HBoxPanel, LineTextInput, HBoxLayout, Panel
from pytide6.buttons import PushButton
from pytide6.widget_wrapper import W

from tt.gui.app import App


class FilePicker(Panel[HBoxLayout]):
    def __init__(self, label: str, app: App):
        super().__init__(HBoxLayout())

        self.__file_name_line_edit = QLineEdit("")

        def pick_csv_file():
            last_opened_dir: str = app.state.get_value(
                "last_opened_dir", f"{Path.home()}"
            )  # pyright: ignore [reportAssignmentType]

            file_name, _ = QFileDialog.getOpenFileName(
                self, caption = "Open CSV File", dir = last_opened_dir, filter = "*.csv"
            )
            if file_name != "":
                self.__file_name_line_edit.setText(file_name)
                app.state.set_value("last_opened_dir", f"{Path(file_name).parent.absolute()}")

        self.addWidget(QLabel(label))
        self.csv_file_dialog_button = PushButton(
            "***", on_clicked = pick_csv_file, auto_default = False,
            style_sheet = "border: 1px solid black;",
            cursor = QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        )
        self.addWidget(HBoxPanel([self.__file_name_line_edit, self.csv_file_dialog_button], spacing = 0, margins = 0))
        self.setMinimumWidth(500)

    def file_name(self) -> str:
        return self.__file_name_line_edit.text()


class CreateNewProject(Dialog):
    def __init__(self, parent, app: App):
        super().__init__(parent, windowTitle = "Create New Project", modal = True)

        project_name_input = LineTextInput("Project Name")
        file_picker = FilePicker("Traces CSV file", app)

        def do_create_new_project():
            new_project_name = project_name_input.text()
            cvs_file_name = file_picker.file_name()
            if new_project_name.strip() == "":
                app.show_error("Please enter a project name")
            elif new_project_name in app.pm.list_project_names():
                app.show_error(f"Project named [{new_project_name}] already exists")
            elif cvs_file_name.strip() == "":
                app.show_error("Please pick csv file that contains traces")
                file_picker.csv_file_dialog_button.click()
            elif not Path(cvs_file_name).exists():
                app.show_error(f"File {cvs_file_name} does not exist")
            else:
                project = app.pm.create_new_project(new_project_name)
                project.set_trace_source_from_csv_file(Path(cvs_file_name))
                _, change_id = project.load_traces()
                app.set_reference_change_id(change_id)
                app.set_new_open_project(project)
                self.close()

        self.setLayout(VBoxLayout(
            widgets = [
                project_name_input,
                file_picker,
                HBoxPanel([
                    W(HBoxPanel(), stretch = 1),
                    PushButton("Ok", on_clicked = do_create_new_project, auto_default = True),
                    PushButton("Cancel", on_clicked = lambda: self.close())
                ])
            ]
        ))
