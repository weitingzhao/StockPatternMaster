import sys
from argparse import ArgumentParser

from src.instance import Instance
from src.setting.config import Config
from utilities.tools import Tools
from pathlib import Path
import yfinance as yf

# Instance
instance = Instance(__name__)

# Group Init
parser = ArgumentParser(prog="init.py")
group = parser.add_mutually_exclusive_group()

# Group arguments setup
group.add_argument("-v", "--version", action="store_true", help="Print the current version.")
group.add_argument("-c", "--config", action="store_true", help="Print the current config.")

# Parse the arguments
args = parser.parse_args()
if args.version:
    exit(f"Stock Pattern Master - init.py: version {instance.Config.VERSION}")
if args.config:
    exit(str(instance.Config))

msft = yf.Ticker("MSFT")

# get all stock info
print(f"info: {msft.info}")

# get historical market data
hist = msft.history(period="1mo")

# show meta information about the history (requires history() to be called first)
print(f"meta data: {msft.history_metadata}")

# show actions (dividends, splits, capital gains)
print(f"actions: {msft.actions}")
print(f"dividends: {msft.dividends}")
print(f"splits: {msft.splits}")
print(f"capital gains: {msft.capital_gains}")  # only for mutual funds & etfs

# show share count
df = msft.get_shares_full(start="2022-01-01", end=None)
print(df)

print(instance)

