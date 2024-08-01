from logging import Logger
from .utilities import Tools
from .config import Config
from .engine import Engine
from .instance import Instance
from .service import Service
from .analyse import Analyse
from .chart import Chart

# Step 1. Init Config
config = Config()
logger: Logger = config.logger
tools: Tools = Tools(config.logger)
# tier 2. Base on Config init Engine
engine = Engine(config)
# Step 3. Base on Engine init Service
service = Service(engine)
# Step 4. Base on Service init Analyze
analyse = Analyse(service)
# Step 5. Base on Analyze init Chart
chart = Chart(analyse)
