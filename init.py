from argparse import ArgumentParser
from src.engine.engine import Engine
from src.instance import Instance
import yfinance as yf

# Instance
instance = Instance(__name__)
_ = Engine(instance)
# Group Init
parser = ArgumentParser(prog="init.py")
group = parser.add_mutually_exclusive_group()

# Group arguments setup
group.add_argument("-v", "--version", action="store_true", help="Print the current version.")
group.add_argument("-c", "--config", action="store_true", help="Print the current config.")
group.add_argument("-f", "--fetch", action="store_true", help="fetch full symbols from alphavantage.")
group.add_argument("-a", "--analysis", action="store_true", help="analysis symbols")
group.add_argument("-s", "--symbols", action="store_true", help="fetch symbols from yfinance.")

parser.add_argument("-p","--period", type=str, metavar="str",
                   help="symbols history, default 1d, Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max")


args = parser.parse_args()

# Parse the arguments
period = args.period if args.period else "1d"


if args.version:
    exit(f"Stock Pattern Master - init.py: version {instance.Config.VERSION}")
if args.config:
    exit(str(instance.Config))
if args.fetch:
    _.Symbols().fetch_stock_list()
if args.analysis:
    _.Symbols().analyze_stock_list()
if args.symbols:
    _.Tradings().fetch(period=period)


