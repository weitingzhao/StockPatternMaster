import json
import time
from pathlib import Path
from typing import List

import pandas as pd
from tqdm import tqdm

from src.instance import Instance
import yfinance as yf


class TradingsEngine:
    def __init__(self, instance: Instance):
        self._ = instance

    def logging_process_time(
            self,
            name: str,
            logging_file_path: Path,
            method_to_run, *args, **kwargs):
        # log start time
        start_time = time.time()

        # **run the provided method**
        method_to_run(*args, **kwargs)

        # log summary
        end_time = time.time()
        total_time = end_time - start_time
        total_time_hours = int(total_time // 3600)
        total_time_minutes = int((total_time % 3600) // 60)
        total_time_seconds = int(total_time % 60)
        process_result = {
            "start_process_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time)),
            "end_process_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time)),
            "total_process_time_seconds": f"{total_time_hours}h {total_time_minutes}m {total_time_seconds}s"
        }
        if logging_file_path.exists():
            with open(logging_file_path, 'r', encoding='utf-8') as status_file:
                existing_data = json.load(status_file)
        else:
            existing_data = {}
        if name in existing_data:
            existing_data[name].update(process_result)
        else:
            existing_data[name] = process_result
        with open(logging_file_path, 'w', encoding='utf-8') as status_file:
            json.dump(existing_data, status_file, indent=4)

    def fetch_tradings_history(
            self,
            name: str,
            symbols: List[str] = None,
            period="1d"):
        def main_process():
            tickers = yf.Tickers(" ".join(symbols))
            for ticker_symbol in tqdm(symbols, desc=f"Fetching {name} trading history"):
                try:
                    # get ticker object
                    ticker = tickers.tickers[ticker_symbol]
                    # Save the history to a csv file
                    history = ticker.history(period=period)
                    self._.csv_tradings("daily", f"{ticker_symbol}.csv").save_df(history)
                except Exception as e:
                    self._.logger.error(f"Error: fetch {ticker_symbol} trading history - got Error:{e}")

        # run main_process with logging
        self.logging_process_time(
            name,
            logging_file_path=self._.FOLDER_Watch / "tradings_fetch_status.json",
            method_to_run=main_process)

    def fetch_tradings_history_by_mylist(
            self,
            period="1d"):
        self.fetch_tradings_history(
            name="mylist",
            symbols=self._.LIST_Watch,
            period=period)

    def fetch_tradings_history_by_sector_or_industry(
            self,
            category: str,
            category_names: List[str],
            period="1d"):
        # get symbol list base on category (sector or industry)
        json_file_path = self._.FOLDER_Watch / f"symbols_{category}.json"
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        for category_name in category_names:
            if category_name in data["detail"]:
                symbols = data["detail"][category_name]
                # fetch trading history
            self.fetch_tradings_history(f"{category}.{category_name}", symbols, period)

    def fetch_symbols_info(self):
        full_symbols = pd.read_csv(self._.FOLDER_Symbols / "FullSymbols.csv")
        full_symbols["symbol"] = full_symbols["symbol"].astype(str)
        symbols = full_symbols["symbol"].tolist()
        # symbols = ["BC","BC/PA"]
        symbols_str = " ".join(symbols)
        tickers = yf.Tickers(symbols_str)

        error_path = self._.Path_exist(self._.FILE_Infos_Errors)
        if error_path.exists():
            with open(error_path.resolve(), "w"):
                pass

        for symbol in tqdm(symbols, desc="Fetching symbol info"):
            try:
                # get ticker object
                ticker = tickers.tickers[symbol]
                # get info & quote type
                ticker_info = ticker.info
                if "quoteType" in ticker_info:
                    quote_type = ticker_info["quoteType"]
                else:
                    quote_type = "unknown"
                # Save the history to a csv file
                self._.json_Data("infos", f"{quote_type}", f"{symbol}.json").save(ticker_info)
            except Exception as e:
                with open(error_path.resolve(), "a") as error_file:
                    error_file.write(f"{symbol}\n")
                print(f"Error: fetch {symbol} info - got Error:{e}")

    def fetch_single(self, symbol: str):
        msft = yf.Ticker("MSFT")

        # get all stock info
        print(f"info: {msft.info}")

        # get historical market data
        hist = msft.history(period="1mo")

        # show meta-information about the history (requires history() to be called first)
        print(f"meta data: {msft.history_metadata}")

        # show actions (dividends, splits, capital gains)
        print(f"actions: {msft.actions}")
        print(f"dividends: {msft.dividends}")
        print(f"splits: {msft.splits}")
        print(f"capital gains: {msft.capital_gains}")  # only for mutual funds & etfs

        # show share count
        df = msft.get_shares_full(start="2022-01-01", end=None)
        print(df)
