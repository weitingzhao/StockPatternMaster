from pathlib import Path
from typing import Optional, Literal

from src import Engine
from .saving_plot_service import SavingPlotService
from src.services.loading.loader.abstract_loader import AbstractLoader


class SavingService:
    def __init__(self, engine: Engine):
        self.engine = engine

    def plot_trading(
            self,
            data,
            loader: AbstractLoader,
            save_folder: Optional[Path] = None,
            mode: Literal["default", "expand"] = "default",
    ) -> SavingPlotService:
        return SavingPlotService(self.engine, data, loader, save_folder,mode)
