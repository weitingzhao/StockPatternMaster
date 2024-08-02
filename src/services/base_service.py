from src.engine import Engine
from src.engines.base_engine import BaseEngine


class BaseService(BaseEngine):
    def __init__(self, engine: Engine):
        super().__init__(engine._config)
        self._engine = engine

