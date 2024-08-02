from argparse import ArgumentParser
from src.instance import Instance

# Group Init
parser = ArgumentParser(prog="init_data.py")
parser.add_argument("-p", "--period", type=str, metavar="str",
                    help="symbols treading, default 1d, Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max")

group = parser.add_mutually_exclusive_group()
# Group arguments setup
group.add_argument("-v", "--version", action="store_true", help="Print the current version.")
group.add_argument("-c", "--config", action="store_true", help="Print the current config.")

# Level 0. Fetch
group.add_argument("-f", "--fetch", action="store_true", help="fetch full symbols from alphavantage.")
group.add_argument("-i", "--info", action="store_true", help="fetch symbols info yfinance.")

# Level 1. Analysis
group.add_argument("-a", "--analyses", action="store_true", help="analyses symbols")

# Level 2. Main daily step, fetch fetching treading data.
group.add_argument("-my", "--mylist", action="store_true", help="fetch symbols from yfinance.")
group.add_argument("-sec", "--sector", type=str, nargs='+',
                   help="Fetch fetching treading for symbols in the specified sectors.")
group.add_argument("-ind", "--industry", type=str, nargs='+',
                   help="Fetch fetching treading for symbols in the specified industries.")

args = parser.parse_args()
# Parse the arguments
period = args.period if args.period else "1d"
# Create Instance
_ = Instance()

if args.version:
    exit(f"Stock Pattern Master - init_data.py: version {_.Config.VERSION}")
if args.config:
    exit(str(_.Config))
# each lower level need base on upper level's result

# Level 0. Fetch
# level 0.a NYSE & NASDAQ vehicle [symbol list] from alphavantage
if args.fetch:
    _.Engine.Symbol().fetch_stock_info_to_db()
# level 0.b Base on full symbols csv file pull all vehicle [info] from exchange.
if args.info:
    _.Engine.Trading().fetch_symbols_info()

# Level 1. Analysis, full stock symbols and each symbol's info does analyses.
if args.analysis:
    _.Engine.Symbol().analyze_symbols_full_list()

# Level 2. Main daily step, based on symbols pull daily fetching treading data.
if args.mylist:
    _.Engine.Trading().fetch_history_by_mylist(period=period)
if args.sector:
    _.Logger.info(f"Fetching symbols by sector: {args.sector}")
    _.Engine.Trading().fetch_history_by_sector_or_industry(
        category="sector",
        category_names=args.sector,
        period=period)
if args.industry:
    _.Logger.info(f"Fetching symbols by industry: {args.industry}")
    _.Engine.Trading().fetch_history_by_sector_or_industry(
        category="industry",
        category_names=args.industry,
        period=period)