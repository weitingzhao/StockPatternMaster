import sys
from argparse import ArgumentParser

from src.instance import Instance
from src.setting.config import Config
from utilities.helper import Helper
from pathlib import Path

# Instance
instance = Instance(__name__, Config(Path(__file__).parents[1]))

# Exception custom handler (Set the sys.excepthook)
sys.excepthook = instance.log_unhandled_exception

# Group Init
parser = ArgumentParser(prog="init.py")
group = parser.add_mutually_exclusive_group()

# Group arguments setup
group.add_argument("-v", "--version", action="store_true", help="Print the current version.")
group.add_argument("-c", "--config", action="store_true", help="Print the current config.")

# Parse the arguments
args = parser.parse_args()
if args.version:
    exit(f"Stock Pattern Master - init.py: version {instance.config.VERSION}")
if args.config:
    exit(str(instance.config))

print(instance)

