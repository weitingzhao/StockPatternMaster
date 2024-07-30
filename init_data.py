from argparse import ArgumentParser
import src as _

# Group Init
parser = ArgumentParser(prog="init_data.py")
parser.add_argument("-p", "--period", type=str, metavar="str",
                    help="symbols history, default 1d, Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max")

group = parser.add_mutually_exclusive_group()
# Group arguments setup
group.add_argument("-v", "--version", action="store_true", help="Print the current version.")
group.add_argument("-c", "--config", action="store_true", help="Print the current config.")

# Level 0. Fetch
group.add_argument("-f", "--fetch", action="store_true", help="fetch full symbols from alphavantage.")
group.add_argument("-i", "--info", action="store_true", help="fetch symbols info yfinance.")

# Level 1. Analysis
group.add_argument("-a", "--analysis", action="store_true", help="analysis symbols")

# Level 2. Main daily step, fetch trading history data.
group.add_argument("-my", "--mylist", action="store_true", help="fetch symbols from yfinance.")
group.add_argument("-sec", "--sector", type=str, nargs='+',
                   help="Fetch trading history for symbols in the specified sectors.")
group.add_argument("-ind", "--industry", type=str, nargs='+',
                   help="Fetch trading history for symbols in the specified industries.")

args = parser.parse_args()

# Parse the arguments
period = args.period if args.period else "1d"

if args.version:
    exit(f"Stock Pattern Master - init_data.py: version {_.instance.Config.VERSION}")
if args.config:
    exit(str(_.instance.Config))
# each lower level need base on upper level's result

# Level 0. Fetch
# level 0.a NYSE & NASDAQ vehicle [symbol list] from alphavantage
if args.fetch:
    _.engine.Symbol().fetch_full_stock_list()
# level 0.b Base on full symbols csv file pull all vehicle [info] from exchange.
if args.info:
    _.engine.Trading().fetch_symbols_info()

# Level 1. Analysis, full stock symbols and each symbol's info does analysis.
if args.analysis:
    _.engine.Symbol().analyze_stock_list()

# Level 2. Main daily step, based on symbols pull daily trading history data.
if args.mylist:
    _.engine.Trading().fetch_tradings_history_by_mylist(period=period)
if args.sector:
    _.instance.logger.info(f"Fetching symbols by sector: {args.sector}")
    _.engine.Trading().fetch_tradings_history_by_sector_or_industry(
        category="sector",
        category_names=args.sector,
        period=period)
if args.industry:
    _.instance.logger.info(f"Fetching symbols by industry: {args.industry}")
    _.engine.Trading().fetch_tradings_history_by_sector_or_industry(
        category="industry",
        category_names=args.industry,
        period=period)