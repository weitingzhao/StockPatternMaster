import re
import os
import sys
import json
import random
import string
from pathlib import Path
from typing import Dict
from zoneinfo import ZoneInfo
import pandas as pd
import logging

from src.setting.config import Config
from src.utilities.csv_loader import CsvLoader
from src.utilities.dates import Dates
from src.utilities.json_loader import JsonLoader
from src.utilities.tools import Tools
from src.utilities.web_loader import WebLoader

# import tzlocal
pip = "pip" if "win" in sys.platform else "pip3"
try:
    import tzlocal
except ModuleNotFoundError:
    exit(f"tzlocal package is required\nRun: {pip} install tzlocal")


class Instance:

    def __init__(self, name: str = __name__,
                 config: Config = Config(Path(__file__).parents[1])):
        # Set the basic parameters
        self.__name__ = name
        self.Config = config
        self.DIR = self.Config.DIR

        # <editor-fold desc="Declare file & folder">
        self.FOLDER_Logs = self._path_exist(self.DIR / "logs")
        self.FOLDER_Symbols = self._path_exist(self.DIR / self.Config.DATA_Folder / "symbols")
        self.FOLDER_Daily = self._path_exist(self.DIR / self.Config.DATA_Folder / "daily")
        self.FOLDER_Amibroker = self._path_exist(self.DIR / self.Config.DATA_Folder / "amibroker")

        self.FILE_Meta = self._path_exist(self.DIR / self.Config.DATA_Folder / "meta.json")
        self.FILE_Isin = self._path_exist(self.DIR / self.Config.DATA_Folder / "isin.csv")

        # </editor-fold>

        # <editor-fold desc="Declare Format">
        # Regex
        self.splitRegex = re.compile(r"(\d+\.?\d*)[\/\- a-z\.]+(\d+\.?\d*)")
        self.bonusRegex = re.compile(r"(\d+) ?: ?(\d+)")
        self.headerText = (b"Date,Open,High,Low,Close,Volume,TOTAL_TRADES,QTY_PER_TRADE,DLV_QTY\n")
        # Timezone
        self.tz_local = tzlocal.get_localzone()
        self.tz_US = ZoneInfo(self.Config.TIME_ZONE)
        # Color
        if "win" in sys.platform:
            # enable color support in Windows
            os.system("color")
        # </editor-fold>

        # <editor-fold desc="Setup Tools">
        # Logger
        self.logger = self._log_configure(self.__name__)
        # Exception custom handler (Set the sys.excepthook)
        sys.excepthook = self._log_unhandled_exception
        # Tools
        self.TOOLS = Tools(self.logger)
        # </editor-fold>

        # <editor-fold desc="Initial Data">
        # Init Meta
        self.META: Dict = json.loads(self.FILE_Meta.read_bytes())
        # Init ISIN
        self.ISIN = pd.read_csv(self.FILE_Isin, index_col="ISIN")
        # initiate the dates
        self.DATES = Dates(self.logger, self.tz_US, self.tz_local, self.META["lastUpdate"])
        # PLOT Plugins
        self.PLOT_PLUGINS = {}
        # </editor-fold>

    def _log_unhandled_exception(self, exc_type, exc_value, exc_traceback):
        # Log the unhandled exception
        self.logger.critical(
            "Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback)
        )

    def _log_configure(self, name: str) -> logging.Logger:
        """Return a logger instance by name
        Creates a file handler to log messages with level WARNING and above
        Creates a stream handler to log messages with level INFO and above

        Parameters:
        name (str): Pass __name__ for module level logger
        """

        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        stdout_handler = logging.StreamHandler()
        stdout_handler.setLevel(logging.INFO)
        stdout_handler.setFormatter(logging.Formatter('[%(asctime)s - %(name)s] %(levelname)s: %(message)s'))

        file_handler = logging.FileHandler(self.FOLDER_Logs / "error.log")
        file_handler.setLevel(logging.WARNING)
        file_handler.setFormatter(
            logging.Formatter('[%(asctime)s - %(name)s] %(levelname)s: %(message)s')
        )

        logger.addHandler(stdout_handler)
        logger.addHandler(file_handler)

        return logger

    @staticmethod
    def _path_exist(path: Path):
        if path.exists():
            return path
        base, ext = os.path.splitext(path)
        if not ext:  # No extension means it's likely a directory
            # Create any necessary parent directories
            path.mkdir(parents=True, exist_ok=True)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()

    @staticmethod
    def Random_char(length):
        return "".join(random.choices(string.ascii_lowercase) for _ in range(length))

    def New_Csv(self, *args) -> CsvLoader:
        path = (self.DIR / self.Config.DATA_Folder).joinpath(*args)
        return CsvLoader(path)

    def New_Json(self, *args):
        path = (self.DIR / self.Config.DATA_Folder).joinpath(*args)
        return JsonLoader(path)

    def New_Web(self, url: str) -> WebLoader:
        return WebLoader(self.logger, url)
