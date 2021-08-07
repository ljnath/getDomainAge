import logging
from logging.handlers import RotatingFileHandler


class LogHandler:

    @staticmethod
    def get_logger(name: str, filepath: str) -> logging.Logger:
        """
        Static method to create an instance of logger.
        The logger is created and cached, if this method is called with the same logger name,
        then the previously created logger is returned

        :param name: Name of logger
        :param filepath: Complete filepath to the log file for writing log messages
        :return logger : instance of logger
        """
        logger = logging.getLogger(name)
        log_formatter = logging.Formatter(
            '%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

        logger.setLevel(logging.DEBUG)

        if not logger.hasHandlers():
            console_log_handler = logging.StreamHandler()
            console_log_handler.setFormatter(log_formatter)
            logger.addHandler(console_log_handler)

            # rotating log file every 10MB with max 10 files
            file_log_handler = RotatingFileHandler(filename=filepath, maxBytes=10 * 1024 * 1024, backupCount=10)
            file_log_handler.setFormatter(log_formatter)
            logger.addHandler(file_log_handler)
        return logger
