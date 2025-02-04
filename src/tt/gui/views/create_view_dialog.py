from PySide6.QtWidgets import QLabel
from pytide6 import Dialog, LineTextInput, ComboBox, VBoxLayout, HBoxPanel, W, PushButton

from tt.data.view import ViewSpec
from tt.gui.app import App


class CreateNewView(Dialog):
    def __init__(self, parent, app: App):
        super().__init__(parent, windowTitle = "Create New View", modal = True)

        self.num_rows: int = 1

        def set_num_rows(num_rows: str):
            self.num_rows = int(num_rows)

        self.num_columns: int = 1

        def set_num_columns(num_columns: str):
            self.num_columns = int(num_columns)

        self.view_name = ""

        def set_view_name(view_name: str):
            self.view_name = view_name

        def create_view():
            assert app.project is not None
            vname = self.view_name.strip()
            if vname in app.project.views.get_view_spec_names():
                app.show_error("View with this name already exists")
            elif vname.strip() == "":
                app.show_error("Please enter a valid view name")
            else:
                app.project.views.add_view_spec(ViewSpec(
                    name = vname, num_rows = self.num_rows, num_columns = self.num_columns, title = vname
                ))
                app.notify_views_require_change()
                self.close()
                app.edit_view(vname)

        self.setLayout(VBoxLayout(
            widgets = [
                LineTextInput("View Name", text = self.view_name, min_width = 300, on_text_change = set_view_name),
                HBoxPanel([
                    QLabel("Rows × Columns : "),
                    ComboBox(
                        items = ["1", "2", "3", "4", "5"],
                        current_selection = f"{self.num_rows}",
                        on_text_change = set_num_rows
                    ),
                    QLabel("×"),
                    ComboBox(
                        items = ["1", "2", "3", "4", "5"],
                        current_selection = f"{self.num_columns}",
                        on_text_change = set_num_columns
                    ),
                    W(HBoxPanel(), stretch = 1)
                ]),
                HBoxPanel([
                    W(HBoxPanel(), stretch = 1),
                    PushButton("Ok", on_clicked = create_view, auto_default = True),
                    PushButton("Cancel", on_clicked = lambda: self.close())
                ])
            ]
        ))


def mk_create_new_view(parent, app: App):
    def create_new_view():
        cview = CreateNewView(parent, app)
        cview.exec()

    return create_new_view
