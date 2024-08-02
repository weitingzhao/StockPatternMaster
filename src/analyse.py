from argparse import ArgumentParser
from src.service import Service
import src.analyses as analyse
from src.analyses.base_analyse import BaseAnalyse


class Analyse(BaseAnalyse):
    def __init__(self, service: Service):
        super().__init__(service)

    # analyses data
    def treading(self, args: ArgumentParser) -> analyse.TradingAnalyse:
        return analyse.TradingAnalyse(self.Service, args)

    def symbols(self) -> analyse.SymbolAnalyse:
        return analyse.SymbolAnalyse(self.Service)

    def pattern_list(self) -> list:
        return analyse.Pattern.get_pattern_list()

    def pattern_dict(self) -> dict:
        return analyse.Pattern.get_pattern_dict()
