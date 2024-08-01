import threading
from typing import List

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException

import src.controller.api as api
import src as src
from datetime import datetime
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Download and prepare new data when app starts
    # This is started in the bg as app needs to start-up in less than 60secs (for Heroku)
    threading.Thread(target=refresh_everything).start()

    # Refresh data after every market close
    # TODO: set the timezones and add multiple refresh jobs for the multiple market closes
    refresh_scheduler.add_job(func=refresh_everything, trigger="cron", day="*", hour=8, minute=35)
    refresh_scheduler.add_job(func=refresh_everything, trigger="cron", day="*", hour=15, minute=35)
    refresh_scheduler.start()
    yield
    # Clean up the ML models and release the resources


app = FastAPI(lifespan=lifespan)


SYMBOL_LIST = []
PERIOD_YEARS = 10

def _prepare_data(force_update: bool = False) -> api.RawStockDataHolder:
    return api.initialize_data_holder(tickers=SYMBOL_LIST, period_years=PERIOD_YEARS, force_update=force_update)

def _date_to_str(date):
    return pd.to_datetime(date).strftime("%Y-%m-%d")

refresh_scheduler: AsyncIOScheduler = AsyncIOScheduler()
data_holder = api.RawStockDataHolder = _prepare_data()

@app.get("/match/symbols", response_model=api.AvailableSymbolsResponse, tags=["search"])
async def match_symbols():
    symbols = src.engine.symbols().analyse_stock_symbols()
    symbollist:List[str] = symbols
    return api.AvailableSymbolsResponse(symbols=symbollist)



@app.get("/data/refresh", response_model=api.SuccessResponse, include_in_schema=False)
async def refresh_data():
    # TODO: hardcoded file prefix and folder
    # _find_and_remove_files(".", "data_holder_*.pk")
    # global data_holder
    # data_holder = _prepare_data()
    print("Data refreshed")
    return api.SuccessResponse(message="Existing data holder files removed, and a new one is created")


@app.get("/refresh", response_model=api.SuccessResponse, include_in_schema=False)
async def refresh_everything():
    # refresh_data()
    # refresh_search()
    global last_refreshed
    last_refreshed = datetime.now()
    print ("Everything refreshed")
    return api.SuccessResponse()


@app.get("/search/prepare/{window_size}", response_model=api.SuccessResponse, include_in_schema=False)
def prepare_search_tree(window_size: int, force_update: bool = False):
    global search_tree_dict
    search_tree_dict[window_size] = api.initialize_search_tree(data_holder=data_holder,
                                                               window_size=window_size,
                                                               force_update=force_update)
    return api.SuccessResponse()

@app.get("/search/recent/", response_model=api.TopKSearchResponse, tags=["search"])
async def search_most_recent(symbol: str, window_size: int = 5, top_k: int = 5, future_size: int = 5):
    symbol = symbol.upper()
    try:
        label = api.RawStockDataHolder. data_holder.symbol_to_label[symbol]
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Ticker symbol {symbol} is not supported")
    most_recent_values = data_holder.values[label][:window_size]

    try:
        search_tree = search_tree_dict[window_size]
    except KeyError:
        raise HTTPException(status_code=400, detail=f"No prepared {window_size} day search window")

    top_k_indices, top_k_distances = search_tree.search(values=most_recent_values, k=top_k + 1)
    # We need to discard the first item, as that is our search sequence
    top_k_indices = top_k_indices[1:]
    top_k_distances = top_k_distances[1:]

    forecast_values = []
    matches = []

    for index, distance in zip(top_k_indices, top_k_distances):
        ticker = search_tree.get_window_symbol(index)
        start_date, end_date = search_tree.get_start_end_date(index)

        start_date_str = _date_to_str(start_date)
        end_date_str = _date_to_str(end_date)

        window_with_future_values = search_tree.get_window_values(index=index, future_length=future_size)
        todays_value = window_with_future_values[-window_size]
        future_value = window_with_future_values[0]
        diff_from_today = todays_value - future_value

        match = api.MatchResponse(symbol=ticker,
                                  distance=distance,
                                  start_date=start_date_str,
                                  end_date=end_date_str,
                                  todays_value=todays_value,
                                  future_value=future_value,
                                  change=diff_from_today,
                                  values=window_with_future_values.tolist())

        matches.append(match)

        forecast_values.append(diff_from_today)

    tmp = np.where(np.array(forecast_values) < 0, 0, 1)
    forecast_confidence = np.sum(tmp) / len(tmp)
    forecast_type = "gain"
    if forecast_confidence <= 0.5:
        forecast_type = "loss"
        forecast_confidence = 1 - forecast_confidence

    top_k_match = api.TopKSearchResponse(matches=matches,
                                         forecast_type=forecast_type,
                                         forecast_confidence=forecast_confidence,
                                         anchor_symbol=symbol,
                                         window_size=window_size,
                                         top_k=top_k,
                                         future_size=future_size,
                                         anchor_values=most_recent_values.tolist())

    return top_k_match

