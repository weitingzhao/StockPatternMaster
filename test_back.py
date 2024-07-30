import concurrent
import importlib
import json
import sys
from concurrent.futures import Future
from datetime import datetime
from pathlib import Path
from typing import List
from src.engines import Engine
from src.instance import Instance
from argparse import ArgumentParser

# Instance
instance = Instance(__name__)
_ = Engine(instance)
futures: List[concurrent.futures.Future] = []
key_list = ("all", "bull", "bear", "vcpu", "vcpd", "dbot", "dtop", "hnsd", "hnsu", "trng")
config_help = """
Config help
DATA_PATH: Folder path for OHLC csv data.
SYM_LIST: Optional file with list of symbols, one per line.
SAVE_FOLDER: Optional folder path to save charts as images.
"""

# Parse CLI arguments
parser = ArgumentParser(
    description="Python CLI tool to identify common Chart patterns",
    epilog="https://github.com/BennyThadikaran/stock-pattern",
)
parser.add_argument("-c", "--config", type=lambda x: Path(x).expanduser().resolve(),
                    default=None, metavar="filepath", help="Custom config file")
parser.add_argument("-d", "--date", type=datetime.fromisoformat, metavar="str",
                    help="ISO format date YYYY-MM-DD.")
parser.add_argument("--tf", action="store", help="Timeframe string.")
parser.add_argument("-p", "--pattern", type=str, metavar="str", choices=key_list,
                    help=f"String pattern. One of {', '.join(key_list)}")
parser.add_argument("-l", "--left", type=int, metavar="int", default=6,
                    help="Number of candles on left side of pivot")
parser.add_argument("-r", "--right", type=int, metavar="int", default=6,
                    help="Number of candles on right side of pivot")
parser.add_argument("--save", type=Path, nargs="?", const=instance.FOLDER_Images,
                    help="Specify the save directory")
parser.add_argument("--idx", type=int, default=0, help="Index to plot")
# Group
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-f", "--file", type=lambda x: Path(x).expanduser().resolve(),
                   default=None, metavar="filepath", help="File containing list of stocks. One on each line")
group.add_argument("--sym", nargs="+", metavar="SYM", help="Space separated list of stock symbols.")
group.add_argument("-v", "--version", action="store_true", help="Print the current version.")
group.add_argument("--plot", type=lambda x: Path(x).expanduser().resolve(),
                   default=None, help="Plot results from json file")

if "-c" in sys.argv or "--config" in sys.argv:
    idx = sys.argv.index("-c" if "-c" in sys.argv else "--config")
    CONFIG_PATH = Path(sys.argv[idx + 1]).expanduser().resolve()
else:
    CONFIG_PATH = instance.Config.FILE_user

if CONFIG_PATH.exists():
    config = json.loads(CONFIG_PATH.read_bytes())
    data_path = Path(config["DATA_PATH"]).expanduser()
else:
    json_content = {"DATA_PATH": "", "POST_SCAN_PLOT": True}
    CONFIG_PATH.write_text(json.dumps(json_content, indent=2))
    print("user.json file generated. Edit `DATA_PATH` to add a data source")
    print(config_help)
    exit()

if config["DATA_PATH"] == "" or not data_path.exists():
    exit("`DATA_PATH` not found or not provided. Edit user.json.")
sym_list = config["SYM_LIST"] if "SYM_LIST" in config else None

if sym_list is not None and not (
        "-f" in sys.argv
        or "--file" in sys.argv
        or "--sym" in sys.argv
        or "-v" in sys.argv
        or "--version" in sys.argv
        or "--plot" in sys.argv
):
    sys.argv.extend(("-f", sym_list))

# get args from parser
args = parser.parse_args()

# Load data loader from config. Default loader is EODFileLoader
loader_name = config.get("LOADER", "treading_data_loader")
loader_module = importlib.import_module(f"src.loaders.{loader_name}")

if args.plot:
    data = json.loads(args.plot.read_bytes())
    # Last item contains meta data about the timeframe used, end_date etc
    meta = data.pop()
    end_date = None

    if meta["end_date"]:
        end_date = datetime.fromisoformat(meta["end_date"])
    loader = getattr(loader_module, loader_name)(
        config,
        meta["timeframe"],
        end_date=end_date,
    )
    plotter = _.Plot(data, loader)
    plotter.plot(args.idx)
    cleanup(loader, futures)
    exit()

loader = getattr(loader_module, loader_name)(
    config,
    args.tf,
    end_date=args.date,
)

if args.pattern:
    key: str = args.pattern
else:
    try:
        user_input = get_user_input()
    except KeyboardInterrupt:
        cleanup(loader, futures)
        exit()

    key = key_list[int(user_input)]
    args.pattern = key


