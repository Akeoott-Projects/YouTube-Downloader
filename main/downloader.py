# downloader.py for downloading YouTube files

import os
import sys
import tkinter as tk
from tkinter import messagebox as msgbox
from tkinter import filedialog
import yt_dlp
from logging_setup import log
from constants import ERROR_TITLE
from error_handler import gather_info

class YTDlpLogger:
    """
    Dummy logger for yt_dlp to suppress its output.
    """
    def debug(self, msg): pass
    def info(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass

class DownloadYT:
    """
    Handles downloading of YouTube videos or audio using yt_dlp.
    Supports both Windows and Linux ffmpeg binaries.
    """

    def __init__(self, download_info: list[str]):
        """
        Initializes the downloader with video/audio info and starts the download process.

        Args:
            download_info (list[str]): [video_url, download_format, resolution, video_title]
        """
        log.info(f"DownloadYT initialized with info: {download_info}")

        self.video_url = download_info[0]
        self.download_format = download_info[1]
        self.resolution = download_info[2]
        self.video_title = download_info[3]
        self.directory = None

        if not self.video_title:
            log.error("Video title is empty. Aborting.")
            msgbox.showerror(title=ERROR_TITLE, message="Video title cannot be empty.")
            sys.exit(1)

        # Select download method based on format and resolution
        if self.download_format == "mp4":
            if self.resolution[-1:] == "p":
                self.download_mp4()
            else:
                self.download_mp4_best_qual()
        elif self.download_format == "mp3":
            if self.resolution[-4:] == "kbps":
                self.download_mp3()
            else:
                self.download_mp3_best_qual()
        else:
            try:
                raise ValueError(f"Download format not in range of 'mp4' or 'mp3'. Format: {self.download_format}")
            except ValueError as e:
                log.error(f"An error occurred while determining what download format to select: {self.download_format}")
                gather_info(e, "error", f"An error occurred while determining what download format to select: {self.download_format}", __name__)

    def _get_ffmpeg_path(self):
        """
        Returns the path to the ffmpeg binary depending on the OS.
        Returns None if not found (yt_dlp will use system ffmpeg if available).
        Handles both normal and PyInstaller-frozen environments.
        """
        if getattr(sys, 'frozen', False):
            # Running in a PyInstaller bundle
            base_dir = sys._MEIPASS # type: ignore
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        if sys.platform.startswith("win"):
            ffmpeg_path = os.path.join(base_dir, 'ffmpeg', 'Windows', 'bin', 'ffmpeg.exe')
        elif sys.platform.startswith("linux"):
            ffmpeg_path = os.path.join(base_dir, 'ffmpeg', 'Linux', 'ffmpeg')
        else:
            ffmpeg_path = None

        if ffmpeg_path and os.path.isfile(ffmpeg_path):
            return ffmpeg_path
        else:
            return None

    def _select_directory(self) -> str | None:
        """
        Prompts the user to select a directory. Handles errors and cancellation.
        Returns the selected directory path or None if cancelled.
        """
        while True:
            try:
                root = tk.Tk()
                root.withdraw()
                directory = filedialog.askdirectory(title="Select a directory")
                root.destroy()

                if not directory:
                    return None
                if os.path.isdir(directory):
                    return directory
                else:
                    if msgbox.askretrycancel(title=ERROR_TITLE, message="Invalid path!"):
                        continue
                    else:
                        return None
            except PermissionError:
                if msgbox.askretrycancel(title=ERROR_TITLE, message="Invalid path!\nPermissionError!"):
                    continue
                else:
                    return None
            except Exception as e:
                gather_info(e, "error", f"Error selecting directory: {e}", __name__)
                return None

    def _prepare_ydl_opts(self, base_opts: dict, directory: str) -> dict:
        """
        Prepares yt_dlp options with output template and ffmpeg location.
        """
        ydl_opts = base_opts.copy()
        ydl_opts['outtmpl'] = os.path.normpath(f"{directory}/{self.video_title}.%(ext)s")
        ffmpeg_bin_path = self._get_ffmpeg_path()
        if ffmpeg_bin_path:
            ydl_opts['ffmpeg_location'] = ffmpeg_bin_path
        return ydl_opts

    def _show_progress_window(self):
        self._progress_root = tk.Tk()
        self._progress_root.title("Downloading...")
        self._progress_root.geometry("400x100")
        self._progress_root.resizable(False, False)
        label = tk.Label(self._progress_root, text="This might take a while.\nThe moment this window closes, your download should be finished.", wraplength=380, justify="center")
        label.pack(expand=True, fill="both", padx=10, pady=20)
        self._progress_root.update()

    def _close_progress_window(self):
        if hasattr(self, '_progress_root') and self._progress_root:
            self._progress_root.destroy()
            self._progress_root = None

    def _cleanup_temp_files(self, output_path):
        base, _ = os.path.splitext(output_path)
        directory = os.path.dirname(output_path)
        for ext in [".webm", ".m4a", ".f*", ".mp3", ".opus"]:
            for f in os.listdir(directory):
                if f.startswith(os.path.basename(base)) and f != os.path.basename(output_path) and f.endswith(tuple(ext.replace('*',''))):
                    try:
                        os.remove(os.path.join(directory, f))
                    except Exception:
                        pass

    def _download_with_opts(self, ydl_opts: dict, cleanup_temp: bool = False):
        """
        Runs yt_dlp with the given options to download the video/audio.
        Shows a progress window and cleans up leftover files if requested.
        """
        self._show_progress_window()
        output_path = ydl_opts['outtmpl'].replace('%(ext)s', 'mp4') if cleanup_temp else ydl_opts['outtmpl'].replace('%(ext)s', 'mp3')
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.video_url])
        finally:
            self._close_progress_window()
            if cleanup_temp:
                self._cleanup_temp_files(output_path)

    def download_mp4(self):
        """
        Downloads a YouTube video as MP4 with the specified resolution.
        """
        resolution = ''.join(filter(str.isdigit, self.resolution))
        if not resolution:
            return self.download_mp4_best_qual()

        base_opts = {
            'outtmpl': f"{self.video_title}.%(ext)s",
            'nocheckcertificate': True,
            'no_warnings': True,
            'ignoreerrors': False,
            'logger': YTDlpLogger(),
            'format': f'bestvideo[height<={resolution}]+bestaudio/best',
            'merge_output_format': 'mp4',
            'postprocessor_args': [
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-b:a', '192k',
            ],
        }

        directory = self._select_directory()
        if not directory:
            sys.exit(0)
        ydl_opts = self._prepare_ydl_opts(base_opts, directory)
        self._download_with_opts(ydl_opts, cleanup_temp=True)
        sys.exit(0)

    def download_mp4_best_qual(self):
        """
        Downloads a YouTube video as MP4 in the best available quality.
        """
        base_opts = {
            'outtmpl': f"{self.video_title}.%(ext)s",
            'nocheckcertificate': True,
            'no_warnings': True,
            'ignoreerrors': False,
            'logger': YTDlpLogger(),
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'postprocessor_args': [
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-b:a', '192k',
            ],
        }
        directory = self._select_directory()
        if not directory:
            sys.exit(0)
        ydl_opts = self._prepare_ydl_opts(base_opts, directory)
        self._download_with_opts(ydl_opts, cleanup_temp=True)
        sys.exit(0)

    def download_mp3(self):
        """
        Downloads a YouTube video as MP3 with the specified quality.
        """
        quality = ''.join(filter(str.isdigit, self.resolution))
        if not quality:
            return self.download_mp3_best_qual()

        base_opts = {
            'outtmpl': f"{self.video_title}.%(ext)s",
            'nocheckcertificate': True,
            'no_warnings': True,
            'ignoreerrors': False,
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality,
            }],
            'logger': YTDlpLogger(),
        }
        directory = self._select_directory()
        if not directory:
            sys.exit(0)
        ydl_opts = self._prepare_ydl_opts(base_opts, directory)
        self._download_with_opts(ydl_opts, cleanup_temp=False)
        sys.exit(0)

    def download_mp3_best_qual(self):
        """
        Downloads a YouTube video as MP3 in the best available quality.
        """
        base_opts = {
            'outtmpl': f"{self.video_title}.%(ext)s",
            'nocheckcertificate': True,
            'no_warnings': True,
            'ignoreerrors': False,
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }],
            'logger': YTDlpLogger(),
        }
        directory = self._select_directory()
        if not directory:
            sys.exit(0)
        ydl_opts = self._prepare_ydl_opts(base_opts, directory)
        self._download_with_opts(ydl_opts, cleanup_temp=False)
        sys.exit(0)

if __name__ == "__main__":
    # Example usage
    video_url: str = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    download_format: str = "mp4"
    resolution: str = "1080p"
    video_title: str = "Rick Astley - Never Gonna Give You Up (Official Video) (4K Remaster)"
    download_info: list[str] = [video_url, download_format, resolution, video_title]
    DownloadYT(download_info)