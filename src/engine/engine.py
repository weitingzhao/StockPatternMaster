from src.instance import Instance
from src.engine.plot_engine import PlotEngine
from src.engine import pattern_detector_engine
from src.engine.plugins_engine import PluginsEngine
from src.engine.symbols_enigne import SymbolsEngine
from src.engine.tradings_engine import TradingsEngine
from src.engine.pattern_scan_engine import PatternScanEngine


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

    def Pattern_List(self) -> list:
        return pattern_detector_engine.get_pattern_list()

    def Pattern_Dict(self) -> dict:
        return pattern_detector_engine.get_pattern_dict()

    def Pattern_Scan(self, args):
        return PatternScanEngine(self.Instance, args)


