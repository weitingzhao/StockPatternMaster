import importlib.util
import logging
import sys
from pathlib import Path
from typing import Union, Type
from types import ModuleType

from src.setting.config import Config


class Helper:

    def __init__(self, config: Config):
        self.Config = config

    def configure_logger(self, name: str) -> logging.Logger:
        """Return a logger instance by name
        Creates a file handler to log messages with level WARNING and above
        Creates a stream handler to log messages with level INFO and above

        Parameters:
        name (str): Pass __name__ for module level logger
        """

        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        stdout_handler = logging.StreamHandler()
        stdout_handler.setLevel(logging.INFO)
        stdout_handler.setFormatter(logging.Formatter('[%(asctime)s - %(name)s] %(levelname)s: %(message)s'))

        file_handler = logging.FileHandler(self.Config.DIR / "error.log")
        file_handler.setLevel(logging.WARNING)
        file_handler.setFormatter(
            logging.Formatter('[%(asctime)s - %(name)s] %(levelname)s: %(message)s')
        )

        logger.addHandler(stdout_handler)
        logger.addHandler(file_handler)

        return logger

    def load_module(self, module_str: str) -> Union[ModuleType, Type]:
        """
        Load a module specified by the given string.

        Arguments
        module_str (str): Module filepath, optionally adding the class name
            with format <filePath>:<className>

        Raises:
        ModuleNotFoundError: If module is not found
        AttributeError: If class name is not found in module.

        Returns: ModuleType
        """
        class_name = None
        module_path = module_str

        if "|" in module_str:
            module_path, class_name = module_str.split("|")

        module_path = Path(module_path).expanduser().resolve()
        spec = importlib.util.spec_from_file_location(module_path.stem, module_path)

        if not spec or not spec.loader:
            raise ModuleNotFoundError(f"Module not found: {module_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_path.stem] = module

        spec.loader.exec_module(module)
        return getattr(module, class_name) if class_name else module

