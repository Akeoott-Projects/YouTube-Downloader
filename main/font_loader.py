import os
import sys
import ctypes
import tkinter as tk
import tkinter.font as tkfont
from error_handler import gather_info
from logging_setup import log

# --- Internal Helper Functions ---
def _resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller .exe.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS    # type: ignore
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- Public Font Loading Function ---
def load_application_font(font_path="assets/Roboto-VariableFont_wdth,wght.ttf"):
    """
    Loads a font from the given path for use in the application.
    Compatible with Windows, macOS, Linux, and PyInstaller.exe.
    This function should ideally be called once at application startup.

    Args:
        font_path: The relative path to the .ttf font file.
    Returns:
        True if font loaded successfully, False otherwise.
    """
    path = _resource_path(font_path)
    if not os.path.exists(path):
        log.warning(f"Font file not found: {font_path}")
        gather_info(FileNotFoundError(font_path), "warning", f"Font file not found: {font_path}. Reinstalling the program is recommended.", __file__)
        return False

    try:
        if sys.platform.startswith("win"):
            try:
                FR_PRIVATE = 0x10
                result = ctypes.windll.gdi32.AddFontResourceExW(path, FR_PRIVATE, 0)
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
            # For macOS and Linux, try to register font with Tkinter
            try:
                # Create a temporary Tkinter root to load the font
                root = tk.Tk()
                root.withdraw() # Hide the main window

                try:
                    tkfont.Font(root=root, family="Roboto", file=path) # Use 'family' instead of 'name' for actual font name    # type: ignore
                    log.info(f"Successfully loaded font: {font_path}")
                    root.destroy()
                    return True
                except tkfont.TclError as e:    # type: ignore
                    log.warning(f"TclError registering font with Tkinter: {e}")
                    gather_info(e, "warning", f"TclError occurred while registering font {font_path} with Tkinter.", __file__)
                    root.destroy()
                    return False
                except Exception as e:
                    log.warning(f"Unexpected error registering font with Tkinter: {e}")
                    gather_info(e, "warning", f"Unexpected error occurred while registering font {font_path} with Tkinter.", __file__)
                    root.destroy()
                    return False
            except ImportError as e:
                log.warning(f"tkinter.font could not be imported: {e}")
                gather_info(e, "warning", f"tkinter.font could not be imported while loading font<br>{font_path}.", __file__)
                return False
    except Exception as e:
        log.warning(f"Error loading font: {font_path} - {e}")
        gather_info(e, "warning", f"A {type(e).__name__} unexpectedly occurred.<br>Error loading font {font_path}", __file__)
    return False

# --- Global Flag for Font Loading Status ---
_font_loaded_successfully = False

# --- Automatic Font Loading on Module Import ---
# This ensures the font is loaded once when the module is first imported.
# You can customize the font path here if it's always the same.
if not _font_loaded_successfully:
    _font_loaded_successfully = load_application_font("assets/Roboto-VariableFont_wdth,wght.ttf")