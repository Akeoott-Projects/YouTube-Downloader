"""
YouTube Downloader Application

This program provides a graphical interface for downloading YouTube videos or audio in various formats and qualities. It is designed to be user-friendly and cross-platform, supporting both Windows and Linux. The application uses yt-dlp for downloading and extracting video/audio streams, and provides support for cookies to allow downloads of age-restricted or private videos.

Features:
- GUI for entering YouTube URLs, selecting format (mp3/mp4), and choosing quality/resolution.
- Fetches available audio qualities and video resolutions for the provided URL.
- Handles cookies for authenticated downloads (place 'www.youtube.com_cookies.txt' in the program directory).
- Progress window with real-time download status.
- Error handling and logging for troubleshooting.
- Supports both standalone and packaged (PyInstaller) execution.

Modules:
- user_input.py: Handles all user input and GUI interactions.
- downloader.py: Manages the download process using yt-dlp.
- yt_info_fetch.py: Fetches available formats and metadata for a given YouTube URL.
- error_handler.py: Centralized error logging and reporting.
- logging_setup.py: Configures logging for the application.
- constants.py: Stores constants such as program version and error titles.

To use:
1. Run this script (main.py) to launch the GUI.
2. Enter a YouTube URL, select format and quality, and follow prompts.
3. If a cookies file is needed, place it in the program directory as 'www.youtube.com_cookies.txt'.
4. The program will download the selected media to a user-chosen directory.
"""

from constants import PROGRAM_VERSION
from logging_setup import log
from error_handler import gather_info

import sys
import os
import tkinter as tk
from tkinter import messagebox

try:
    from user_input import YouTubeDownloaderGUI
    from downloader import DownloadYT

except ImportError as e:
    log.error(f"Failed to import necessary modules: {e}")
    gather_info(e, "error", "Module failed to load", __file__)
    sys.exit(1)

def check_and_warn_cookies():
    """Warn user if cookies file is missing and explain its purpose."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cookie_path = os.path.join(base_dir, 'www.youtube.com_cookies.txt')
    if os.path.isfile(cookie_path):
        log.info("Cookies file detected and will be used.")
        return
    log.info("No cookies file detected. Proceeding without cookies.")
    root = tk.Tk()
    root.withdraw()
    msg = (
        "To download some YouTube videos, a cookies file may be required.\n\n"
        "If you have not already done so, please place your YouTube cookies file in the same directory as this program.\n\n"
        "The file should be named 'www.youtube.com_cookies.txt'.\n\n"
        "Would you like more information?"
    )
    result = messagebox.askyesnocancel(
        title="YouTube Cookies Required (Recommended)",
        message=msg,
        icon='warning'
    )
    if result is None:
        log.info("User chose to quit at cookies warning.")
        root.destroy()
        sys.exit(0)
    elif result:
        log.info("User requested more information about cookies.")
        show_cookie_tutorial(root)
    else:
        log.info("User chose to continue without cookies.")
    root.destroy()

def show_cookie_tutorial(root=None):
    """Show a simple tutorial on how to get YouTube cookies."""
    log.info("Showing cookie tutorial to user.")
    tutorial = (
        "How to get your YouTube cookies file:\n\n"
        "1. Use a browser extension like 'Get cookies.txt' to export your YouTube cookies.\n"
        "2. Save the file as 'www.youtube.com_cookies.txt'.\n"
        "3. Place this file in the same directory as this program (the .exe file if packaged, or the main script directory if running as source).\n\n"
        "This will allow the downloader to access videos that require login or age verification."
    )
    messagebox.showinfo("How to get YouTube cookies", tutorial, parent=root)

def get_cookies_file_path():
    """Return path to cookies file if it exists, else None."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cookie_path = os.path.join(base_dir, 'www.youtube.com_cookies.txt')
    if os.path.isfile(cookie_path):
        return cookie_path
    return None

def main():
    """Main entry point for the YouTube Downloader application."""
    check_and_warn_cookies()
    log.info(f"Starting YouTube Downloader Application (Version: {PROGRAM_VERSION})")

    gui = YouTubeDownloaderGUI()
    video_url, download_format, resolution, video_title = gui.get_inputs()

    if video_url and download_format and resolution:
        log.info("User inputs successfully gathered from GUI.\n" \
        f"  Video URL: {video_url}\n" \
        f"  Download Format: {download_format}\n" \
        f"  Selected Quality/Resolution: {resolution}")

        if video_title is None:
            video_title = "could-not-retrive-title"

        download_info: list[str] = [video_url, download_format , resolution, video_title]

        DownloadYT(download_info).run()

    else:
        log.info("GUI was closed or inputs were not finalized by the user. Exiting.")
        sys.exit(0)

    log.info("Application finished.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log.critical(f"An unhandled critical error occurred: {e}", exc_info=True)
        gather_info(e, "error", "An unhandled critical error occurred", __file__)
        sys.exit(1)