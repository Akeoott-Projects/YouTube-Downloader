import os
import sys
import ctypes
import tkinter as tk
import tkinter.font as tkfont

from error_handler import gather_info
from logging_setup import log


# Get absolute path to resource (handles PyInstaller and dev mode)
def _resource_path(relative_path):
    try:
        base_path = sys._MEIPASS # type: ignore
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Load a font for use in the application (cross-platform)
def load_application_font(font_path="assets/Roboto-VariableFont_wdth,wght.ttf"):
    path = _resource_path(font_path)
    if not os.path.exists(path):
        log.warning(f"Font file not found: {font_path}")
        gather_info(FileNotFoundError(font_path), "warning", f"Font file not found: {font_path}. Reinstalling the program is recommended.", __file__)
        return False

    try:
        if sys.platform.startswith("win"):
            # Windows: use AddFontResourceExW
            try:
                FR_PRIVATE = 0x10
                result = ctypes.windll.gdi32.AddFontResourceExW(path, FR_PRIVATE, 0) # type: ignore
                if result == 0:
                    log.warning(f"Failed to load font: {font_path}. AddFontResourceExW returned 0.")
                    gather_info(Exception("AddFontResourceExW returned 0"), "warning", f"Failed to load font: {font_path}. AddFontResourceExW returned 0. Please retry or reinstall this program. THIS PROGRAM WILL ATTEMPT TO CONTINUE!", __file__)
                    return False
                else:
                    log.info(f"Successfully loaded font: {font_path}")
                    return True
            except Exception as e:
                log.error(f"Error loading font on Windows: {e}")
                gather_info(e, "warning", f"Error occurred while loading font {font_path} on Windows.", __file__)
                return False
        else:
            # macOS/Linux: try referencing font with Tkinter
            try:
                root = tk.Tk()
                root.withdraw()
                try:
                    tkfont.Font(root=root, family="Roboto")
                    log.info(f"Successfully referenced system font: Roboto (from {font_path})")
                    root.destroy()
                    return True
                except tk.TclError as e:
                    log.warning(f"TclError referencing font with Tkinter: {e}")
                    gather_info(e, "warning", f"TclError occurred while referencing font Roboto with Tkinter.<br>Ensure 'Roboto' font is installed on your system.", __file__)
                    root.destroy()
                    return False
                except Exception as e:
                    log.warning(f"Unexpected error referencing font with Tkinter: {e}")
                    gather_info(e, "warning", f"Unexpected error occurred while referencing font Roboto with Tkinter.", __file__)
                    root.destroy()
                    return False
            except ImportError as e:
                log.warning(f"tkinter or tkinter.font could not be imported: {e}")
                gather_info(e, "warning", f"tkinter or tkinter.font could not be imported while loading font<br>{font_path}.", __file__)
                return False
    except Exception as e:
        log.warning(f"Error loading font: {font_path} - {e}")
        gather_info(e, "warning", f"A {type(e).__name__} unexpectedly occurred.<br>Error loading font {font_path}", __file__)
    return False


# Global flag for font loading status
_font_loaded_successfully = False


# Automatically load font on module import
if not _font_loaded_successfully:
    _font_loaded_successfully = load_application_font("assets/Roboto-VariableFont_wdth,wght.ttf")