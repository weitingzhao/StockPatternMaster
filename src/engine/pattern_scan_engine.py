import json
import importlib
import concurrent
from tqdm import tqdm
from pathlib import Path
from datetime import datetime

from src.engine.Plotter import Plotter
from src.engine.plot_engine import PlotEngine
from src.instance import Instance
from argparse import ArgumentParser
from concurrent.futures import Future
from src.engine import pattern_detector_engine
from typing import Tuple, Callable, List, Optional
from src.plugin.pattern_detector import PatternDetector
from src.loaders.abstract_loader import AbstractLoader


class PatternScanEngine:

    def __init__(self, instance: Instance, args: ArgumentParser):
        # Setup instance, args, etc.
        self.instance = instance
        self.args = args
        self.PatternDetector = PatternDetector(self.instance)

        # Dynamically initialize the loader
        loader_name = self.instance.Config.__dict__.get("LOADER", "treading_data_loader:TreadingDataLoader")
        module_name, class_name = loader_name.split(":")
        loader_module = importlib.import_module(f"src.loaders.{module_name}")
        self.loader = getattr(loader_module, class_name)(
            config=self.instance.Config.__dict__,
            tf=args.tf,
            end_date=args.date)

    def cleanup(self, loader: AbstractLoader, futures: List[concurrent.futures.Future]):
        if futures:
            for future in futures:
                future.cancel()
            concurrent.futures.wait(futures)
        if loader.closed:
            loader.close()

    def scan_pattern(
            self,
            symbol: str,
            functions: Tuple[Callable, ...],
            loader: AbstractLoader,
            bars_left: int = 6,
            bars_right: int = 6
    ) -> List[dict]:

        patterns: List[dict] = []
        # Load symbol (default loader is csv trading_data_loader)
        df = loader.get(symbol)

        if df is None or df.empty:
            return patterns

        if df.index.has_duplicates:
            df = df[~df.index.duplicated()]

        pivots = self.PatternDetector.get_max_min(
            df=df,
            bars_left=bars_left,
            bars_right=bars_right)

        if not pivots.shape[0]:
            return patterns

        for function in functions:
            if not callable(function):
                raise TypeError(f"Expected callable. Got {type(function)}")
            try:
                result = function(self.PatternDetector, symbol, df, pivots)
            except Exception as e:
                self.instance.logger.exception(f"SYMBOL name: {symbol}", exc_info=e)
                return patterns
            if result:
                patterns.append(self.PatternDetector.make_serializable(result))

        return patterns

    def process_by_pattern(
            self,
            symbol_list: List,
            fns: Tuple[Callable, ...],
            futures: List[concurrent.futures.Future]
    ) -> List[dict]:
        patterns: List[dict] = []
        # Load or initialize state dict for storing previously detected patterns
        state = None
        state_file = None
        filtered = None

        if self.instance.Config.__dict__.get("SAVE_STATE", False) and self.args.file and not self.args.date:
            state_file = self.instance.DIR / f"state/{self.args.file.stem}_{self.args.pattern}.json"
            if not state_file.parent.is_dir():
                state_file.parent.mkdir(parents=True)
            state = json.loads(state_file.read_bytes()) if state_file.exists() else {}

        # determine the folder to save to in a case save option is set
        save_folder: Optional[Path] = None
        image_folder = f"{datetime.now():%d_%b_%y_%H%M}"
        if "SAVE_FOLDER" in self.instance.Config.__dict__:
            save_folder = Path(self.instance.Config.__dict__["SAVE_FOLDER"]) / image_folder
        if self.args.save:
            save_folder = self.args.save / image_folder
        if save_folder and not save_folder.exists():
            self.instance.Path_exist(save_folder)

        # begin a scan process
        with concurrent.futures.ProcessPoolExecutor() as executor:

            for sym in symbol_list:
                future = executor.submit(
                    self.scan_pattern,
                    symbol=sym,
                    functions=fns,
                    loader=self.loader,
                    bars_left=self.args.left,
                    bars_right=self.args.right)
                futures.append(future)

            for future in tqdm(
                    iterable=concurrent.futures.as_completed(futures),
                    total=len(futures)
            ):
                try:
                    result = future.result()
                except Exception as e:
                    self.cleanup(self.loader, futures)
                    self.instance.logger.exception("Error in Future - scaning patterns", exc_info=e)
                    return []
                patterns.extend(result)
            futures.clear()

            if state is not None:
                # if no args.file option, no need to save state, return patterns
                # Filter for newly detected patterns and remove stale patterns

                # list for storing newly detected patterns
                filtered = []
                # initial length of state dict
                len_state = len(state)
                # Will contain keys to all patterns currently detected
                detected = set()
                for dct in patterns:
                    # unique identifier
                    key = f'{dct["sym"]}-{dct["pattern"]}'
                    detected.add(key)
                    if not len_state:
                        # if the state is empty, this is a first run
                        # no need to filter
                        state[key] = dct
                        filtered.append(dct)
                        continue
                    if key in state:
                        if dct["start"] == state[key]["start"]:
                            # if the pattern starts on the same date,
                            # they are the same previously detected pattern
                            continue
                        # Else there is a new pattern for the same key
                        state[key] = dct
                        filtered.append(dct)
                    # new pattern
                    filtered.append(dct)
                    state[key] = dct
                # set difference - get keys in state dict not existing in detected
                # These are pattern keys no longer detected and can be removed
                invalid_patterns = set(state.keys()) - detected
                # Clean up stale patterns in state dict
                for key in invalid_patterns:
                    state.pop(key)
                if state_file:
                    state_file.write_text(json.dumps(state, indent=2))
                    self.instance.logger.info(
                        f"\nTo view all current market patterns, run `py init.py --plot state/{state_file.name}\n"
                    )

            patterns_to_output = patterns if state is None else filtered
            if not patterns_to_output:
                return []
            # Save the images if required
            if save_folder:
                plotter = Plotter(
                    data=None,
                    loader=self.loader,
                    save_folder=save_folder)
                for i in patterns_to_output:
                    future = executor.submit(plotter.save, i.copy())
                    futures.append(future)

                self.instance.logger.info("Saving images")

                for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
                    try:
                        future.result()
                    except Exception as e:
                        self.cleanup(self.loader, futures)
                        self.instance.logger.exception("Error in Futures - Saving images ", exc_info=e)
                        return []

        patterns_to_output.append({
            "timeframe": self.loader.timeframe,
            "end_date": self.args.date.isoformat() if self.args.date else None,
        })
        return patterns_to_output

    def process_by_pattern_name(
            self,
            symbol_list: List,
            pattern_name: str,
            futures: List[concurrent.futures.Future]
    ) -> List[dict]:

        fn_dict = pattern_detector_engine.get_pattern_dict()
        key_list = pattern_detector_engine.get_pattern_list()
        # Get function out
        fn = fn_dict[pattern_name]

        # check functions
        if callable(fn):
            fns = (fn,)
        elif fn == "bull":
            bull_list = ("vcpu", "hnsu", "dbot")
            fns = tuple(v for k, v in fn_dict.items() if k in bull_list and callable(v))
        elif fn == "bear":
            bear_list = ("vcpd", "hnsd", "dtop")
            fns = tuple(v for k, v in fn_dict.items() if k in bear_list and callable(v))
        else:
            fns = tuple(v for k, v in fn_dict.items() if k in key_list[3:] and callable(v))

        try:
            return self.process_by_pattern(symbol_list, fns, futures)
        except KeyboardInterrupt:
            self.cleanup(self.loader, futures)
            self.instance.logger.info("User exit")
            exit()
