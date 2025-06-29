# downloader.py for downloading YouTube files

import os
import sys
import tkinter as tk
from tkinter import messagebox as msgbox
from tkinter import filedialog
import tkinter.ttk as ttk
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
        Initializes the downloader with video/audio info.

        Args:
            download_info (list[str]): [video_url, download_format, resolution, video_title]
        """
        log.info(f"DownloadYT initialized with info: {download_info}")
        self.video_url = download_info[0]
        self.download_format = download_info[1]
        self.resolution = download_info[2]
        self.video_title = download_info[3]
        self.directory = None

    def run(self):
        """
        Selects and runs the appropriate download method based on format and resolution.
        """
        if not self.video_title:
            log.error("Video title is empty. Aborting.")
            msgbox.showerror(title=ERROR_TITLE, message="Video title cannot be empty.")
            sys.exit(1)

        if self.download_format == "mp4":
            if self.resolution and self.resolution[-1:] == "p":
                self._download('mp4', quality=''.join(filter(str.isdigit, self.resolution)), best=False)
            else:
                self._download('mp4', best=True)
        elif self.download_format == "mp3":
            if self.resolution and self.resolution[-4:] == "kbps":
                self._download('mp3', quality=''.join(filter(str.isdigit, self.resolution)), best=False)
            else:
                self._download('mp3', best=True)
        else:
            try:
                raise ValueError(f"Download format not in range of 'mp4' or 'mp3'. Format: {self.download_format}")
            except ValueError as e:
                log.error(f"An error occurred while determining what download format to select: {self.download_format}")
                gather_info(e, "error", f"An error occurred while determining what download format to select: {self.download_format}", __name__)

    def _show_progress_window(self):
        self._progress_root = tk.Tk()
        self._progress_root.title("Downloading...")
        self._progress_root.geometry("400x120")
        self._progress_root.resizable(False, False)
        self._progress_label = tk.Label(self._progress_root, text="Preparing download...", wraplength=380, justify="center")
        self._progress_label.pack(expand=True, fill="both", padx=10, pady=(15, 5))
        self._progress_bar = ttk.Progressbar(self._progress_root, orient="horizontal", length=350, mode="determinate")
        self._progress_bar.pack(padx=20, pady=(0, 15))
        self._progress_root.update()

    def _update_progress(self, percent: float, status: str = ""): 
        if hasattr(self, '_progress_label'):
            self._progress_label.config(text=status)
        if hasattr(self, '_progress_bar'):
            self._progress_bar['value'] = percent
        if hasattr(self, '_progress_root') and self._progress_root is not None:
            self._progress_root.update_idletasks()

    def _hook(self, d):
        if d['status'] == 'downloading':
            percent = 0
            if 'total_bytes' in d and d['total_bytes']:
                percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
            elif 'total_bytes_estimate' in d and d['total_bytes_estimate']:
                percent = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
            speed = d.get('speed')
            eta = d.get('eta')
            speed_str = f" at {speed/1024/1024:.2f} MB/s" if speed else ""
            eta_str = f", ETA: {eta}s" if eta else ""
            status = f"Downloading: {percent:.1f}%{speed_str}{eta_str}"
            self._update_progress(percent, status)
        elif d['status'] == 'finished':
            self._update_progress(100, "Download complete!")

    def _download(self, fmt: str, quality: str | None = None, best: bool = False):
        """
        Generalized download method for both mp3 and mp4, with or without quality.
        """
        base_opts = {
            'outtmpl': f"{self.video_title}.%(ext)s",
            'nocheckcertificate': True,
            'no_warnings': True,
            'ignoreerrors': False,
            'logger': YTDlpLogger(),
            'progress_hooks': [self._hook],
        }
        if fmt == 'mp4':
            if best or not quality:
                base_opts.update({
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'merge_output_format': 'mp4',
                })
            else:
                base_opts.update({
                    'format': f'bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'merge_output_format': 'mp4',
                })
            cleanup_temp = True
        elif fmt == 'mp3':
            postproc = {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }
            if not (best or not quality):
                postproc['preferredquality'] = quality
            base_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [postproc],
            })
            cleanup_temp = False
        else:
            raise ValueError(f"Unsupported format: {fmt}")

        directory = self._select_directory()
        if not directory:
            sys.exit(0)
        ydl_opts = self._prepare_ydl_opts(base_opts, directory)
        self._download_with_opts(ydl_opts, cleanup_temp=cleanup_temp)
        sys.exit(0)

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
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.video_url])
        finally:
            self._close_progress_window()
            if cleanup_temp:
                # Handle both string and dict for outtmpl
                outtmpl = ydl_opts.get('outtmpl')
                if isinstance(outtmpl, dict):
                    # Use the 'default' template if available, else pick any value
                    template = outtmpl.get('default') or next(iter(outtmpl.values()))
                else:
                    template = outtmpl
                if template:
                    output_path = template.replace('%(ext)s', 'mp4')
                    self._cleanup_temp_files(output_path)

if __name__ == "__main__":
    # Example usage
    video_url: str = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    download_format: str = "mp4"
    resolution: str = "1080p"
    video_title: str = "Rick Astley - Never Gonna Give You Up (Official Video) (4K Remaster)"
    download_info: list[str] = [video_url, download_format, resolution, video_title]
    downloader = DownloadYT(download_info)
    downloader.run()