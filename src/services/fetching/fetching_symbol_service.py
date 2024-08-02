import json
import io
import pandas as pd
from pandas import Series, Timestamp
from typing import List, Hashable
import yfinance as yf
from tqdm import tqdm

from src.engine import Engine
from src.services.base_service import BaseService


def asset_type(asset_type: str) -> int:
    if asset_type == "Stock":
        return 1
    elif asset_type == "ETF":
        return 2
    elif asset_type == "Index":
        return 3
    elif asset_type == "Mutual Fund":
        return 4
    else:
        return -1


def DATE2(value: str) -> object | Timestamp | Timestamp:
    if pd.isna(value):
        return None
    return pd.to_datetime(value)


class FetchingSymbolService(BaseService):

    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.API_KEY = self._config.API_KEY_Alphavantage

    def fetch_stock_info_to_db(self):

        # url = f'https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={self.API_KEY}'
        # data = self._engine.web(url).request()

        df_source = pd.read_csv(self._config.FOLDER_Symbols / "FullSymbols.csv")

        # symbol data
        # df_source = pd.read_csv(io.StringIO(data))  # Create DataFrame
        # df_source["ipoDate"] = pd.to_datetime(df_source['ipoDate'], errors='coerce')
        # df_source["delistingDate"] = pd.to_datetime(df_source['delistingDate'], errors='coerce')

        # sql query
        sql_query = """
                        INSERT INTO symbol (symbol, name, market, asset_type, ipo_date, delisting_date, status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (symbol) DO UPDATE SET
                            name = EXCLUDED.name,
                            market = EXCLUDED.market,
                            asset_type = EXCLUDED.asset_type,
                            ipo_date = EXCLUDED.ipo_date,
                            delisting_date = EXCLUDED.delisting_date,
                            status = EXCLUDED.status
                    """

        # insert function
        def insert_fn(_: Hashable, row: Series):
            return (
                row.get('symbol', default="null"),
                row.get('name', default="null"),
                row.get('exchange', default="null"),
                asset_type(row.get('assetType', default="NULL")),
                DATE2(row.get('ipoDate')),
                DATE2(row.get('delistingDate')),
                row['status'] == "Active",
            )

        self._engine.db().save_df(
            sql_query=sql_query,
            df_source=df_source,
            execute_func=insert_fn
        )

    def fetch_symbols_info(self):
        full_symbols = pd.read_csv(self._config.FOLDER_Symbols / "FullSymbols.csv")
        full_symbols["symbol"] = full_symbols["symbol"].astype(str)
        symbols = full_symbols["symbol"].tolist()
        # symbols = ["BC","BC/PA"]
        symbols_str = " ".join(symbols)
        tickers = yf.Tickers(symbols_str)

        error_path = self.path_exist(self._config.FILE_Infos_Errors)
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
                # Save the treading to a csv file
                self._.json_Data("infos", f"{quote_type}", f"{symbol}.json").save(ticker_info)
            except Exception as e:
                with open(error_path.resolve(), "a") as error_file:
                    error_file.write(f"{symbol}\n")
                print(f"Error: fetch {symbol} info - got Error:{e}")

    def showing_symbol_info_single(self, symbol: str):
        ticker = yf.Ticker(symbol.upper())

        # get all stock info
        print(f"info: {ticker.info}")

        # get historical market data
        hist = ticker.history(period="1mo")

        # show meta-information about the treading (requires treading() to be called first)
        print(f"meta data: {ticker.history_metadata}")

        # show actions (dividends, splits, capital gains)
        print(f"actions: {ticker.actions}")
        print(f"dividends: {ticker.dividends}")
        print(f"splits: {ticker.splits}")
        print(f"capital gains: {ticker.capital_gains}")  # only for mutual funds & etfs

        # show share count
        df = ticker.get_shares_full(start="2022-01-01", end=None)
        print(df)
