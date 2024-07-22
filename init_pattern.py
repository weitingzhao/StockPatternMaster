import logging
import concurrent.futures
import sys
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Optional, Tuple, Union, Dict

from src.engine.engine import Engine
from src.instance import Instance
from src.utilities.abstract_loader import AbstractLoader

try:
    from tqdm import tqdm
except ModuleNotFoundError:
    exit("tqdm is required. Run 'pip install tqdm' to install")


def uncaught_exception_handler(*args):
    """
    Handle all uncaught exceptions
    Function passed to sys.excepthook
    """
    logger.critical("Uncaught exception", exc_info=args)
    # cleanup(loader, futures)


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


logger = logging.getLogger(__name__)

# Instance
instance = Instance(__name__)
_ = Engine(instance)
# Group Init
parser = ArgumentParser(prog="init_pattern.py", description="Python CLI tool to identify common Chart patterns")
group = parser.add_mutually_exclusive_group(required=True)

# Group arguments setup
group.add_argument("-f", "--file", type=lambda x: Path(x).expanduser().resolve(), default=None,
                   metavar="filepath", help="File containing list of stocks, One on each line")
group.add_argument("--sym", nargs="+", metavar="SYM", help="Space separated list of stock symbols.")
group.add_argument("-v", "--version", action="store_true", help="Print the current version.")
group.add_argument("--plot", type=lambda x: Path(x).expanduser().resolve(),
                   default=None, help="Plot results from json file")

# Parser arguments setup
parser.add_argument("-c", "--config", type=lambda x: Path(x).expanduser().resolve(),
                    metavar="filepath", default=None, help="Custom config file")
parser.add_argument("-d", "--date", type=datetime.fromisoformat,
                    metavar="str", help="ISO format date YYYY-MM-DD.")
parser.add_argument("--tf", action="store", help="Timeframe string.")
parser.add_argument("-l", "--left", type=int,
                    metavar="int", default=6, help="Number of candles on left side of pivot")
parser.add_argument("-r", "--right", type=int,
                    metavar="int", default=6, help="Number of candles on right side of pivot")
parser.add_argument("--save", type=Path, nargs="?",
                    const=instance.DIR / "images", help="Save results to file")
parser.add_argument("--idx", type=int, default=0, help="Index to plot")

# Use default Config_path or user provided
if "-c" in sys.argv or "--config" in sys.argv:
    idx = sys.argv.index("-c" if "-c" in sys.argv else "--config")
    CONFIG_PATH = Path(sys.argv[idx + 1]).expanduser().resolve()
else:
    CONFIG_PATH = instance.DIR / "user.json"


    



