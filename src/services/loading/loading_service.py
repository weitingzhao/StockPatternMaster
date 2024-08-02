from pathlib import Path

from src import Engine
from .loading_trading_service import LoadingTradingService


class LoadingService:
    def __init__(self, engine: Engine):
        self.engine = engine

    def trading(self, path: Path) -> LoadingTradingService:
        return LoadingTradingService(self.engine, path)
