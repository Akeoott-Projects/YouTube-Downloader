# downloader.py for downloading youtube files

# Still not finished ;-;

from logging_setup import log
from error_handler import gather_info
import yt_dlp

class DownloadYT():
    def __init__(self, download_info: list[str]):
        log.info(f"DownloadYT initialized with info: {download_info}")
        print(download_info[0])
        print(download_info[1])
        print(download_info[2])
        print(download_info[3])

    def download_video(self):
        pass

if __name__ == "__main__":

    video_url: str = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    download_format: str = "mp4"
    quality_resolution: str = "1080p"

    download_info: list[str] = [video_url, download_format , quality_resolution]

    info = DownloadYT(download_info)