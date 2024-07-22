import json
from pathlib import Path


class Config:
    """A class to store all configuration

    # Attributes for polt.py
                            plugin configuration.                       (Default {})
    PLOT_DAYS:              Number of days to be plotted with plot.py.  (Default 160.)
    PLOT_WEEKS:             Number of weeks to be plotted with plot.py. (Default 140.)
    PLOT_M_RS_LEN_D:        Length used to calculate Mansfield
                            Relative Strength on daily TF.              (Default 60.)
    PLOT_M_RS_LEN_W:        Length used to calculate Mansfield
                            Relative Strength on Weekly TF.             (Default 52.)
    PLOT_RS_INDEX:          Index used to calculate Dorsey Relative
                            strength and Mansfield relative strength.   (Default 'S&P 500')
    MAGNET_MODE:            When True, lines snap to closest High,
                            Low, Close or Open. If False, mouse
                            click coordinates on chart are used.        (Default True)

    PLOT_CHART_STYLE:       Chart theme                                 (Default 'tradingview')
    PLOT_CHART_TYPE:        Chart type. One of: ohlc, candle, line      (Default 'candle')

    PLOT_RS_COLOR:          Dorsey RS line color                        (Default 'darkblue')
    PLOT_M_RS_COLOR:        Mansfield RS line color                     (Default 'darkgreen')
    PLOT_DLV_L1_COLOR:      Delivery mode L1 bar color                  (Default 'red')
    PLOT_DLV_L2_COLOR:      Delivery mode L2 bar color                  (Default 'darkorange')
    PLOT_DLV_L3_COLOR:      Delivery mode L3 bar color                  (Default 'royalblue')
    PLOT_DLV_DEFAULT_COLOR: Delivery mode default color                 (Default 'darkgrey')

    PLOT_AXHLINE_COLOR:     Horizontal line color across the Axes       (Default 'crimson')
    PLOT_TLINE_COLOR:       Trend line color                             (Default 'darkturquoise')
    PLOT_ALINE_COLOR:       Arrow color                                 (Default 'mediumseagreen')
    PLOT_HLINE_COLOR:       Horizontal line color                       (Default 'royalblue')

    """

    PRESET = {}
    WATCH = {"SECTORS": "sectors.csv"}

    FOLDER_Data = "data"
    FOLDER_Research = "research"

    TIME_ZONE = "America/New_York"

    Has_Latest_Holidays = False

    # alphavantage.co API Key
    API_KEY_Alphavantage = 'ZLV0FVBBQUBFWEZU'

    # Delivery
    DLV_L1 = 1
    DLV_L2 = 1.5
    DLV_L3 = 2
    DLV_AVG_LEN = 60
    VOL_AVG_LEN = 30

    # PLOT CONFIG
    PLOT_DAYS = 160
    PLOT_WEEKS = 140
    PLOT_M_RS_LEN_D = 60
    PLOT_M_RS_LEN_W = 52
    PLOT_RS_INDEX = "^GSPC" #S&P 500
    MAGNET_MODE = True

    # PLOT THEMES AND COLORS
    # 'binance', 'binancedark', 'blueskies', 'brasil', 'charles',
    # 'checkers', 'classic', 'default', 'ibd', 'kenan', 'mike',
    # 'nightclouds', 'sas', 'starsandstripes', 'tradingview', 'yahoo'
    PLOT_CHART_STYLE = "tradingview"
    # ohlc, candle, line
    PLOT_CHART_TYPE = "candle"

    # PLOT COLORS
    # https://matplotlib.org/stable/gallery/color/named_colors.html#base-colors
    PLOT_RS_COLOR = "darkblue"
    PLOT_M_RS_COLOR = "darkgreen"
    PLOT_DLV_L1_COLOR = "red"
    PLOT_DLV_L2_COLOR = "darkorange"
    PLOT_DLV_L3_COLOR = "royalblue"
    PLOT_DLV_DEFAULT_COLOR = "darkgrey"
    PLOT_AXHLINE_COLOR = "crimson"
    PLOT_TLINE_COLOR = "darkturquoise"
    PLOT_ALINE_COLOR = "mediumseagreen"
    PLOT_HLINE_COLOR = "royalblue"

    # DO NOT EDIT BELOW
    VERSION = "0.1.0"

    def __init__(self, dir: Path) -> None:
        self.DIR = dir
        user_config = self.DIR / "setting" / "user.json"

        if user_config.exists():
            dct = json.loads(user_config.read_bytes())

            if "WATCH" in dct:
                dct["WATCH"].update(self.WATCH)

            self.__dict__.update(dct)

    def to_list(self, filename: str):
        return (self.DIR / "data" / filename).read_text().strip("\n").split("\n")

    def __str__(self):
        txt = f"SPM1 | Version: {self.VERSION}\n"
        for p in self.__dict__:
            txt += f"{p}: {getattr(self, p)}\n"
        return txt
