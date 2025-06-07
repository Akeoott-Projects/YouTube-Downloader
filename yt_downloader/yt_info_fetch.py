# yt_info_fetch.py is there to fetch information such as resolution, audio quality and format.
YT_INFO_FETCH_FILE_VERSION = "1.0.0"

import yt_dlp
from logging_setup import log

def fetch_youtube_video_info(url: str):
    """
    Fetches available audio qualities and video resolutions for a given YouTube URL using yt-dlp.

    Args:
        url (str): The YouTube video URL.

    Returns:
        tuple: (success (bool), audio_qualities (list), video_resolutions (list), error_message (str))
    """
    log.info(f"Attempting to fetch video info for: {url}")

    audio_qualities = []
    video_resolutions = []
    error_message = ""

    try:
        # Options for fetching all available formats without downloading
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best', # Prioritize mp4 for video, m4a for audio
            'listformats': True,
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False) # Only extract info, don't download

            if 'entries' in info_dict: # Handle playlists/channels                              # type: ignore
                info_dict = info_dict['entries'][0] # Take the first video if it's a playlist   # type: ignore

            formats = info_dict.get('formats', [])  # type: ignore

            for f in formats:
                # Audio qualities (check for audio-only streams and bitrate)
                if f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                    abr = f.get('abr') # Average bitrate in kbps
                    if abr:
                        audio_qualities.append(f"{int(abr)}kbps")

                # Video resolutions (check for video streams, preferably with audio if 'best' is used)
                # Or for separate video streams to offer maximum resolution
                if f.get('vcodec') != 'none': # It's a video stream
                    height = f.get('height')
                    ext = f.get('ext')
                    if height and ext == 'mp4': # Assuming you want MP4 video specifically
                        video_resolutions.append(f"{height}p")
                        
        # Deduplicate and sort lists
        audio_qualities = sorted(list(set(audio_qualities)), key=lambda x: int(x.replace('kbps', '')), reverse=True)
        video_resolutions = sorted(list(set(video_resolutions)), key=lambda x: int(x.replace('p', '')), reverse=True)

        return True, audio_qualities, video_resolutions, ""

    except yt_dlp.utils.DownloadError as e:
        error_message = f"DownloadError: {e}"
        log.error(f"yt-dlp DownloadError for {url}: {error_message}")
        return False, [], [], error_message
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        log.exception(f"Unexpected error fetching info for {url}: {error_message}") # Logs traceback
        return False, [], [], error_message

if False:
    if __name__ == '__main__':

        test_url_valid = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" # Rick Astley - Never Gonna Give You Up
        test_url_invalid = "https://www.youtube.com/watch?v=invalidvideoid"
        test_url_no_quality = "https://www.youtube.com/watch?v=no_quality_example"

        print(f"\n--- Testing valid URL: {test_url_valid} ---")
        success, audio, video, err = fetch_youtube_video_info(test_url_valid)
        if success:
            print(f"Success! Audio: {audio}, Video: {video}")
        else:
            print(f"Failed: {err}")

        print(f"\n--- Testing invalid URL: {test_url_invalid} ---")
        success, audio, video, err = fetch_youtube_video_info(test_url_invalid)
        if success:
            print(f"Success! Audio: {audio}, Video: {video}")
        else:
            print(f"Failed: {err}")