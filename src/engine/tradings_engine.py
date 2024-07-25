import json
from typing import List

import pandas as pd
from tqdm import tqdm

from src.instance import Instance
import yfinance as yf


class TradingsEngine:
    def __init__(self, instance: Instance):
        self._ = instance

    def fetch_tradings_history(self, period="1d"):
        tickers = yf.Tickers(" ".join(self._.LIST_Watch))
        for ticker_symbol in self._.LIST_Watch:
            # get ticker object
            ticker = tickers.tickers[ticker_symbol]
            # Save the history to a csv file
            history = ticker.history(period=period)
            self._.csv_tradings("tradings", f"{ticker_symbol}.csv").save_df(history)

    def fetch_info(self):
        full_symbols = pd.read_csv(self._.FOLDER_Symbols / "FullSymbols.csv")
        full_symbols["symbol"] = full_symbols["symbol"].astype(str)
        symbols = full_symbols["symbol"].tolist()
        # symbols = ["BC","BC/PA"]
        symbols_str = " ".join(symbols)
        tickers = yf.Tickers(symbols_str)

        error_path = self._.Path_exist(self._.DIR / self._.Config.FOLDER_Data / "infos" / "errors.json")
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
                self._.json("infos", f"{quote_type}", f"{symbol}.json").save(ticker_info)
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
