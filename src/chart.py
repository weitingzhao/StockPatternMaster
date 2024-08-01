from argparse import ArgumentParser
import utilities as util
from src.analyse import Analyse
import src.charts as chart
from src.charts.base_chart import BaseChart


class Chart(BaseChart):
    def __init__(self, analyse: Analyse):
        super().__init__(analyse)

    def local_tradings(
            self,
            args,
            parser: ArgumentParser
    ) -> chart.TradingPatternChart:
        return chart.TradingPatternChart(
            self.Analyse,
            args,
            util.Plugin(),
            parser)

    def web_visualization(self) -> chart.TradingVisualizeChart:
        return chart.TradingVisualizeChart(self.Analyse)