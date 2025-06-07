# error_handler.py for handeling and displaying errors
ERROR_HANDLER_FILE_VERSION = "1.0.0"

import traceback
import sys

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt

from logging_setup import log
from constants import WARNING_TITLE, ERROR_TITLE, ISSUE_INFO_HTML


def error_display(e: Exception, e_type: str, context: str, location: str):

    app = QApplication(sys.argv)
    qt_box = QMessageBox()

    if location is None:
        log.warning("No location provided.")
        location = "No location provided."

    if context is None:
        log.warning("No context provided.")
        context = "No context provided."

    if e_type == "info":
        return
    
    elif e_type == "warning":
        qt_box.setIcon(QMessageBox.Warning)
        title = WARNING_TITLE
        continue_pg = True

    elif e_type == "error":
        qt_box.setIcon(QMessageBox.Critical)
        title = ERROR_TITLE
        continue_pg = False

    else:
        log.warning("e_type not recognized.")
        title = "ERROR (Could not retrive title)"
        continue_pg = False

    # Use HTML tags for formatting
    qt_box.setWindowTitle(title)
    message_text = (
        f"<h3>An <span style='color:red;'>{e_type}</span> has ocurred</h3>"
        "Context:<br>"
        f"{context}"
    )
    qt_box.setText(message_text)
    qt_box.setTextFormat(Qt.RichText)  # type: ignore

    qt_box.setInformativeText(f"{ISSUE_INFO_HTML}<br>")
    qt_box.setDetailedText(f"{type(e).__name__}\n{location}\n\nError:\n{e}")

    if continue_pg:
        qt_box.setStandardButtons(QMessageBox.Ignore | QMessageBox.Close)
    else:
        qt_box.setStandardButtons(QMessageBox.Close)

    # Show the message box and get the result
    result = qt_box.exec_()

    if result == QMessageBox.Ignore:
        pass
    else:
        sys.exit()


def gather_info(e: Exception, e_type: str, context: str, file_name: str):
    # First two variables needed to reach 'exc_traceback'
    exc_type, exc_value, exc_traceback = sys.exc_info()
    frames = traceback.extract_tb(exc_traceback)
    try:
        last_frame = frames[-1]
        location: str = f"Line: {last_frame.lineno}\nFile: {file_name}\nFunction: {last_frame.name}"
        log.info(f"Handeling {type(e).__name__} for user display.")
        error_display(e=e, e_type=e_type, context=context, location=location)
    except IndexError as e:
        sys.exit()