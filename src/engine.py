from pathlib import Path
import src.engines as engine
from src.instance import Instance
import src.engines.loaders as loader


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
        return loader.JsonLoader(self.Instance.Config.FILE_user)

    #<editor-fold desc="Csv">
    def csv_tradings(self, *args) -> loader.CsvLoader:
        path = self.Instance.ROOT_Data.joinpath(*args)
        self.Instance.Path_exist(path)
        return loader.CsvLoader(path)

    #</editor-fold>

    #<editor-fold desc="Json">
    def json_Data(self, *args):
        return self.json(root=self.Instance.ROOT_Data, *args)

    def json_Research(self, *args):
        return self.json(root=self.Instance.ROOT_Research, *args)

    def json(self, root: Path, *args):
        path = root.joinpath(*args)
        self.Instance.Path_exist(path)
        return loader.JsonLoader(path)

    #</editor-fold>

    #<editor-fold desc="Web">
    def web(self, url: str) -> loader.WebLoader:
        return loader.WebLoader(self.Instance.logger, url)
    #</editor-fold>
