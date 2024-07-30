from pathlib import Path
from src.instance import Instance
import src.engines as engine
from src.engines.loaders.csv_loader import CsvLoader
from src.engines.loaders.web_loader import WebLoader
from src.engines.loaders.json_loader import JsonLoader


class Engine:

    def __init__(self, instance: Instance):
        self.Instance = instance

    def Symbols(self) -> engine.Symbol:
        return engine.Symbol(self.Instance)

    def Tradings(self) -> engine.Trading:
        return engine.Trading(self.Instance)

    def Plugins(self) -> engine.Plugin:
        return engine.Plugin(self.Instance)

    def Plot(self, args, parser) -> engine.Plot:
        return engine.Plot(self.Instance, args, self.Plugins(), parser)

    def Pattern_List(self) -> list:
        return engine.get_pattern_list()

    def Pattern_Dict(self) -> dict:
        return engine.get_pattern_dict()

    def Pattern_Scan(self, args):
        return engine.PatternScan(self.Instance, args)

    def config_json(self):
        return JsonLoader(self.Instance.Config.FILE_user)

    def csv_tradings(self, *args) -> CsvLoader:
        path = self.Instance.ROOT_Data.joinpath(*args)
        self.Instance.Path_exist(path)
        return CsvLoader(path)

    def json_Data(self, *args):
        return self.json(root=self.Instance.ROOT_Data, *args)

    def json_Research(self, *args):
        return self.json(root=self.Instance.ROOT_Research, *args)

    def json(self, root: Path, *args):
        path = root.joinpath(*args)
        self.Instance.Path_exist(path)
        return JsonLoader(path)

    def web(self, url: str) -> WebLoader:
        return WebLoader(self.Instance.logger, url)
