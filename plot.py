from datetime import datetime
from src.engine.engine import Engine
from src.instance import Instance
from argparse import ArgumentParser
import mplfinance as mpl

def process_plot(df, plot_args):
    mpl.plot(df, **plot_args)

# Instance
instance = Instance(__name__)
_ = Engine(instance)
# Group Init
parser = ArgumentParser(prog="plot.py")
group = parser.add_mutually_exclusive_group(required=True)

# Group arguments setup
group.add_argument("--sym", nargs="+", metavar="SYM",help="Space separated list of stock symbols.")
group.add_argument("--watch", metavar="NAME", help="load a watchlist file by NAME.")
group.add_argument("--watch-add", nargs=2, metavar=("NAME", "FILENAME"),
                   help="Save a watchlist by NAME and FILENAME")
group.add_argument("--watch-rm", metavar="NAME", help="Remove a watchlist by NAME and FILENAME")
group.add_argument("--preset", help="Load command line options saved by NAME.", metavar="NAME")
group.add_argument("--preset-rm", action="store", metavar="str", help="Remove preset by NAME.")
group.add_argument("--ls", action="store_true", help="List available presets and watchlists.")

# Parser arguments setup
parser.add_argument("--preset-save", action="store", metavar="str",
                    help="Save command line options by NAME.")
parser.add_argument("-s", "--save", action="store_true", help="Save chart as png.")
parser.add_argument("-v", "--volume", action="store_true", help="Add Volume")
parser.add_argument("--rs", action="store_true", help="Dorsey Relative strength indicator.")
parser.add_argument("--m-rs", action="store_true", help="Mansfield Relative strength indicator.")
parser.add_argument("--tf", action="store", choices=("weekly", "daily"), default="daily",
                    help="Timeframe. Default 'daily'")
parser.add_argument("--sma", type=int, nargs="+", metavar="int", help="Simple Moving average")
parser.add_argument("--ema", type=int, nargs="+", metavar="int", help="Exponential Moving average")
parser.add_argument("--vol-sma", type=int, nargs="+", metavar="int", help="Volume Moving average")
parser.add_argument("-d", "--date", type=datetime.fromisoformat, metavar="str",
                    help="ISO format date YYYY-MM-DD.")
parser.add_argument("--period", action="store", type=int, metavar="int",
                    help=f"Number of Candles to plot. Default {instance.Config.PLOT_DAYS}")
parser.add_argument("--snr", action="store_true",help="Add Support and Resistance lines on chart")
parser.add_argument("-r", "--resume", action="store_true",
                    help="Resume a watchlist from last viewed chart.")
parser.add_argument("--dlv", action="store_true", help="Delivery Mode. Plot delivery data on chart.")

# Register Plugins
if len(instance.PLOT_PLUGINS):
    _.Plugins().register(instance.PLOT_PLUGINS, parser)

# Parse the arguments
args = parser.parse_args()
if args.tf == "weekly" and args.dlv:
    exit("WARN: Delivery mode is not supported on weekly timeframe.")

# Core function -> plot chart
plotter = _.Plot(args, parser=parser)
symbol_list = plotter.symbol_list

# Save args and preset
if args.preset:
    args = plotter.args
if args.save:
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor() as executor:
        for symbol in symbol_list:
            print("executing", symbol, flush=True)
            executor.submit(process_plot, plotter.plot(symbol), plotter.plot_args)
    exit("Done")

# PROMPT BETWEEN EACH CHART
plotter.idx = 0
plotter.len = len(symbol_list)
answer = "n"

if args.resume and hasattr(instance.Config, "PLOT_RESUME"):
    resume = getattr(instance.Config, "PLOT_RESUME")
    if resume["watch"] == args.watch:
        plotter.idx = resume["idx"]

while True:
    if answer in ("n", "p"):
        if plotter.idx == plotter.len:
            break
        print(f"{plotter.idx + 1} of {plotter.len}", flush=True, end="\r"*11)
        # Core function -> plot chart
        plotter.plot(symbol_list[plotter.idx])

    answer = plotter.key

    if answer == "n":
        if plotter.idx == plotter.len:
            exit("\nDone")
        plotter.idx += 1
    elif answer == "p":
        if plotter.idx == 0:
            print("\nAt first Chart")
            answer = ""
            continue
        plotter.idx -= 1
    elif answer == "q":
        if args.watch:
            userObj = instance.config_user() if instance.config_user().is_file() else {}
            userObj["PLOT_RESUME"] = {"watch": args.watch, "idx": plotter.idx}
            instance.config_user().save(userObj)
        exit("\nquiting")

print("\nDone")


