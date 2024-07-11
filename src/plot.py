from src.setting.config import Config
from src.utilities.plugin import Plugin
from src.instance import Instance
from argparse import ArgumentParser
from pathlib import Path

DIR = Path(__file__).parent

instance = Instance()
config = Config()
plugin = Plugin()

parser = ArgumentParser(prog="plot.py")
group = parser.add_mutually_exclusive_group(required=True)

group.add_argument(
    "--sym",
    nargs="+",
    metavar="SYM",
    help="Space separated list of stock symbols.",
)

group.add_argument(
    "--watch",
    metavar="NAME",
    help="load a watchlist file by NAME."
)

if len(instance.PLOT_PLUGINS):
    plugin.register(instance.PLOT_PLUGINS, parser)



