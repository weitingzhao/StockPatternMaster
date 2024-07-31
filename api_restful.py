import threading
from fastapi import FastAPI, HTTPException, Response

import src.api as api
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

refresh_scheduler: AsyncIOScheduler = AsyncIOScheduler()


@app.get("/")
async def root():
    return Response(content="Welcome to the stock pattern Master RestAPI")


@app.get("/refresh", response_model=api.SuccessResponse, include_in_schema=False)
async def refresh_everything():
    refresh_data()
    refresh_search()
    global last_refreshed
    last_refreshed = datetime.now()
    return api.SuccessResponse()


@app.get("/data/refresh", response_model=api.SuccessResponse, include_in_schema=False)
async def refresh_data():
    # TODO: hardcoded file prefix and folder
    # _find_and_remove_files(".", "data_holder_*.pk")
    # global data_holder
    # data_holder = _prepare_data()
    print("Data refreshed")
    return api.SuccessResponse(message="Existing data holder files removed, and a new one is created")


@app.get("/search/refresh", response_model=api.SuccessResponse, include_in_schema=False)
async def refresh_search():
    # TODO: hardcoded file prefix and folder
    # _find_and_remove_files(".", "search_tree_*.pk")
    # prepare_all_search_trees()
    print("Search trees are refreshed")
    return api.SuccessResponse()
