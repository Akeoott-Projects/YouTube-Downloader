# main.py is there to excecute the entire program!

# lib and error handle imports
from constants import PROGRAM_VERSION
from logging_setup import log
from error_handler import gather_info

import sys
import os

try: # Application file imports
    from user_input import YouTubeDownloaderGUI
    from downloader import DownloadYT

except ImportError as e:
    log.error(f"Failed to import necessary modules: {e}")
    gather_info(e, "error", "Module failed to load", __file__)
    sys.exit(1)

def main():
    log.info(f"Starting YouTube Downloader Application (Version: {PROGRAM_VERSION})")

    gui = YouTubeDownloaderGUI()
    video_url, download_format, resolution, video_title = gui.get_inputs()

    # if all True: will start download.
    if video_url and download_format and resolution:
        log.info("User inputs successfully gathered from GUI.\n" \
        f"  Video URL: {video_url}\n" \
        f"  Download Format: {download_format}\n" \
        f"  Selected Quality/Resolution: {resolution}")

        if video_title is None:
            video_title = "could-not-retrive-title"

        download_info: list[str] = [video_url, download_format , resolution, video_title]

        DownloadYT(download_info)

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