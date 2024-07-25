from src.instance import Instance


class SymbolsEngine:

    def __init__(self, instance: Instance):
        self._ = instance
        self.API_KEY = self._.Config.API_KEY_Alphavantage

    def fetch_stock_list(self):
        url = f'https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={self.API_KEY}'
        data = self._.web(url).request()
        self._.csv_tradings("symbols", f"FullSymbols.csv").save_str(data)

    def analyze_stock_list(self):
        # Load the stock list
        pd_symbols = self._.csv_tradings("symbols", "FullSymbols.csv").load()

        # step 1. Filter by status
        pd_active_symbols = pd_symbols[pd_symbols['status'] == 'Active']
        # step 2. Group by exchange and asset type
        pd_symbols_grouped = pd_active_symbols.groupby(['exchange', 'assetType'])
        # step 3. Export grouped data to separate lists
        pd_grouped_list = {name: group for name, group in pd_symbols_grouped}

        # Save symbols into separate csv files
        summary = {'count': {
            'total_exchanges': len(pd_active_symbols["exchange"].unique()),
            'total_derivatives': len(pd_active_symbols["assetType"]),
        }}
        for name, group in pd_grouped_list.items():
            exchange = name[0]
            derivative = name[1]
            csv = self._.csv_tradings("symbols", exchange, f"{derivative}.csv")
            csv.save_df(group)

            # Collect summary information
            if exchange not in summary:
                summary[exchange] = {}
            total = len(group)
            summary[exchange][derivative] = total

            # Ensure the dynamic key exists in summary before adding the total
            if derivative not in summary['count']:
                summary['count'][derivative] = 0
            summary['count'][derivative] += total

        self._.json("symbols", "summary.json").save(summary)
