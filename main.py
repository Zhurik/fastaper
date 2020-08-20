"""
Основной модуль приложения
"""

import os
import json

from typing import Optional, Dict, List

import datetime
from datetime import date as date_type

from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every

from tortoise.contrib.fastapi import register_tortoise

from utils import save_rates, process_cargo_prices, CargoPrice, Cargo

JSON_PATH = "../example.json"


app = FastAPI()


@app.on_event("startup")
@repeat_every(seconds=2, wait_first=True, max_repetitions=1, raise_exceptions=True)
async def load_from_json() -> None:
    """
    Загружаем начальные значения из JSON
    """

    rows_updated = 0

    if os.path.isfile(JSON_PATH):
        with open(JSON_PATH, "r") as file:
            data = json.load(file)

        rates_data = {}

        for str_date in data:
            date = datetime.datetime.strptime(str_date, "%Y-%m-%d")
            rates_data[date] = []
            for cargo in data[str_date]:
                rates_data[date].append(
                    Cargo(
                        cargo_type=cargo["cargo_type"],
                        rate=cargo["rate"]
                    )
                )

        rows_updated = await save_rates(rates_data)

    print(f"При запуске было добавлено {rows_updated} строк")


@app.post("/add_rates")
async def add_rates(rates: Dict[date_type, List[Cargo]]):
    """
    Получаем новые тарифы из JSON
    """

    rows_saved = await save_rates(rates)

    return {"rows_saved": rows_saved}


@app.get("/rate")
async def get_prices(
        price: Optional[int] = None,
        cargo_type: Optional[str] = None,
        date: Optional[date_type] = None,
        prices_data: Optional[List[CargoPrice]] = None
):
    """
    Считаем тариф для полученного запроса
    """

    if prices_data:
        return await process_cargo_prices(prices_data)

    elif price and cargo_type and date:
        prices_data = [CargoPrice(
            date=date,
            cargo_type=cargo_type,
            price=price
        )]

        return await process_cargo_prices(prices_data)

    elif price or cargo_type or date:
        return [{
            "price": price or "Missing price",
            "cargo_type": cargo_type or "Missing cargo_type",
            "date": date or "Missing date"
        }]

    else:
        return {"Error": "Missing everything"}


register_tortoise(
    app,
    db_url="postgres://postgres:docker@db:5432/postgres",
    modules={
        "models": ["models"]
    },
    generate_schemas=True,
    add_exception_handlers=True,
)
