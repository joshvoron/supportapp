"""
PROJECT LOGGER ver 0.1 by Ilya Voronov. Jan 31 2025
"""
import sys
import os
import json
import logging

from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from colored import Fore, Back, Style


class ProjectLogger:
    """
    A configurable project-wide logger that:
      - Writes all messages to a timestamped file under `logs/`
      - Emits colorized output to the console according to level and module
      - Honors a specified timezone for timestamps
      - Supports child loggers with inherited or custom colors
    """

    def __init__(self, timezone, debug, level):
        """
        Initialize the ProjectLogger.

        :param timezone: IANA timezone string (e.g. 'Europe/Berlin').
                         Invalid values raise ValueError.
        :param debug:   'True' or 'False' to force DEBUG level console output.
        :param level:   One of the standard logging levels as string
                        (e.g. 'INFO', 'WARNING'). Defaults to INFO.
        """
        # Validate and store timezone
        try:
            self.timezone = ZoneInfo(timezone)
        except ZoneInfoNotFoundError:
            logging.critical("An error occurred while trying to found time "
                             "zone.")
            raise ValueError(f"Invalid timezone: {timezone}")

        # Log record format (shared between file & console)
        self.format = (
            "%(asctime)s [%(name)s] [%(filename)s:%("
            "lineno)d] [%(levelname)s] %(message)s"
        )

        # Create a timestamped filename in logs/
        timestamp = datetime.now(self.timezone).strftime('%Y-%m-%d %H.%M.%S')
        self.file_name = f"logs/log__{timestamp}.txt"

        self.debug = debug
        self.level = getattr(logging, level, logging.INFO)

        # Handlers and the root logger will be set up in configure()
        self.logger = None
        self.stream_handler = None
        self.file_handler = None
        self.configure()

    class TimezoneFormatter(logging.Formatter):
        """
        A logging.Formatter that forces timestamps into a given timezone.
        """

        def __init__(self, timezone, fmt, datefmt):
            super().__init__(fmt, datefmt)
            self.timezone = timezone

        def converter(self, timestamp):
            # Convert epoch timestamp to a time tuple in the desired tz
            dt = datetime.fromtimestamp(timestamp, tz=self.timezone)
            return dt.timetuple()

        def formatTime(self, record, datefmt=None):
            # Override to format time in the target timezone
            dt = datetime.fromtimestamp(record.created, tz=self.timezone)
            if datefmt:
                return dt.strftime(datefmt)
            return dt.isoformat()

    class ColorFormatter(TimezoneFormatter):
        """
        Extends TimezoneFormatter to inject ANSI color codes based
        on log level and module name.
        """

        def __init__(self, timezone, fmt, datefmt):
            super().__init__(timezone, fmt, datefmt)
            self.COLORS = {
                "DEBUG": f"{Fore.RGB(30, 107, 0)}"
                         f"{Back.RGB(20, 26, 22)}",
                "INFO": Fore.RGB(42, 180, 201),
                "WARNING": Fore.RGB(201, 170, 42),
                "ERROR": Fore.RGB(204, 0, 0),
                "CRITICAL": f"{Back.RGB(97, 9, 9)}",
            }
            self.RESET = f"{Style.reset}"
            # Default module color; entries here can be overridden at runtime
            self.MODULE_COLORS = {
                "default": Fore.rgb(92, 113, 191)
            }

        def format(self, record):
            """
            Inject color codes for levelname and logger name, then
            delegate to TimezoneFormatter.format().
            """
            levelname = record.levelname
            name = record.name

            parent = self.is_child(name)
            if levelname in self.COLORS:
                record.levelname = (
                    f"{self.COLORS[levelname]}{levelname}{self.RESET}"
                )
            if name in self.MODULE_COLORS:
                record.name = (
                    f"{self.MODULE_COLORS[name]}{name}{self.RESET}"
                )
            elif parent:
                record.name = (
                    f"{self.MODULE_COLORS[parent]}{name}{self.RESET}"
                )
            else:
                record.name = (
                    f"{self.MODULE_COLORS["default"]}{name}{self.RESET}"
                )
            formatted = super().format(record)

            # Restore original values so other handlers aren’t affected
            record.levelname = levelname
            record.name = name
            return formatted

        def is_child(self, name: str):
            """
            If `name` starts with any key in MODULE_COLORS followed by a dot,
            return that parent key; else None.
            """
            for item in self.MODULE_COLORS:
                if name.startswith(item) and name[len(item):].startswith("."):
                    return item
            return False

    def configure(self):
        """
        Create the logs directory (if needed), then prepare:
          - A FileHandler (DEBUG+ all messages, plain formatting)
          - A StreamHandler (DEBUG+ all messages, color formatting)
        """
        try:
            os.makedirs('logs', exist_ok=True)
            self.file_handler = logging.FileHandler(
                filename=self.file_name, mode='w'
            )
        except FileNotFoundError:
            logging.critical(
                "An error occurred while trying to save the log file."
            )
            quit()

        # File handler logs everything, timestamped
        self.file_handler.setLevel(logging.DEBUG)
        file_formatter = self.TimezoneFormatter(
            self.timezone,
            self.format,
            datefmt="%Y-%m-%d %H:%M:%S %Z",
        )
        self.file_handler.setFormatter(file_formatter)

        # Console handler also logs everything, but with colors
        self.stream_handler = logging.StreamHandler(sys.stdout)
        self.stream_handler.setLevel(logging.DEBUG)
        stream_formatter = self.ColorFormatter(
            self.timezone,
            self.format,
            datefmt="%Y-%m-%d %H:%M:%S %Z")
        self.stream_handler.setFormatter(stream_formatter)

    def start_logging(self):
        """
        Instantiate and configure the root logger only once.
        Returns the root logger for further use.
        """
        if self.logger is None:
            root = logging.getLogger()
            root.propagate = False
            root.addHandler(self.file_handler)
            self.stream_handler.formatter.MODULE_COLORS["root"] = Fore.blue
            root.addHandler(self.stream_handler)
            root.level = (
                logging.DEBUG if self.debug == 'True' else self.level
            )
            self.logger = root
        else:
            self.logger.warning(
                "THE MAIN LOGGER HAS ALREADY BEEN CREATED.  "
                "USE THIS COMMAND ONLY ONCE!")
        return self.logger

    def new_logger(self, name, color=None):
        """
        Create or retrieve a top-level child logger attached to root.
        :param name:  Unique logger name
        :param color: Optional Fore.<COLOR> constant name (e.g. 'red')
        """
        child = logging.getLogger(name)
        child.propagate = False
        child.addHandler(self.file_handler)
        if color:
            color = getattr(Fore, color.upper())
        else:
            color = Fore.white
        self.stream_handler.formatter.MODULE_COLORS[name] = f"{color}"
        child.addHandler(self.stream_handler)
        return child

    def new_child(self, parent: logging.Logger, name: str, color: str | None = None):
        """
        Create a nested logger under an existing one.
        :param parent: Parent logger instance
        :param name: Name (child name = parent.name + '.' + suffix)
        :param color:  Optional new color; defaults to parent’s color
        """
        child_logger = parent.getChild(name)
        child_logger.propagate = False
        child_logger.addHandler(self.file_handler)
        if color is not None:
            color = getattr(Fore, color.upper())
        else:
            color = parent.name
        self.stream_handler.formatter.MODULE_COLORS[child_logger.name] = (
            self.stream_handler.formatter.MODULE_COLORS[color]
        )
        child_logger.addHandler(self.stream_handler)
        return child_logger

    def set_color(self, logger_name: str, color: str):
        """
        Change the console color for an existing logger name.
        """
        color = getattr(Fore, color.upper(), None)
        if color:
            self.stream_handler.formatter.MODULE_COLORS[logger_name] = (
                f"{color}"
            )
        else:
            logging.warning(f"Unknown Fore color: {color}")

    def set_colors_from_json(self, file_path: str):
        """
        Load a JSON file mapping logger names to Fore color names and
        apply them via `set_color()`.
        JSON format: { "module.name": "GREEN", "other": "RED" }
        """
        with open(file_path) as file:
            dictionary = json.loads(file.read())
            for item in dictionary:
                self.set_color(item, dictionary[item])

