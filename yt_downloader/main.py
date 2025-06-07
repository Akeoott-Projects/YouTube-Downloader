# main.py is there to excecute the entire program!
MAIN_FILE_VERSION = "1.0.0"

# lib and error handle imports
from error_handler import gather_info
from logging_setup import log
import sys

import os

try: # Application file imports
    from user_input import YouTubeDownloaderGUI

except ImportError as e:
    log.error(f"Failed to import necessary modules: {e}")
    gather_info(e=e, e_type="error", context="Module failed to load", file_name="main.py")
    sys.exit(1)

def main():
    log.info(f"Starting YouTube Downloader Application (Version: {MAIN_FILE_VERSION})")

    gui = YouTubeDownloaderGUI()
    video_url, download_format, quality_resolution = gui.get_inputs()

    if video_url and download_format and quality_resolution:
        log.info("User inputs successfully gathered from GUI.")
        log.info(f"  Video URL: {video_url}")
        log.info(f"  Download Format: {download_format}")
        log.info(f"  Selected Quality/Resolution: {quality_resolution}")
    else:
        log.info("GUI was closed or inputs were not finalized by the user. Exiting.")
        # You might want to show a final message to the user here
        sys.exit(0)

    log.info("Application finished.")

if __name__ == "__main__":
    # Ensure this block is executed only when main.py is run directly
    try:
        main()
    except Exception as e:
        log.critical(f"An unhandled critical error occurred: {e}", exc_info=True)
        # If gather_info can handle critical unhandled exceptions, call it here
        gather_info(e=e, e_type="error", context="An unhandled critical error occurred", file_name="main.py")
        sys.exit(1) # Exit with error code