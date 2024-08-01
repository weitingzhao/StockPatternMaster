import csv
import sys
import json
import concurrent
from typing import List
from pathlib import Path
from datetime import datetime
from argparse import ArgumentParser
import src as _
from concurrent.futures import Future

# Instance
key_list = _.engine.pattern_list()

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
parser.add_argument("-p", "--patterns", type=str, metavar="str", choices=key_list,
                    help=f"String patterns. One of {', '.join(key_list)}")
parser.add_argument("-l", "--left", type=int, metavar="int", default=6,
                    help="Number of candles on left side of pivot")
parser.add_argument("-r", "--right", type=int, metavar="int", default=6,
                    help="Number of candles on right side of pivot")
parser.add_argument("--save", type=Path, nargs="?", const=_.instance.FOLDER_Images,
                    help="Specify the save directory")
parser.add_argument("--idx", type=int, default=0, help="Index to local")
parser.add_argument("-v", "--version", action="store_true", help="Print the current version.")

# Parser Group
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-f", "--file", type=lambda x: Path(x).expanduser().resolve(),
                   default=None, metavar="filepath", help="File containing list of stocks. One on each line")
group.add_argument("--local", type=lambda x: Path(x).expanduser().resolve(),
                   default=None, help="Plot results from json file")
group.add_argument("-my", "--mylist", nargs="+", metavar="SYM",
                   help="Space separated list of stock symbols.")
group.add_argument("-sec", "--sector", type=str, nargs='+',
                   help="Fetch fetching treading for symbols in the specified sectors.")
group.add_argument("-ind", "--industry", type=str, nargs='+',
                   help="Fetch fetching treading for symbols in the specified industries.")
# check "config"
if "-c" in sys.argv or "--config" in sys.argv:
    idx = sys.argv.index("-c" if "-c" in sys.argv else "--config")
    CONFIG_PATH = Path(sys.argv[idx + 1]).expanduser().resolve()
else:
    CONFIG_PATH = _.instance.config.FILE_user

if CONFIG_PATH.exists():
    config = json.loads(CONFIG_PATH.read_bytes())
    data_path = Path(config["DATA_PATH"]).expanduser()
else:
    json_content = {"DATA_PATH": "", "POST_SCAN_PLOT": True}
    CONFIG_PATH.write_text(json.dumps(json_content, indent=2))
    print("user.json file generated. Edit `DATA_PATH` to add a data source")
    print("""
    Config help
    DATA_PATH: Folder path for OHLC csv data.
    SYM_LIST: Optional file with list of symbols, one per line.
    SAVE_FOLDER: Optional folder path to save charts as images.
    """)
    exit()

# check "Data Path"
if config["DATA_PATH"] == "" or not data_path.exists():
    exit("`DATA_PATH` not found or not provided. Edit user.json.")

# get "args"
args = parser.parse_args()

# -v --version
if args.version:
    exit(
        f"""
    Stock-Pattern Master | Version {_.instance.config.VERSION}
    Copyright (C) 2024 Vision Zhao

    Github: https://github.com/weitingzhao/StockPatternMaster

    This program comes with ABSOLUTELY NO WARRANTY.
    This is free software, and you are welcome to redistribute it
    under certain conditions.
    See license: https://www.gnu.org/licenses/gpl-3.0.en.html#license-text
    """
    )


# # Load data loader from config. Default loader is EODFileLoader
# loader_name = config.get("LOADER", "treading_data_loader:TreadingDataLoader")
# module_name, class_name = loader_name.split(":")
# # Dynamically import the module
# loader_module = importlib.import_module(f"src.tire2.{module_name}")
#
# # Plot
# if args.local:
#     symbol_list = json.loads(args.local.read_bytes())
#     # Last item contains meta data about the timeframe used, end_date etc
#     meta = symbol_list.pop()
#     end_date = None
#     if meta["end_date"]:
#         end_date = datetime.fromisoformat(meta["end_date"])
#     # Access the class from the imported module
#     loader = getattr(loader_module, class_name)(
#         config=config,
#         tf=meta["timeframe"],
#         end_date=end_date)
#     plotter = _.Plot(symbol_list, loader)
#     plotter.local(args.idx)
#     cleanup(loader, futures)
#     exit()

def get_user_input() -> str:
    user_input = input("""
    Enter a number to select a patterns.
    0. ALL  - Scan all patterns
    1: BULL - All Bullish patterns
    2: BEAR - All Bearish patterns
    3. VCPU - Bullish VCP (Volatility Contraction patterns)
    4. VCPD - Bearish VCP
    5. DBOT - Double Bottom (Bullish)
    6. DTOP - Double Top (Bearish)
    7. HNSD - Head and Shoulder
    8. HNSU - Reverse Head and Shoulder
    9. TRNG - Triangles (Symmetrical, Ascending, Descending)
    > """)
    if not (user_input.isdigit() and int(user_input) in range(10)):
        print("Enter a key from the list")
        return get_user_input()
    return user_input

def load_symbols(file_name: str, arg_param: List[str]):
    with (_.instance.FOLDER_Watch / f"{file_name}.json").open("r", encoding="utf-8") as file:
        data = json.load(file)
        if "all" in arg_param:
            for x,symbols in data['detail'].items():
                symbol_list.extend(symbols)
        else:
            for category in arg_param:
                symbol_list.extend(data['detail'].get(category, []))
    _.instance.logger.info(f"Fetching symbols by {file_name}: {args.sector}")


# -p --patterns
if args.pattern:
    key: str = args.pattern
else:
    try:
        user_input = get_user_input()
    except KeyboardInterrupt:
        exit()
    key = key_list[int(user_input)]
    args.pattern = key

##--------------------------##
# Initialize Scaner
scaner = _.analyse.treading(args)
_.logger.info(f"Scanning `{key.upper()}` patterns on `{scaner.loader.timeframe}`. Press Ctrl - C to exit")

# Prepare symbol list and futures result
symbol_list = []
# Level 2. Main daily step, based on symbols pull daily fetching treading data.
if args.file:
    symbol_list = args.file.read_text().strip().split("\n")[1:]
if args.mylist:
    with (_.instance.FOLDER_Watch / "mylist.csv").open("r", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)
        symbol_list = [row[0] for row in reader]
if args.sector:
    load_symbols("symbols_sector", args.sector)
if args.industry:
    load_symbols("symbols_industry", args.industry)

# check "Symbol List"
sym_list = config["SYM_LIST"] if "SYM_LIST" in config else None
if sym_list is not None and not (
        "-f" in sys.argv
        or "--file" in sys.argv
        or "--sym" in sys.argv
        or "-v" in sys.argv
        or "--version" in sys.argv
        or "--local" in sys.argv
):
    sys.argv.extend(("-f", sym_list))

# Process by patterns
futures: List[concurrent.futures.Future] = []
patterns = scaner.process_by_pattern_name(symbol_list, key, futures)
print(f"patterns:{patterns}")
