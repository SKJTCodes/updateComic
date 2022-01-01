import os
import logging
import logging.handlers
from pathlib import Path
import sys


class Logger:
    def __init__(self, out_file):
        os.system("")  # allows colour to be printed in cmd and powershell natively.
        self.out_file = out_file

        # init logger
        self.log = logging.getLogger("PIL.PngImagePlugin")
        self.log.setLevel(logging.DEBUG)
        logging.getLogger('urllib3').propagate = False

        self.out_dir = os.path.dirname(out_file)
        Path(self.out_dir).mkdir(parents=True, exist_ok=True)

    def get_logger(self):
        # init handler
        file_handler = logging.FileHandler(str(self.out_file))
        file_handler.setLevel(logging.DEBUG)

        file_fmt = logging.Formatter("%(asctime)s (%(levelname)s): %(message)s")
        file_handler.setFormatter(file_fmt)

        std_handler = logging.StreamHandler(sys.stdout)
        std_handler.setLevel(logging.INFO)
        std_format = "$BOLD%(levelname)-15s %(message)s$RESET"
        std_fmt = ColoredFormatter(ColoredFormatter.formatter_message(std_format))
        std_handler.setFormatter(std_fmt)

        self.log.addHandler(file_handler)
        self.log.addHandler(std_handler)

        return self.log


RESET_SEQ = "\033[0m"
COLOR_SEQ = "[1;%dm"
BOLD_SEQ = "\033[1m"


class ColoredFormatter(logging.Formatter):
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

    COLORS = {
        "WARNING": YELLOW,
        "INFO": GREEN,
        "DEBUG": WHITE,
        "CRITICAL": BLUE,
        "ERROR": RED
    }

    def __init__(self, msg):
        logging.Formatter.__init__(self, msg)

    def format(self, record):
        levelname = record.levelname
        if levelname in self.COLORS:
            level_color = "\033" + COLOR_SEQ % (30 + self.COLORS[levelname]) + levelname
            record.levelname = level_color
        return logging.Formatter.format(self, record)

    @staticmethod
    def formatter_message(msg):
        return msg.replace("$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)


