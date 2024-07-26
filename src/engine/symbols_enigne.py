import json
from pathlib import Path

import pandas as pd

from src.instance import Instance


class SymbolsEngine:

    def __init__(self, instance: Instance):
        self._ = instance
        self.API_KEY = self._.Config.API_KEY_Alphavantage

    def fetch_full_stock_list(self):
        url = f'https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={self.API_KEY}'
        data = self._.web(url).request()
        self._.csv_tradings("symbols", f"FullSymbols.csv").save_str(data)

    def analyze_stock_list(self):
        # Load the stock list
        pd_symbols = pd.read_csv(self._.FOLDER_Symbols / "FullSymbols.csv")

        # step 1. Filter by status
        pd_active_symbols = pd_symbols[pd_symbols['status'] == 'Active']
        # step 2. Group by exchange and asset type
        pd_symbols_grouped = pd_active_symbols.groupby(['exchange', 'assetType'])
        # step 3. Export grouped data to separate lists
        pd_grouped_list = {name: group for name, group in pd_symbols_grouped}

        # Category 1.a Save symbols into separate csv files
        json_symbols = {'count': {
            'total_exchanges': len(pd_active_symbols["exchange"].unique()),
            'total_derivatives': len(pd_active_symbols["assetType"]),
        }}
        for name, group in pd_grouped_list.items():
            exchange = name[0]
            derivative = name[1]
            csv = self._.csv_tradings("symbols", "exchange", exchange, f"{derivative}.csv")
            csv.save_df(group)

            # Collect json_symbols information
            if exchange not in json_symbols:
                json_symbols[exchange] = {}
            total = len(group)
            json_symbols[exchange][derivative] = total

            # Ensure the dynamic key exists in json_symbols before adding the total
            if derivative not in json_symbols['count']:
                json_symbols['count'][derivative] = 0
            json_symbols['count'][derivative] += total
        # Category 1.b Symbols json_symbols
        self._.json_Research("watch", "symbols_summary.json").save(json_symbols)

        # Category 2. Equity by Sector & Industry
        json_file_sector = self._.Path_exist(self._.FOLDER_Watch / "symbols_sector.json")
        json_file_industry = self._.Path_exist(self._.FOLDER_Watch / "symbols_industry.json")

        json_symbols_sector = {}
        json_symbols_industy = {}
        for json_file in  (self._.FOLDER_Infos / "EQUITY").glob("*.json"):
            with (open(json_file, "r")) as file:
                data = json.load(file)
                sector = data.get("sector", "Unknown")
                industry = data.get("industry", "Unknown")
                symbol = data.get("symbol", "Unknown")

                # sector
                if sector not in json_symbols_sector:
                    json_symbols_sector[sector] = []
                json_symbols_sector[sector].append(symbol)
                # industry
                if industry not in json_symbols_industy:
                    json_symbols_industy[industry] = []
                json_symbols_industy[industry].append(symbol)

        with open(json_file_sector, "w", encoding='utf-8') as json_file:
            json.dump({
                "summary": {sector: len(symbols) for sector, symbols in json_symbols_sector.items()},
                "detail": json_symbols_sector
            }, json_file, ensure_ascii=False, indent=4)
        with open(json_file_industry, "w", encoding='utf-8') as json_file:
            json.dump({
                "summary": {sector: len(symbols) for sector, symbols in json_symbols_industy.items()},
                "detail": json_symbols_industy
            }, json_file, ensure_ascii=False, indent=4)

