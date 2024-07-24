import concurrent
import importlib
import json
import sys
from concurrent.futures import Future
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Optional, Tuple
from tqdm import tqdm
from src.engine.engine import Engine
from src.instance import Instance
from argparse import ArgumentParser
from src.loaders.abstract_loader import AbstractLoader


def get_user_input() -> str:
    user_input = input(
        """
    Enter a number to select a pattern.

    0. ALL  - Scan all patterns
    1: BULL - All Bullish patterns
    2: BEAR - All Bearish patterns
    3. VCPU - Bullish VCP (Volatility Contraction pattern)
    4. VCPD - Bearish VCP
    5. DBOT - Double Bottom (Bullish)
    6. DTOP - Double Top (Bearish)
    7. HNSD - Head and Shoulder
    8. HNSU - Reverse Head and Shoulder
    9. TRNG - Triangles (Symmetrical, Ascending, Descending)
    > """
    )

    if not (user_input.isdigit() and int(user_input) in range(10)):
        print("Enter a key from the list")
        return get_user_input()

    return user_input


def cleanup(loader: AbstractLoader, futures: List[concurrent.futures.Future]):
    if futures:
        for future in futures:
            future.cancel()
        concurrent.futures.wait(futures)
    if loader.closed:
        loader.close()


def scan_pattern(
        symbol: str,
        functions: Tuple[Callable, ...],
        loader: AbstractLoader,
        bars_left: int = 6,
        bars_right: int = 6) -> List[dict]:
    patterns: List[dict] = []
    df = loader.get(symbol)
    if df is None or df.empty:
        return patterns

    if df.index.has_duplicates:
        df = df[~df.index.duplicated()]
    pivots = _.Pattern_Detector().get_max_min(df, barsLeft=bars_left, barsRight=bars_right)
    if not pivots.shape[0]:
        return patterns

    for fun in functions:
        if not callable(fun):
            raise TypeError(f"Expected callable. Got {type(fun)}")
        try:
            result = fun(symbol, df, pivots)
        except Exception as e:
            instance.logger.exception(f"SYMBOL name: {symbol}", exc_info=e)
            return patterns
        if result:
            patterns.append(_.Pattern_Detector().make_serializable(result))

    return patterns


def process(
        symbol_list: List,
        fns: Tuple[Callable, ...],
        futures: List[concurrent.futures.Future]
) -> List[dict]:
    patterns: List[dict] = []
    # Load or initialize state dict for storing previously detected patterns
    state = None
    state_file = None
    filtered = None

    if instance.Config.get("SAVE_STATE", False) and args.file and not args.date:
        state_file = instance.DIR / f"state/{args.file.stem}_{args.pattern}.json"
        if not state_file.parent.is_dir():
            state_file.parent.mkdir(parents=True)
        state = json.loads(state_file.read_bytes()) if state_file.exists() else {}

    # determine the folder to save to in case save option is set
    save_folder: Optional[Path] = None
    image_folder = f"{datetime.now():%d_%b_%y_%H%M}"
    if "SAVE_FOLDER" in instance.Config:
        save_folder = Path(instance.Config["SAVE_FOLDER"]) / image_folder
    if args.save:
        save_folder = args.save / image_folder
    if save_folder and not save_folder.exists():
        save_folder.mkdir(parents=True)
    # begin a scan process
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for sym in symbol_list:
            future = executor.submit(scan_pattern, sym, fns, loader, bars_left=args.left, bars_right=args.right)
            futures.append(future)
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
            try:
                result = future.result()
            except Exception as e:
                cleanup(loader, futures)
                instance.logger.exception("Error in Future - scaning patterns", exc_info=e)
                return []
            patterns.extend(result)
        futures.clear()

        if state is not None:
            # if no args.file option, no need to save state, return patterns
            # Filter for newly detected patterns and remove stale patterns

            # list for storing newly detected patterns
            filtered = []
            # initial length of state dict
            len_state = len(state)
            # Will contain keys to all patterns currently detected
            detected = set()
            for dct in patterns:
                # unique identifier
                key = f'{dct["sym"]}-{dct["pattern"]}'
                detected.add(key)
                if not len_state:
                    # if state is empty, this is a first run
                    # no need to filter
                    state[key] = dct
                    filtered.append(dct)
                    continue
                if key in state:
                    if dct["start"] == state[key]["start"]:
                        # if the pattern starts on the same date,
                        # they are the same previously detected pattern
                        continue
                    # Else there is a new pattern for the same key
                    state[key] = dct
                    filtered.append(dct)
                # new pattern
                filtered.append(dct)
                state[key] = dct
            # set difference - get keys in state dict not existing in detected
            # These are pattern keys no longer detected and can be removed
            invalid_patterns = set(state.keys()) - detected
            # Clean up stale patterns in state dict
            for key in invalid_patterns:
                state.pop(key)
            if state_file:
                state_file.write_text(json.dumps(state, indent=2))
                instance.logger.info(
                    f"\nTo view all current market patterns, run `py init.py --plot state/{state_file.name}\n"
                )

        patterns_to_output = patterns if state is None else filtered
        if not patterns_to_output:
            return []
        # Save the images if required
        if save_folder:
            plotter = _.Plot(None, loader, save_folder=save_folder)
            for i in patterns_to_output:
                future = executor.submit(plotter.save, i.copy())
                futures.append(future)

            instance.logger.info("Saving images")

            for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
                try:
                    future.result()
                except Exception as e:
                    cleanup(loader, futures)
                    instance.logger.exception("Error in Futures - Saving images ", exc_info=e)
                    return []

    patterns_to_output.append({
        "timeframe": loader.timeframe,
        "end_date": args.date.isoformat() if args.date else None,
    })
    return patterns_to_output


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
parser.add_argument("--save", type=Path, nargs="?", const=instance.DIR / "images",
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
    CONFIG_PATH = instance.Config.user_config

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

# Load patterns dictionary
fn_dict = _.Pattern_List()
fn = fn_dict[key]

instance.logger.info(
    f"Scanning `{key.upper()}` patterns on `{loader.timeframe}`. Press Ctrl - C to exit"
)

data = args.file.read_text().strip().split("\n") if args.file else args.sym
patterns: List[dict] = []

# Get function out
fn = fn_dict[key]
# check functions
if callable(fn):
    fns = (fn,)
elif fn == "bull":
    bull_list = ("vcpu", "hnsu", "dbot")
    fns = tuple(v for k, v in fn_dict.items() if k in bull_list and callable(v))
elif fn == "bear":
    bear_list = ("vcpd", "hnsd", "dtop")
    fns = tuple(v for k, v in fn_dict.items() if k in bear_list and callable(v))
else:
    fns = tuple(v for k, v in fn_dict.items() if k in key_list[3:] and callable(v))

args = parser.parse_args()

try:
    patterns = process(data, fns, futures)
except KeyboardInterrupt:
    cleanup(loader, futures)
    instance.logger.info("User exit")
    exit()
