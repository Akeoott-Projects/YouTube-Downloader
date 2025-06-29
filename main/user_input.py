from logging_setup import log
import font_loader  

import customtkinter as ctk
from tkinter import messagebox
import threading 

from yt_info_fetch import fetch_youtube_video_info 

ROBOTO_NORMAL_FONT_TUPLE = ("Roboto", 14)
ROBOTO_TITLE_FONT_TUPLE = ("Roboto", 18, "bold")
ROBOTO_SMALL_FONT_TUPLE = ("Roboto", 12)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class YouTubeDownloaderGUI(ctk.CTk):
    """Minimal YouTube downloader GUI for user input."""
    def __init__(self):
        super().__init__()
        self.geometry("450x450")
        self.title("YouTube Downloader")

        self.video_url = ""
        self.download_format = ""
        self.resolution = ""
        self.data_ready = False

        self.available_audio_qualities = []
        self.available_video_resolutions = []

        self.container = ctk.CTkFrame(self)
        self.container.pack(pady=20, padx=60, fill="both", expand=True)

        self.page1_link_input = ctk.CTkFrame(self.container)
        self.page2_format_selection = ctk.CTkFrame(self.container)
        self.page3_quality_selection = ctk.CTkFrame(self.container)

        self.create_page1()
        self.create_page2()
        self.create_page3()

        self._show_page(self.page1_link_input)

    def create_page1(self):
        """Page for entering YouTube URL."""
        ctk.CTkLabel(self.page1_link_input, text="Enter YouTube Video URL:", font=ROBOTO_TITLE_FONT_TUPLE).pack(pady=10)

        self.url_entry = ctk.CTkEntry(self.page1_link_input, placeholder_text="e.g., https://www.youtube.com/watch?v=dQw4w9WgXcQ", width=300, font=ROBOTO_NORMAL_FONT_TUPLE)
        self.url_entry.pack(pady=12, padx=10)

        self.page1_error_label = ctk.CTkLabel(self.page1_link_input, text="", text_color="red", font=ROBOTO_NORMAL_FONT_TUPLE)
        self.page1_error_label.pack(pady=(0, 5))
        
        self.fetching_status_label = ctk.CTkLabel(self.page1_link_input, text="", text_color="grey", font=ROBOTO_SMALL_FONT_TUPLE)
        self.fetching_status_label.pack(pady=(5, 0))

        ctk.CTkButton(self.page1_link_input, text="Next", font=ROBOTO_NORMAL_FONT_TUPLE, command=self._process_url).pack(pady=10)

    def create_page2(self):
        """Page for selecting download format."""
        ctk.CTkLabel(self.page2_format_selection, text="Select Download Format:", font=ROBOTO_TITLE_FONT_TUPLE).pack(pady=10)

        ctk.CTkButton(self.page2_format_selection, text="Download MP3 (Audio)", font=ROBOTO_NORMAL_FONT_TUPLE, command=lambda: self._select_format("mp3")).pack(pady=10)
        ctk.CTkButton(self.page2_format_selection, text="Download MP4 (Video)", font=ROBOTO_NORMAL_FONT_TUPLE, command=lambda: self._select_format("mp4")).pack(pady=10)
        
        ctk.CTkButton(self.page2_format_selection, text="Back", font=ROBOTO_NORMAL_FONT_TUPLE, command=lambda: self._show_page(self.page1_link_input)).pack(pady=(20, 5))

    def create_page3(self):
        """Page for selecting quality/resolution."""
        ctk.CTkLabel(self.page3_quality_selection, text="Select Quality/Resolution:", font=ROBOTO_TITLE_FONT_TUPLE).pack(pady=10)

        self.quality_combobox = ctk.CTkComboBox(self.page3_quality_selection, values=[], width=200, font=ROBOTO_NORMAL_FONT_TUPLE)
        self.quality_combobox.pack(pady=12, padx=10)

        self.page3_error_label = ctk.CTkLabel(self.page3_quality_selection, text="", text_color="red", font=ROBOTO_NORMAL_FONT_TUPLE)
        self.page3_error_label.pack(pady=(0, 5))
        
        ctk.CTkButton(self.page3_quality_selection, text="Download", font=ROBOTO_NORMAL_FONT_TUPLE, command=self._final_download).pack(pady=10)

        ctk.CTkButton(self.page3_quality_selection, text="Back", font=ROBOTO_NORMAL_FONT_TUPLE, command=lambda: self._show_page(self.page2_format_selection)).pack(pady=(20, 5))

    def _show_page(self, page):
        # Switch visible page
        log.debug(f"Switching to page: {page._name}")
        for p in [self.page1_link_input, self.page2_format_selection, self.page3_quality_selection]:
            p.pack_forget()
        page.pack(fill="both", expand=True)
        self.page1_error_label.configure(text="")
        self.page3_error_label.configure(text="")
        self.fetching_status_label.configure(text="")

    def _process_url(self):
        # Validate and fetch video info
        url = self.url_entry.get().strip()
        if not url:
            self.page1_error_label.configure(text="URL cannot be empty.")
            log.warning("User attempted to proceed with empty URL input.")
            return
        
        if not (url.startswith("http://") or url.startswith("https://")) or "youtube.com/watch?v=" not in url:
            self.page1_error_label.configure(text="Please enter a valid YouTube URL.")
            log.warning("User entered invalid YouTube URL.")
            return

        self.video_url = url
        self.page1_error_label.configure(text="")

        self.fetching_status_label.configure(text="Fetching video information... Please wait.")
        self.update_idletasks()

        threading.Thread(target=self._fetch_video_info_thread, args=(url,)).start()

    def _fetch_video_info_thread(self, url: str):
        # Run info fetch in background
        success, video_title, audio_qualities, video_resolutions, e = fetch_youtube_video_info(url)  
        self.after(0, self._after_fetch_video_info_callback, success, video_title, audio_qualities, video_resolutions, e)

    def _after_fetch_video_info_callback(self, success: bool, video_title: str, audio_qualities: list, video_resolutions: list, e):
        # Handle info fetch result
        self.fetching_status_label.configure(text="")

        if not success:
            self.page1_error_label.configure(text=f"Error fetching video info: {e}")
            log.error(f"Failed to fetch video info for {self.video_url}: {e}")
            messagebox.showerror("Video Info Error", f"Could not retrieve video information:\n{e}", parent=self)
            return

        self.available_audio_qualities = audio_qualities
        self.available_video_resolutions = video_resolutions
        self.video_title_val = video_title
        
        log.info(f"Video title: {video_title}")
        log.info(f"Available audio qualities: {self.available_audio_qualities}")
        log.info(f"Available video resolutions: {self.available_video_resolutions}")

        self._show_page(self.page2_format_selection)

    def _select_format(self, format_type: str):
        # Store format and update quality options
        self.download_format = format_type
        log.info(f"Selected format: {self.download_format}")

        if self.download_format == "mp3":
            if not self.available_audio_qualities:
                self.page3_error_label.configure(text="No audio qualities found for this video.")
                self.quality_combobox.set("No qualities available")
                self.quality_combobox.configure(values=["No qualities available"])
            else:
                self.quality_combobox.configure(values=self.available_audio_qualities)
                self.quality_combobox.set(self.available_audio_qualities[0]) 
        elif self.download_format == "mp4":
            if not self.available_video_resolutions:
                self.page3_error_label.configure(text="No video resolutions found for this video.")
                self.quality_combobox.set("No resolutions available")
                self.quality_combobox.configure(values=["No resolutions available"])
            else:
                self.quality_combobox.configure(values=self.available_video_resolutions)
                self.quality_combobox.set(self.available_video_resolutions[0]) 
        
        self._show_page(self.page3_quality_selection)

    def _final_download(self):
        # Validate and finalize selection
        selected_quality = self.quality_combobox.get().strip()

        if not selected_quality or selected_quality in ["No qualities available", "No resolutions available"]:
            self.page3_error_label.configure(text="Please select a valid quality/resolution.")
            log.warning("User attempted to download without selecting a valid quality/resolution.")
            return

        self.resolution = selected_quality
        self.data_ready = True
        log.info(f"Final selection - Format: {self.download_format}, Quality: {self.resolution}")
        self.destroy()

    def get_inputs(self):
        """Show GUI and return user input or None if cancelled."""
        self.mainloop()

        if not self.data_ready:
            log.info("GUI was closed or inputs were not finalized by the user. Exiting.")
            return None, None, None, None
        
        self.video_title = getattr(self, 'video_title_val', None)

        log.debug(
            f"Returning from GUI:\n"
            f"Video URL: {self.video_url}\n"
            f"Format: {self.download_format}\n"
            f"Quality/Resolution: {self.resolution}\n"
            f"Video Title: {self.video_title}"
        )
        return self.video_url, self.download_format, self.resolution, self.video_title

if __name__ == "__main__":
    # Run GUI if executed directly
    app_gui = YouTubeDownloaderGUI()
    video_url, download_format, resolution, video_title = app_gui.get_inputs()

    if video_url and download_format and resolution:
        print("\n--- Download Details ---")
        print(f"Video URL: {video_url}")
        print(f"Download Format: {download_format}")
        print(f"Selected Quality/Resolution: {resolution}")
        print(f"Video Title: {video_title}")
    else:
        print("\nGUI was closed or inputs were not finalized.")