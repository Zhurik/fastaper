"""
Тестируем
"""

import asyncio
from datetime import date
from typing import Generator

import pytest
from fastapi.testclient import TestClient

from tortoise.contrib.test import finalizer, initializer
from main import app
from models import CargoRate


TEST_YEAR = 1990
TEST_MONTH = 1
TEST_DAY = 1
TEST_PRICE = 100

TEST_CARGO = "Test box"


@pytest.fixture(scope="module")
def client() -> Generator:
    initializer(["models"])
    with TestClient(app) as c:
        yield c
    finalizer()


@pytest.fixture(scope="module")
def event_loop(client: TestClient) -> Generator:
    yield client.task.get_loop()


async def get_and_delete_user():
    """
    Подчищаем тестовую запись
    """
    test_row = await CargoRate.get(
        date=date(
            TEST_YEAR,
            TEST_MONTH,
            TEST_DAY
        ),
        cargo_type=TEST_CARGO
    )

    await test_row.delete()

    assert await CargoRate.get(
        date=date(
            TEST_YEAR,
            TEST_MONTH,
            TEST_DAY
        ),
        cargo_type=TEST_CARGO
    ).count() == 0


def test_create_cargo_rate(client: TestClient, event_loop: asyncio.AbstractEventLoop):
    response = client.post("/add_rates", json={
        f"{TEST_YEAR}-{TEST_MONTH}-{TEST_DAY}": [{
            "cargo_type": TEST_CARGO,
            "rate": "0.1"
        }]
    })

    assert response.status_code == 200, response.text

    data = response.json()

    assert "rows_saved" in data
    assert data["rows_saved"] == 1

    event_loop.run_until_complete(get_and_delete_user())


def test_rate_json(client: TestClient, event_loop: asyncio.AbstractEventLoop):
    client.post("/add_rates", json={
        f"{TEST_YEAR}-{TEST_MONTH}-{TEST_DAY}": [{
            "cargo_type": TEST_CARGO,
            "rate": "0.1"
        }]
    })

    response = client.get("/rate", json=[{
        "date": f"{TEST_YEAR}-{TEST_MONTH}-{TEST_DAY}",
        "cargo_type": TEST_CARGO,
        "price": TEST_PRICE
    }])

    assert response.status_code == 200, response.text

    data = response.json()

    assert "calculated_price" in data[0]
    assert data[0]["calculated_price"] == 10

    event_loop.run_until_complete(get_and_delete_user())


def test_rate_url(client: TestClient, event_loop: asyncio.AbstractEventLoop):
    client.post("/add_rates", json={
        f"{TEST_YEAR}-{TEST_MONTH}-{TEST_DAY}": [{
            "cargo_type": TEST_CARGO,
            "rate": "0.1"
        }]
    })

    response = client.get(f"/rate?date={TEST_YEAR}-{TEST_MONTH}-{TEST_DAY}&cargo_type={TEST_CARGO}&price={TEST_PRICE}")

    assert response.status_code == 200, response.text

    data = response.json()

    assert "calculated_price" in data[0]
    assert data[0]["calculated_price"] == 10

    event_loop.run_until_complete(get_and_delete_user())


def test_rate_url_missing(client: TestClient, event_loop: asyncio.AbstractEventLoop):
    client.post("/add_rates", json={
        f"{TEST_YEAR}-{TEST_MONTH}-{TEST_DAY}": [{
            "cargo_type": TEST_CARGO,
            "rate": "0.1"
        }]
    })

    response = client.get(f"/rate?date={TEST_YEAR}-{TEST_MONTH}-02&cargo_type={TEST_CARGO}&price={TEST_PRICE}")

    assert response.status_code == 200, response.text

    data = response.json()

    assert "calculated_price" in data[0]
    assert data[0]["calculated_price"] == None

    event_loop.run_until_complete(get_and_delete_user())


def test_rate_wrong_url(client: TestClient, event_loop: asyncio.AbstractEventLoop):
    client.post("/add_rates", json={
        f"{TEST_YEAR}-{TEST_MONTH}-{TEST_DAY}": [{
            "cargo_type": TEST_CARGO,
            "rate": "0.1"
        }]
    })

    response = client.get(f"/rate?date={TEST_YEAR}-{TEST_MONTH}-{TEST_DAY}&cargo_type={TEST_CARGO}")

    assert response.status_code == 200, response.text

    data = response.json()

    assert data[0]["price"] == "Missing price"

    event_loop.run_until_complete(get_and_delete_user())


def test_rate_wrong_everything(client: TestClient, event_loop: asyncio.AbstractEventLoop):
    client.post("/add_rates", json={
        f"{TEST_YEAR}-{TEST_MONTH}-{TEST_DAY}": [{
            "cargo_type": TEST_CARGO,
            "rate": "0.1"
        }]
    })

    response = client.get(f"/rate")

    assert response.status_code == 200, response.text

    data = response.json()

    assert data == {"Error": "Missing everything"}

    event_loop.run_until_complete(get_and_delete_user())
