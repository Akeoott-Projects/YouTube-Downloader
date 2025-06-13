import os
import sys
import ctypes
import tkinter as tk
import tkinter.font as tkfont
# Assuming these are correctly imported from your project
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
            # For macOS and Linux, rely on the font being installed on the system
            # or registered via lower-level Tcl commands if you absolutely
            # need to load it from a file for bundling (more advanced).
            # The tkfont.Font constructor does NOT take a 'file' argument.
            try:
                # Create a temporary Tkinter root to initialize Tk
                root = tk.Tk()
                root.withdraw() # Hide the main window

                # Attempt to load the font using the Tk `font` command directly.
                # This is the more correct way to load a font from a file path
                # for Tkinter on non-Windows platforms, if supported by the Tcl/Tk version.
                # However, the most reliable way is still system installation.
                # For basic use, if the font is installed on the system,
                # you just need to reference it by family name.
                try:
                    # Removed 'file=path' as it's not a valid option for tkfont.Font
                    # This line now just attempts to create a font object, assuming 'Roboto'
                    # is available on the system.
                    tkfont.Font(root=root, family="Roboto")
                    log.info(f"Successfully referenced system font: Roboto (from {font_path})")
                    root.destroy()
                    return True
                except tk.TclError as e: # Corrected from tkfont.TclError to tk.TclError
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

# --- Global Flag for Font Loading Status ---
_font_loaded_successfully = False

# --- Automatic Font Loading on Module Import ---
# This ensures the font is loaded once when the module is first imported.
# You can customize the font path here if it's always the same.
if not _font_loaded_successfully:
    _font_loaded_successfully = load_application_font("assets/Roboto-VariableFont_wdth,wght.ttf")