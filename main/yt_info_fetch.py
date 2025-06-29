# yt_info_fetch.py is there to fetch information such as resolution, audio quality and format.

import yt_dlp
from logging_setup import log
from error_handler import gather_info
import sys, os

def get_cookies_file_path():
    """Return path to cookies file if it exists, else None."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cookie_path = os.path.join(base_dir, 'www.youtube.com_cookies.txt')
    if os.path.isfile(cookie_path):
        log.debug("yt_info_fetch: Cookies file will be used.")
        return cookie_path
    log.debug("yt_info_fetch: No cookies file found.")
    return None

def fetch_youtube_video_info(url: str):
    """Fetch video title, available audio qualities, and video resolutions for a YouTube URL."""
    log.info(f"[yt_info_fetch] Fetching video info for: {url}")
    cookies_path = get_cookies_file_path()
    if cookies_path:
        log.debug("[yt_info_fetch] yt_dlp will use cookies file.")
    else:
        log.debug("[yt_info_fetch] yt_dlp will not use a cookies file.")

    video_title = ""
    audio_qualities = []
    video_resolutions = []
    e = ""

    try:
        # yt-dlp options for info extraction only
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
            'listformats': True,
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
        }
        if cookies_path:
            ydl_opts['cookiefile'] = cookies_path

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info_dict = ydl.extract_info(url, download=False)
            except yt_dlp.utils.ExtractorError as e:
                if 'cookies' in str(e).lower():
                    log.error(f"Cookies are required but not provided for {url}: {e}")
                    gather_info(e, "error", "Cookies are required for this video but none were provided. Please provide cookies.txt if needed.", __file__)
                    return False, "", [], [], "Cookies required but not provided."
                else:
                    raise

            if isinstance(info_dict, dict) and 'entries' in info_dict: # Playlist/channel
                info_dict = info_dict['entries'][0]

            video_title = info_dict.get('title', '') # type: ignore
            formats = info_dict.get('formats', []) # type: ignore

            for f in formats:
                # Audio qualities (audio-only streams)
                if f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                    abr = f.get('abr')
                    if abr:
                        audio_qualities.append(f"{int(abr)}kbps")
                # Video resolutions (video streams, mp4 only)
                if f.get('vcodec') != 'none':
                    height = f.get('height')
                    ext = f.get('ext')
                    if height and ext == 'mp4':
                        video_resolutions.append(f"{height}p")
            # Remove duplicates and sort
            audio_qualities = sorted(list(set(audio_qualities)), key=lambda x: int(x.replace('kbps', '')), reverse=True)
            video_resolutions = sorted(list(set(video_resolutions)), key=lambda x: int(x.replace('p', '')), reverse=True)

            return True, video_title, audio_qualities, video_resolutions, ""

    except yt_dlp.utils.DownloadError as e:
        log.error(f"yt-dlp DownloadError for {url}: {e}")
        gather_info(e, "error", "Could not fetch required information about the video.", __file__)
        return False, "", [], [], e
    except Exception as e:
        log.exception(f"Unexpected error fetching info for {url}: {e}")
        gather_info(e, "error", "Could not fetch required information about the video.", __file__)
        return False, "", [], [], e

if __name__ == '__main__':
    # Simple test for valid and invalid URLs
    test_url_valid = "https://www.youtube.com/watch?v=hrnASwStFec"
    test_url_invalid = "https://www.youtube.com/watch?v=invalidvideoid"

    print(f"\n--- Testing valid URL: {test_url_valid} ---")
    success, title, audio, video, e = fetch_youtube_video_info(test_url_valid)
    if success:
        print(f"Success! Title: '{title}', Audio: {audio}, Video: {video}")
    else:
        print(f"Failed: {e}")

    print(f"\n--- Testing invalid URL: {test_url_invalid} ---")
    success, title, audio, video, e = fetch_youtube_video_info(test_url_invalid)
    if success:
        print(f"Success! Title: '{title}', Audio: {audio}, Video: {video}")
    else:
        print(f"Failed: {e}")