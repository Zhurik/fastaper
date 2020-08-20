"""
Необходимые для работы приложения функции и модели
"""

from datetime import date as date_type

from typing import List, Dict

from pydantic import BaseModel

from models import CargoRate


class CargoPrice(BaseModel):
    """
    Модель для расчета стоимости груза
    """

    date: date_type
    cargo_type: str
    price: float
    calculated_price: float = None


class Cargo(BaseModel):
    """
    Модель тарифа для груза
    """

    cargo_type: str
    rate: str


async def save_rates(rates: Dict[date_type, List[Cargo]]) -> int:
    """
    Логика сохранения данных в БД
    """

    done = 0

    for date in rates:
        for cargo in rates[date]:
            if await CargoRate.get(
                    date=date,
                    cargo_type=cargo.cargo_type
            ).count() == 0:
                await CargoRate.create(
                    date=date,
                    cargo_type=cargo.cargo_type,
                    rate=cargo.rate
                )

                done += 1

    return done


async def process_cargo_prices(prices_data: List[CargoPrice]) -> List[CargoPrice]:
    """
    Логика обработки входящих запросов
    """

    for item in prices_data:
        data = await CargoRate.get(
            date=item.date,
            cargo_type=item.cargo_type
        ).values("rate")

        if len(data) != 0:
            item.calculated_price = item.price * data[0]["rate"]
        else:
            item.calculated_price = None

    return prices_data
