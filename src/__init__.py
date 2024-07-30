from logging import Logger
from .config import Config
from .instance import Instance
from .engine import Engine

# Step 1. Init Config
config = Config()

# Step 2. Init Instance
instance = Instance(config)
logger: Logger = instance.logger

# Step 3. Init Engine
engine = Engine(instance)


