import re
import os
import sys
import json
from typing import Dict
from zoneinfo import ZoneInfo

import pandas as pd

from src.setting.config import Config
from src.setting.dates import Dates
from src.utilities.helper import Helper

# import tzlocal
pip = "pip" if "win" in sys.platform else "pip3"
try:
    import tzlocal
except ModuleNotFoundError:
    exit(f"tzlocal package is required\nRun: {pip} install tzlocal")


class Instance:

    def __init__(self, name: str, config: Config):
        # Set the basic parameters
        self.__name__ = name
        self.config = config
        self.PLOT_PLUGINS = {}

        # Base on config, set the instance variables
        self.DAILY_FOLDER = self.config.DIR / self.config.DATA_Folder / "daily"
        self.ISIN_FILE = self.config.DIR / self.config.DATA_Folder / "isin.csv"
        self.AMIBROKER_FOLDER = self.config.DIR / self.config.DATA_Folder / "amibroker"
        self.META_FILE = self.config.DIR / self.config.DATA_Folder / "meta.json"

        self.hasLatestHolidays = False

        self.splitRegex = re.compile(r"(\d+\.?\d*)[\/\- a-z\.]+(\d+\.?\d*)")
        self.bonusRegex = re.compile(r"(\d+) ?: ?(\d+)")
        self.headerText = (b"Date,Open,High,Low,Close,Volume,TOTAL_TRADES,QTY_PER_TRADE,DLV_QTY\n")

        # Logger
        self.logger = Helper(self.config).configure_logger(self.__name__)

        # Set time
        self.tz_local = tzlocal.get_localzone()
        self.tz_US = ZoneInfo(self.config.TIME_ZONE)

        if "win" in sys.platform:
            # enable color support in Windows
            os.system("color")

        # Init Meta
        self.META: Dict = json.loads(self.META_FILE.read_bytes())

        # Init ISIN
        self.ISIN = pd.read_csv(self.ISIN_FILE, index_col="ISIN")

        # initiate the dates
        self.DATES = Dates(self.logger, self.tz_US, self.tz_local, self.META["lastUpdate"])

    def log_unhandled_exception(self, exc_type, exc_value, exc_traceback):
        # Log the unhandled exception
        self.logger.critical(
            "Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback)
        )