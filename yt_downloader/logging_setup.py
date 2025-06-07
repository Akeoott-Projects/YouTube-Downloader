# logging_setup.py for configuring logging via the akeoott_logging_config library
LOGGING_SETUP_FILE_VERSION = "1.0.0"

from akeoott_logging_config import LogConfig
import logging

def setup_main_logger():
    log_main = LogConfig(logger_name="main")
    log_main.setup(
        activate_logging=True,
        print_log=True,
        save_log=False,
        log_file_path=None,
        log_file_name="yt_downloader_logs.log",
        log_level=logging.DEBUG,
        log_format='%(levelname)s (%(asctime)s.%(msecs)03d)     %(message)s [Line: %(lineno)d in %(filename)s - %(funcName)s]',
        date_format='%Y-%m-%d %H:%M:%S',
        log_file_mode='a'
    )
    return log_main.logger

log = setup_main_logger()