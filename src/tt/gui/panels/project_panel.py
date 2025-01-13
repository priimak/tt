from pytide6 import VBoxPanel, RichTextLabel

from tt.gui.app import App


class ProjectPanel(VBoxPanel):
    def __init__(self, app: App):
        super().__init__(margins = 0)
        self.app = app

        self.top_label = RichTextLabel("" if app.project is None else f"<H3>Project <em>{app.project.name}</em></H3>")
        self.layout().addWidget(self.top_label)
        self.layout().addWidget(self.top_label)
