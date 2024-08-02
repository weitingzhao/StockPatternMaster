from src.analyse import Analyse
from src.analyses.base_analyse import BaseAnalyse


class BaseChart(BaseAnalyse):

    def __init__(self, analyse: Analyse):
        super().__init__(analyse._service)
        self._analyse = analyse
