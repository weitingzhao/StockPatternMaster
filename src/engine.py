from src import Config
from pathlib import Path
import src.engines as engine
import utilities as util
from src.engines.base_engine import BaseEngine


class Engine(BaseEngine):
    def __init__(self, config: Config):
        super().__init__(config)

    def web(self, url: str) -> engine.WebEngine:
        return engine.WebEngine(self._config, url)

    def db(self) -> engine.PgSqlEngine:
        return engine.PgSqlEngine(self._config)

    def json_data(self, *args):
        return self.json(root=self._config.ROOT_Data, *args)

    def json_research(self, *args):
        return self.json(root=self._config.ROOT_Research, *args)

    def json_user(self):
        return self.json(root=self._config.FILE_user)

    def json(self, root: Path, *args):
        path = self.path_exist(root.joinpath(*args))
        return engine.JsonEngine(self._config, path)

    def csv(self, *args) -> engine.CsvEngine:
        path = self._config.ROOT_Data.joinpath(*args)
        self.path_exist(path)
        return engine.CsvEngine(self._config, path)

    def plugin(self) -> util.Plugin:
        return util.Plugin()