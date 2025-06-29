"""
logging_setup.py

Configures the main logger for the YouTube Downloader application using the akeoott_logging_config library (custom logging library by Akeoott).

- Uses LogConfig to create a logger named 'main'.
- Logging is activated, printed to console, and saved to 'yt_downloader_logs.log' in the current directory.
- Log level is set to DEBUG, with detailed formatting including line number, filename, and function name.
- Log file is overwritten on each run (mode 'w').

See akeoott_logging_config.LogConfig and its setup() method for more details.
"""

from akeoott_logging_config import LogConfig
import logging

def setup_main_logger():
    log_main = LogConfig(logger_name="main")
    log_main.setup(
        activate_logging=True,
        print_log=True,
        save_log=True,
        log_file_path=None,
        log_file_name="yt_downloader_logs.log",
        log_level=logging.DEBUG,
        log_format='%(levelname)s (%(asctime)s.%(msecs)03d)     %(message)s [Line: %(lineno)d in %(filename)s - %(funcName)s]',
        date_format='%Y-%m-%d %H:%M:%S',
        log_file_mode='w'
    )
    return log_main.logger

log = setup_main_logger()