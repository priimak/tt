from PySide6.QtWidgets import QMenu, QMenuBar, QMessageBox, QWidget

from tt import __version__


class HelpMenu(QMenu):
    def __init__(self, parent: QMenuBar, about_dialog_parent: QWidget):
        super().__init__("&Help", parent)

        # In QMessageBox.about(parent = None, ...) will place message window at the center of the screen
        self.addAction(  # pyright: ignore [reportCallIssue]
            "&About",
            lambda: QMessageBox.about(
                None,  # pyright: ignore [reportArgumentType]
                "About",
                f"<html><H2>TT - <em>Trace Tool</em></H2><H4>Version: {__version__}</H4><br/>"
                "<p style=\"font-size:14px;\">The signal is the truth. The noise is what "
                "distracts us from the truth.</br>&nbsp;&nbsp;&nbsp;&nbsp;- <em>Nate Silver</em></p></html>"
            )
        )
