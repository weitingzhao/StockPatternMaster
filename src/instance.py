import re
import os
import sys
import json
from pathlib import Path
from typing import Dict
from zoneinfo import ZoneInfo
import pandas as pd
import logging

from src.config import Config
from src.loaders.csv_loader import CsvLoader
from src.utilities.dates import Dates
from src.loaders.json_loader import JsonLoader
from src.utilities.tools import Tools
from src.loaders.web_loader import WebLoader

# import tzlocal
pip = "pip" if "win" in sys.platform else "pip3"
try:
    import tzlocal
except ModuleNotFoundError:
    exit(f"tzlocal package is required\nRun: {pip} install tzlocal")


class Instance:

    def __init__(self, name: str = __name__, config_path: Path = None):
        # Set the basic parameters
        self.__name__ = name
        self.DIR = Path(__file__).parents[1]
        self.Config: Config = Config(self.DIR / "user.json" if config_path is None else config_path)

        # <editor-fold desc="Declare file & folder">
        # data
        self.FOLDER_Logs = self.Path_exist(self.DIR / "logs")
        self.FOLDER_Symbols = self.Path_exist(self.DIR / self.Config.FOLDER_Data / "symbols")
        self.FOLDER_Daily = self.Path_exist(self.DIR / self.Config.FOLDER_Data / "daily")
        self.FOLDER_Amibroker = self.Path_exist(self.DIR / self.Config.FOLDER_Data / "amibroker")
        self.FOLDER_Tradings = self.Path_exist(self.DIR / self.Config.FOLDER_Data / "tradings")

        self.FILE_Meta = self.Path_exist(self.DIR / self.Config.FOLDER_Data / "meta.json")
        self.FILE_Isin = self.Path_exist(self.DIR / self.Config.FOLDER_Data / "isin.csv")

        # research
        self.FOLDER_Watch = self.Path_exist(self.DIR / self.Config.FOLDER_Research / "watch")
        self.FOLDER_Charts = self.Path_exist(self.DIR / self.Config.FOLDER_Research / "charts")
        self.FOLDER_Lines = self.Path_exist(self.DIR / self.Config.FOLDER_Research / "lines")

        self.FILE_WatchList = self.Path_exist(Path(self.Config.__dict__["SYM_LIST"]))
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
        self.tools = Tools(self.logger)
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
        # MyList
        self.LIST_Watch = pd.read_csv(self.FILE_WatchList)["watchlist"].tolist()
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
    def Path_exist(path: Path):
        if path.exists():
            return path
        base, ext = os.path.splitext(path)
        if not ext:  # No extension means it's likely a directory
            # Create any necessary parent directories
            path.mkdir(parents=True, exist_ok=True)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
        return path

    def config_json(self):
        return JsonLoader(self.DIR / "src" / "setting" / "user.json")

    def config_new(self, user_path: Path):
        self.Config = Config(user_path)
        return self.Config

    def csv_tradings(self, *args) -> CsvLoader:
        path = (self.DIR / self.Config.FOLDER_Data).joinpath(*args)
        self.Path_exist(path)
        return CsvLoader(path)

    def json(self, *args):
        path = (self.DIR / self.Config.FOLDER_Data).joinpath(*args)
        self.Path_exist(path)
        return JsonLoader(path)

    def web(self, url: str) -> WebLoader:
        return WebLoader(self.logger, url)
