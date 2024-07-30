import yfinance as yf

# Specify the stock ticker symbol
ticker_symbol = 'AAPL'

# Fetch the stock data
stock_data = yf.Ticker(ticker_symbol)

# Fetch historical market data for the past year
historical_data = stock_data.history(period="1y")
print("Historical Market Data:\n", historical_data.head())

# Fetch dividends
dividends = stock_data.dividends
print("\nDividends:\n", dividends)

# Fetch stock splits
splits = stock_data.splits
print("\nStock Splits:\n", splits)