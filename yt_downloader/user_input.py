# user_input.py gets user input for selecting download
USER_INPUT_FILE_VERSION = "1.0.0"

from logging_setup import log
import customtkinter as ctk
from tkinter import messagebox
import threading # For running blocking operations in the background
from constants import ISSUE_INFO, WARNING_TITLE

# Import the new function from the separate file
from yt_info_fetch import fetch_youtube_video_info 

ROBOTO_NORMAL_FONT_TUPLE = ("Roboto", 14)
ROBOTO_TITLE_FONT_TUPLE = ("Roboto", 18, "bold")
ROBOTO_SMALL_FONT_TUPLE = ("Roboto", 12)

# CustomTkinter setup
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# --- GUI Class ---
class YouTubeDownloaderGUI(ctk.CTk):
    """
    A CustomTkinter GUI for obtaining user inputs for YouTube video downloading.
    Guides the user through link input, format selection (MP3/MP4), and quality/resolution choice.
    """
    def __init__(self):
        super().__init__()
        self.geometry("450x450")
        self.title("YouTube Downloader")

        # --- Instance variables to store inputs ---
        self.video_url_val = ""
        self.format_val = "" # "mp3" or "mp4"
        self.quality_val = "" # "320kbps" or "1080p"
        self.data_ready = False # Flag to indicate if data is ready for retrieval

        # --- Dynamic data for quality/resolution choices ---
        self.available_audio_qualities = []
        self.available_video_resolutions = []

        # --- Layout setup ---
        self.container = ctk.CTkFrame(self)
        self.container.pack(pady=20, padx=60, fill="both", expand=True)

        # --- Pages ---
        self.page1_link_input = ctk.CTkFrame(self.container)
        self.page2_format_selection = ctk.CTkFrame(self.container)
        self.page3_quality_selection = ctk.CTkFrame(self.container)

        self.create_page1()
        self.create_page2()
        self.create_page3()

        self._show_page(self.page1_link_input)

    def create_page1(self):
        """Creates widgets for the link input page."""
        ctk.CTkLabel(self.page1_link_input, text="Enter YouTube Video URL:", font=ROBOTO_TITLE_FONT_TUPLE).pack(pady=10)

        self.url_entry = ctk.CTkEntry(self.page1_link_input, placeholder_text="e.g., https://www.youtube.com/watch?v=dQw4w9WgXcQ", width=300, font=ROBOTO_NORMAL_FONT_TUPLE)
        self.url_entry.pack(pady=12, padx=10)

        self.page1_error_label = ctk.CTkLabel(self.page1_link_input, text="", text_color="red", font=ROBOTO_NORMAL_FONT_TUPLE)
        self.page1_error_label.pack(pady=(0, 5))
        
        # New "Fetching..." message label
        self.fetching_status_label = ctk.CTkLabel(self.page1_link_input, text="", text_color="grey", font=ROBOTO_SMALL_FONT_TUPLE)
        self.fetching_status_label.pack(pady=(5, 0))


        ctk.CTkButton(self.page1_link_input, text="Next", font=ROBOTO_NORMAL_FONT_TUPLE, command=self._process_url).pack(pady=10)

    def create_page2(self):
        """Creates widgets for the format selection page."""
        ctk.CTkLabel(self.page2_format_selection, text="Select Download Format:", font=ROBOTO_TITLE_FONT_TUPLE).pack(pady=10)

        ctk.CTkButton(self.page2_format_selection, text="Download MP3 (Audio)", font=ROBOTO_NORMAL_FONT_TUPLE, command=lambda: self._select_format("mp3")).pack(pady=10)
        ctk.CTkButton(self.page2_format_selection, text="Download MP4 (Video)", font=ROBOTO_NORMAL_FONT_TUPLE, command=lambda: self._select_format("mp4")).pack(pady=10)
        
        ctk.CTkButton(self.page2_format_selection, text="Back", font=ROBOTO_NORMAL_FONT_TUPLE, command=lambda: self._show_page(self.page1_link_input)).pack(pady=(20, 5))

    def create_page3(self):
        """Creates widgets for the quality/resolution selection page."""
        ctk.CTkLabel(self.page3_quality_selection, text="Select Quality/Resolution:", font=ROBOTO_TITLE_FONT_TUPLE).pack(pady=10)

        self.quality_combobox = ctk.CTkComboBox(self.page3_quality_selection, values=[], width=200, font=ROBOTO_NORMAL_FONT_TUPLE)
        self.quality_combobox.pack(pady=12, padx=10)

        self.page3_error_label = ctk.CTkLabel(self.page3_quality_selection, text="", text_color="red", font=ROBOTO_NORMAL_FONT_TUPLE)
        self.page3_error_label.pack(pady=(0, 5))
        
        ctk.CTkButton(self.page3_quality_selection, text="Download", font=ROBOTO_NORMAL_FONT_TUPLE, command=self._final_download).pack(pady=10)

        ctk.CTkButton(self.page3_quality_selection, text="Back", font=ROBOTO_NORMAL_FONT_TUPLE, command=lambda: self._show_page(self.page2_format_selection)).pack(pady=(20, 5))

    def _show_page(self, page):
        """Hides all pages and shows the selected one, clearing error messages."""
        log.debug(f"Switching to page: {page._name}")
        for p in [self.page1_link_input, self.page2_format_selection, self.page3_quality_selection]:
            p.pack_forget()
        page.pack(fill="both", expand=True)
        self.page1_error_label.configure(text="")
        self.page3_error_label.configure(text="")
        self.fetching_status_label.configure(text="") # Also clear fetching status

    def _process_url(self):
        """
        Validates the URL, displays a fetching message, and starts a thread
        to fetch video info before proceeding to format selection.
        """
        url = self.url_entry.get().strip()
        if not url:
            self.page1_error_label.configure(text="URL cannot be empty.")
            return
        
        # Basic URL validation (you might want a more robust regex here)
        if not (url.startswith("http://") or url.startswith("https://")) or "youtube.com/watch?v=" not in url:
            self.page1_error_label.configure(text="Please enter a valid YouTube URL.")
            return

        self.video_url_val = url
        self.page1_error_label.configure(text="") # Clear error

        # Display fetching message
        self.fetching_status_label.configure(text="Fetching video information... Please wait.")
        self.update_idletasks() # Force GUI update

        # Start fetching in a separate thread to keep GUI responsive
        # The _fetch_video_info_thread will call _after_fetch_video_info_callback
        threading.Thread(target=self._fetch_video_info_thread, args=(url,)).start()

    def _fetch_video_info_thread(self, url: str):
        """Runs the blocking video info fetching in a separate thread."""
        success, audio_qualities, video_resolutions, error_msg = fetch_youtube_video_info(url)  # type: ignore
        # Schedule the result processing back on the main GUI thread
        self.after(0, self._after_fetch_video_info_callback, success, audio_qualities, video_resolutions, error_msg)

    def _after_fetch_video_info_callback(self, success: bool, audio_qualities: list, video_resolutions: list, error_msg: str):
        """Callback executed on the main GUI thread after video info is fetched."""
        self.fetching_status_label.configure(text="") # Clear fetching message

        if not success:
            self.page1_error_label.configure(text=f"Error fetching video info: {error_msg}")
            log.error(f"Failed to fetch video info for {self.video_url_val}: {error_msg}")
            messagebox.showerror("Video Info Error", f"Could not retrieve video information:\n{error_msg}", parent=self)
            return

        self.available_audio_qualities = audio_qualities
        self.available_video_resolutions = video_resolutions
        
        log.info(f"Available audio qualities: {self.available_audio_qualities}")
        log.info(f"Available video resolutions: {self.available_video_resolutions}")

        self._show_page(self.page2_format_selection)


    def _select_format(self, format_type: str):
        """Stores the selected format and prepares for quality/resolution selection."""
        self.format_val = format_type
        log.info(f"Selected format: {self.format_val}")

        # Populate the quality combobox based on the selected format
        if self.format_val == "mp3":
            if not self.available_audio_qualities:
                self.page3_error_label.configure(text="No audio qualities found for this video.")
                self.quality_combobox.set("No qualities available")
                self.quality_combobox.configure(values=["No qualities available"])
            else:
                self.quality_combobox.configure(values=self.available_audio_qualities)
                # Set default to the highest quality if available
                self.quality_combobox.set(self.available_audio_qualities[0]) 
        elif self.format_val == "mp4":
            if not self.available_video_resolutions:
                self.page3_error_label.configure(text="No video resolutions found for this video.")
                self.quality_combobox.set("No resolutions available")
                self.quality_combobox.configure(values=["No resolutions available"])
            else:
                self.quality_combobox.configure(values=self.available_video_resolutions)
                # Set default to the highest resolution if available
                self.quality_combobox.set(self.available_video_resolutions[0]) 
        
        self._show_page(self.page3_quality_selection)

    def _final_download(self):
        """Validates the final selection and sets data_ready to True."""
        selected_quality = self.quality_combobox.get().strip()

        if not selected_quality or selected_quality in ["No qualities available", "No resolutions available"]:
            self.page3_error_label.configure(text="Please select a valid quality/resolution.")
            return

        self.quality_val = selected_quality
        self.data_ready = True
        log.info(f"Final selection - Format: {self.format_val}, Quality: {self.quality_val}")
        self.destroy() # Close the GUI

    def get_inputs(self):
        """
        Displays the GUI and waits for user input.
        Returns the collected inputs after the user submits the form or closes the window.

        Returns:
            A tuple containing: (video_url, format, quality_resolution).
            All elements are None if inputs are not successfully gathered (e.g., window closed).
        """
        self.mainloop() # Start the GUI interaction

        # This part executes after self.destroy() is called
        if not self.data_ready: # If window was closed without pressing Download button
            log.info("GUI closed without providing final input.")
            return None, None, None

        log.debug(
            f"Returning from GUI:\n"
            f"Video URL: {self.video_url_val}\n"
            f"Format: {self.format_val}\n"
            f"Quality/Resolution: {self.quality_val}"
        )
        return self.video_url_val, self.format_val, self.quality_val

# --- For testing standalone ---
if False:
    if __name__ == "__main__":
        app_gui = YouTubeDownloaderGUI()
        url, fmt, quality = app_gui.get_inputs()

        if url and fmt and quality:
            print("\n--- Download Details ---")
            print(f"Video URL: {url}")
            print(f"Download Format: {fmt}")
            print(f"Selected Quality/Resolution: {quality}")
            print("\nNow you would proceed with the actual download using yt-dlp!")
        else:
            print("\nGUI was closed or inputs were not finalized.")