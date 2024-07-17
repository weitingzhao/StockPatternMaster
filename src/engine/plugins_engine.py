from argparse import ArgumentParser
from importlib import import_module
from typing import Dict
from src.instance import Instance


class PluginsEngine:
    def __init__(self, instance: Instance):
        self._ = instance
        self.plugins =[]

    def register(self, plugins: Dict, parser: ArgumentParser):
        for plugin in plugins.values():
            instance = import_module(f'plugin.{plugin["name"]}')
            instance.load(parser)
            self.plugins.append(instance)

    def run(self, *args):
        for plugin in self.plugins:
            plugin.main(*args)
