from src.instance import Instance


# Define the function to fetch stock list
def fetch_stock_list():
    url = f'https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={api_key}'
    data = _.New_Web(url).request()
    _.New_Csv("symbols", f"FullSymbols.csv").save_str(data)


def analyze_stock_list():
    # Load the stock list
    pd_symbols = _.New_Csv("symbols", "FullSymbols.csv").load()

    # step 1. Filter by status
    pd_active_symbols = pd_symbols[pd_symbols['status'] == 'Active']
    # step 2. Group by exchange and asset type
    pd_symbols_grouped = pd_active_symbols.groupby(['exchange', 'assetType'])
    # step 3. Export grouped data to separate lists
    pd_grouped_list = {name: group for name, group in pd_symbols_grouped}

    # Save symbols into seperate csv files
    summary = {'count': {
        'total_exchanges': len(pd_active_symbols["exchange"].unique()),
        'total_derivatives': len(pd_active_symbols["assetType"]),
    }}
    for name, group in pd_grouped_list.items():
        exchange = name[0]
        derivative = name[1]
        csv = _.New_Csv("symbols", exchange, f"{derivative}.csv")
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

    _.New_Json("symbols", "summary.json").save(summary)


### Main Code ###
# Instance
_ = Instance(__name__)

# Alpha Vantage API Key
api_key = 'ZLV0FVBBQUBFWEZU'

# Step 1. Fetch Stock symbol from alphavantage API
# fetch_stock_list()
# Step 2. Analyze the stock lists
analyze_stock_list()

