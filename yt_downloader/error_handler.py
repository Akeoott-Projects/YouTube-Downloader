# Improved error_handler.py for handling and displaying errors

from logging_setup import log
from constants import WARNING_TITLE, ERROR_TITLE, INFO_TITLE, ISSUE_INFO_HTML

import sys
import traceback

from PyQt5.QtWidgets import QApplication, QMessageBox, QPushButton
from PyQt5.QtCore import Qt, QCoreApplication


def get_app():
    """Ensure a single QApplication instance exists."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

def format_error_details(e: Exception, location: str, context: str) -> str:
    """Format detailed error information for display and copying."""
    return (
        f"Exception: {type(e).__name__}\n"
        f"Message: {e}\n"
        f"Location: {location}\n"
        f"Context: {context}\n"
        f"Traceback:\n{traceback.format_exc()}"
    )

def error_display(
    e: Exception,
    e_type: str,
    context: str,
    location: str,
    exit_on_close: bool = True
):
    """
    Display an error/warning/info dialog to the user.
    """
    app = get_app()
    qt_box = QMessageBox()
    qt_box.setTextFormat(Qt.RichText) # type: ignore

    # Set defaults and log missing info
    if not location:
        log.warning("No location provided.")
        location = "No location provided."
    if not context:
        log.warning("No context provided.")
        context = "No context provided."

    # Set icon, title, and behavior
    if e_type == "info":
        qt_box.setIcon(QMessageBox.Information)
        title = INFO_TITLE if 'INFO_TITLE' in globals() else "Information"
        buttons = QMessageBox.Ok
        exit_on_close = False
    elif e_type == "warning":
        qt_box.setIcon(QMessageBox.Warning)
        title = WARNING_TITLE
        buttons = QMessageBox.Ok
        exit_on_close = False
    elif e_type == "error":
        qt_box.setIcon(QMessageBox.Critical)
        title = ERROR_TITLE
        buttons = QMessageBox.Close
        exit_on_close = True
    else:
        log.warning("e_type not recognized.")
        title = "Unknown Error"
        buttons = QMessageBox.Close
        exit_on_close = True

    # Main message
    message_text = (
        f"<h3 style='color:#b22222;'>{title}</h3>"
        f"<b>Type:</b> <span style='color:red;'>{e_type.capitalize()}</span><br>"
        f"<b>Context:</b> {context}<br>"
        f"<b>Location:</b> {location}<br>"
        f"<br>{ISSUE_INFO_HTML}"
    )
    qt_box.setWindowTitle(title)
    qt_box.setText(message_text)

    # Detailed error info
    details = format_error_details(e, location, context)
    qt_box.setDetailedText(details)

    # Add "Copy Details" button
    copy_btn = qt_box.addButton("Copy Details", QMessageBox.ActionRole)

    qt_box.setStandardButtons(buttons)

    # Show the dialog and handle user actions
    result = qt_box.exec_()
    if qt_box.clickedButton() == copy_btn:
        app.clipboard().setText(details) # type: ignore
        # Show dialog again for user to close
        return error_display(e, e_type, context, location, exit_on_close)
    if exit_on_close and result in (QMessageBox.Close, QMessageBox.Ok):
        QCoreApplication.quit()
        sys.exit()

def gather_info(
    e: Exception,
    e_type: str,
    context: str,
    file_name: str
):
    """
    Gather traceback info and display/log the error.
    """
    exc_type, exc_value, exc_traceback = sys.exc_info()
    frames = traceback.extract_tb(exc_traceback)
    try:
        last_frame = frames[-1]
        location = (
            f"Line: {last_frame.lineno}\n"
            f"File: {file_name}\n"
            f"Function: {last_frame.name}"
        )
        log.error(f"Handling {type(e).__name__}: {e}\n{traceback.format_exc()}")
        error_display(e, e_type, context, location, exit_on_close=(e_type == "error"))
    except IndexError:
        log.critical("No traceback available.")
        sys.exit()

if __name__ == "__main__":
    try:
        # Simulate an error for testing
        1 / 0
    except Exception as e:
        gather_info(e, "error", "Testing error handler", __file__)