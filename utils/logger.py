import os
import logging
from logging.handlers import RotatingFileHandler

class Logger:
    def __init__(self):
        # Get the log directory from an environment variable
        log_dir = os.getenv('LOG_DIR', './storage/logs')  # Default to 'logs' if the env variable is not set
        os.makedirs(log_dir, exist_ok=True)  # Create the directory if it doesn't exist

        # Main log file for all log levels
        log_file = os.path.join(log_dir, 'app.log')
        self._setup_handler(log_file, logging.DEBUG, '[%(levelname)s] [%(asctime)s] %(message)s')

        # Separate log file for errors
        error_log_file = os.path.join(log_dir, 'error.log')
        self._setup_handler(error_log_file, logging.ERROR, '[%(levelname)s] [%(asctime)s] %(message)s')

        # Set up the logger
        self.logger = logging.getLogger('app_logger')
        self.logger.setLevel(logging.DEBUG)  # Log all levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    def _setup_handler(self, log_file, level, format):
        handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)  # 10MB per file, keep 5 backups
        formatter = logging.Formatter(format, datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        handler.setLevel(level)
        logging.getLogger('app_logger').addHandler(handler)

    def error(self, message):
        self.logger.error(message)

    def warn(self, message):
        self.logger.warning(message)

    def info(self, message):
        self.logger.info(message)

    def debug(self, message):
        self.logger.debug(message)

    def critical(self, message):
        self.logger.critical(message)
