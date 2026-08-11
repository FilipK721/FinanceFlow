from logging import DEBUG, Formatter, StreamHandler, Handler, getLogger, Logger
from logging.handlers import RotatingFileHandler
import colorlog
import sys
from pathlib import Path

class FormatterConfig:
    @staticmethod
    def get_formatter() -> Formatter:
        """
        Creates a Formatter object that specifies a format of the logger message
        :return: A Formatter object that specifies a format of the logger message
        """
        return Formatter(
            fmt='%(asctime)-10s | %(levelname)-8s | %(filename)s:%(lineno)-4s%(funcName)20s: %(message)-20s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    @staticmethod
    def get_colored_formatter() -> Formatter:
        """
        Creates a Formatter object that specifies a format of the logger message and colors it
        :return: A Formatter object that specifies a format of the logger message and colors it
        """
        return colorlog.ColoredFormatter(
            fmt='%(asctime)-10s [%(levelname)-8s] %(filename)s:%(lineno)-4s%(funcName)20s: %(message)-20s',
            datefmt='%Y-%m-%d %H:%M:%S',
            reset=True,
            log_colors={
                'DEBUG':    'cyan',
                'INFO':     'green',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CRITICAL': 'red'
            }
        )
    

class LoggerConfig:
    """
    A custom loggers configuration
    """

    @staticmethod
    def get_console_logger(
        name: str,
        level: int = DEBUG,
        formatter: Formatter | None = None):

        """
        Creates Logger object that sends messages to the console
        :param name: logger name
        :param level: logger threshold
        :param formatter: object that specifies a format of the logger message
        :return: logger that sends messages to the console
        """
        if formatter is None:
            FormatterConfig.get_colored_formatter()

        stream_handler = LoggerConfig._get_stream_handler(formatter)
        return LoggerConfig._get_logger(name, level, [stream_handler])

    @staticmethod
    def get_file_logger(
        name: str,
        level: int = DEBUG,
        formatter: Formatter | None = None,
        ) -> Logger:
        """
        Creates Logger object that sends messages to the file
        :param name: logger name
        :param level: logger threshold
        :param filename: name of the file to which the logger sends messages
        :param formatter: object that specifies a format of the logger message
        :return: logger that sends messages to the file
        """
        if not formatter:
            formatter = FormatterConfig.get_formatter()
        file_handler = LoggerConfig._get_file_handler(formatter)
        return LoggerConfig._get_logger(name, level, [file_handler])

    @staticmethod
    def get_console_and_file_logger(
        name: str,
        level: int = DEBUG
        ) -> Logger:
        """
        Creates Logger object that sends messages to the file and to the console
        :param name: logger name
        :param level: logger threshold
        :param filename: name of the file to which the logger sends messages
        :param console_formatter: object that specifies a format of the logger message for the console
        :param file_formatter: object that specifies a format of the logger message for the file
        :return: logger that sends messages to the file and to the console
        """
        console_formatter = FormatterConfig.get_colored_formatter()
        file_formatter = FormatterConfig.get_formatter()

        stream_handler = LoggerConfig._get_stream_handler(console_formatter)
        file_handler = LoggerConfig._get_file_handler(file_formatter)
        return LoggerConfig._get_logger(name, level, [stream_handler, file_handler])

    @staticmethod
    def _get_logger(name: str, level: int, handlers: list[Handler]) -> Logger:
        """
        Creates a Logger object
        :param name: logger name
        :param level: logger threshold
        :param handlers: collection of handlers for the logger
        :return: A Logger object
        """
        logger = getLogger(name)
        logger.setLevel(level)

        if not logger.handlers:
            for handler in handlers:
                logger.addHandler(handler)
        
        return logger

    @staticmethod
    def _get_stream_handler(formatter: Formatter) -> StreamHandler:
        """
        Creates a StreamHandler object that sends messages from the logger to the console
        :param formatter: object that specifies a format of the logger message
        :return: A StreamHandler object that sends messages from the logger to the console
        """
        stream_handler = StreamHandler(stream=sys.stdout)
        stream_handler.setFormatter(formatter)
        return stream_handler

    @staticmethod
    def _get_file_handler(formatter: Formatter) -> RotatingFileHandler:
        log_file_path = Path('logs/app.log')
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            str(log_file_path),
            mode='a',
            maxBytes=5 * 1024 * 1024,
            backupCount=2,
            encoding='utf-8',
            delay=True
        )
        file_handler.setFormatter(formatter)
        return file_handler