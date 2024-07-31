import re
import os
import sys
import logging
import pandas as pd
from pathlib import Path
from src.config import Config
from zoneinfo import ZoneInfo
from src.utilities.tools import Tools

# import tzlocal
pip = "pip" if "win" in sys.platform else "pip3"
try:
    import tzlocal
except ModuleNotFoundError:
    exit(f"tzlocal package is required\nRun: {pip} install tzlocal")


class Instance:

    def __init__(self, config: Config = None):
        # Set the basic parameters
        self.Config = config
        self.ROOT = self.Path_exist(self.Config.DATA_ROOT)

        # <editor-fold desc="Declare file & folder">
        # data structure
        self.ROOT_Logs      = self.Path_exist(self.ROOT / self.Config.FOLDER_Log)
        self.ROOT_Data      = self.Path_exist(self.ROOT / self.Config.FOLDER_Data)
        self.ROOT_Research  = self.Path_exist(self.ROOT / self.Config.FOLDER_Research)

        # data sub-folder
        self.FOLDER_Symbols = self.Path_exist(self.ROOT_Data / "symbols")
        self.FOLDER_Daily   = self.Path_exist(self.ROOT_Data / "daily")
        self.FOLDER_Tradings= self.Path_exist(self.ROOT_Data / "daily")
        self.FOLDER_Infos   = self.Path_exist(self.ROOT_Data / "infos")

        # research sub-folder
        self.FOLDER_Watch   = self.Path_exist(self.ROOT_Research / "watch")
        self.FOLDER_Charts  = self.Path_exist(self.ROOT_Research / "charts")
        self.FOLDER_Lines   = self.Path_exist(self.ROOT_Research / "lines")
        self.FOLDER_Images = self.Path_exist(self.ROOT_Research / "images")
        self.FOLDER_States = self.Path_exist(self.ROOT_Research / "states")

        # Files
        self.FILE_Infos_Errors = self.Path_exist(self.FOLDER_Infos / "errors.json")
        self.FILE_WatchList = self.Path_exist(Path(self.Config.__dict__["SYM_LIST"]))
        # </editor-fold>

        # <editor-fold desc="Declare Format">
        # Regex
        self.splitRegex = re.compile(r"(\d+\.?\d*)[/\- a-z.]+(\d+\.?\d*)")
        self.bonusRegex = re.compile(r"(\d+) ?: ?(\d+)")
        self.headerText = b"Date,Open,High,Low,Close,Volume,TOTAL_TRADES,QTY_PER_TRADE,DLV_QTY\n"
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
        self.logger = self._log_initial(self.Config.__name__)
        # Exception custom handler (Set the sys.excepthook)
        sys.excepthook = self._log_unhandled_exception
        # Tools
        self.tools = Tools(self.logger)
        # </editor-fold>

        # <editor-fold desc="Initial Data">
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

    def _log_initial(self, name: str) -> logging.Logger:
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

        file_handler = logging.FileHandler(self.ROOT_Logs / "error.log")
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

