import src.engine.pattern_engine as PatternEngine
from src.engine.plot_engine import PlotEngine
from src.engine.plugins_engine import PluginsEngine
from src.engine.symbols_enigne import SymbolsEngine
from src.engine.tradings_engine import TradingsEngine
from src.instance import Instance


class Engine:

    def __init__(self, instance: Instance):
        self.Instance = instance

    def Symbols(self) -> SymbolsEngine:
        return SymbolsEngine(self.Instance)

    def Tradings(self) -> TradingsEngine:
        return TradingsEngine(self.Instance)

    def Plugins(self) -> PluginsEngine:
        return PluginsEngine(self.Instance)

    def Plot(self, args, parser) -> PlotEngine:
        return PlotEngine(self.Instance, args, self.Plugins(), parser)

    def Pattern_List(self):
        return PatternEngine.get_pattern_dict()

    def Pattern(self, pattern: str):
        return self.Pattern_List()[pattern]

    def Pattern_Detector(self):
        return PatternEngine.PatternDetector(self.Instance)