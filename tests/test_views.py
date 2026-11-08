import json
from unittest.mock import patch

import pytest

from src.utils import filter_transactions_by_date
from src.views import get_cards_info, get_greeting, get_top_transactions, main_page


@pytest.mark.parametrize(
    "date, expected",
    [
        ("2026-12-01 05:59:59", "Доброй ночи"),
        ("2026-12-01 06:00:00", "Доброе утро"),
        ("2026-12-01 12:00:00", "Добрый день"),
        ("2026-12-01 18:00:00", "Добрый вечер"),
        ("2026-12-01 23:00:00", "Доброй ночи"),
    ],
)
def test_get_greeting(date: str, expected: str) -> None:
    """Проверка задания времени через параметризацию"""
    assert get_greeting(date) == expected


def test_get_cards_info() -> None:
    """Проверка получения информации с карты"""
    transactions = [
        {"Номер карты": "*7197", "Сумма платежа": -100.0},
        {"Номер карты": "*7197", "Сумма платежа": -50.0},
        {"Номер карты": "*5091", "Сумма платежа": -200.0},
        {"Номер карты": "*4556", "Сумма платежа": 5000.0},
    ]

    result = get_cards_info(transactions)

    assert result == [
        {"last_digits": "7197", "total_spent": 150.0, "cashback": 1.5},
        {"last_digits": "5091", "total_spent": 200.0, "cashback": 2.0},
    ]


def test_get_top_transactions() -> None:
    """Проверка на сортировку по сумме"""
    transactions = [
        {
            "Дата операции": "01.12.2021 10:00:00",
            "Сумма платежа": 100.0,
            "Категория": "Категория 1",
            "Описание": "Операция 1",
        },
        {
            "Дата операции": "02.12.2021 10:00:00",
            "Сумма платежа": 600.0,
            "Категория": "Категория 2",
            "Описание": "Операция 2",
        },
        {
            "Дата операции": "03.12.2021 10:00:00",
            "Сумма платежа": 300.0,
            "Категория": "Категория 3",
            "Описание": "Операция 3",
        },
        {
            "Дата операции": "04.12.2021 10:00:00",
            "Сумма платежа": 500.0,
            "Категория": "Категория 4",
            "Описание": "Операция 4",
        },
        {
            "Дата операции": "05.12.2021 10:00:00",
            "Сумма платежа": 200.0,
            "Категория": "Категория 5",
            "Описание": "Операция 5",
        },
        {
            "Дата операции": "06.12.2021 10:00:00",
            "Сумма платежа": 400.0,
            "Категория": "Категория 6",
            "Описание": "Операция 6",
        },
    ]

    result = get_top_transactions(transactions)

    assert result == [
        {
            "date": "02.12.2021",
            "amount": 600.0,
            "category": "Категория 2",
            "description": "Операция 2",
        },
        {
            "date": "04.12.2021",
            "amount": 500.0,
            "category": "Категория 4",
            "description": "Операция 4",
        },
        {
            "date": "06.12.2021",
            "amount": 400.0,
            "category": "Категория 6",
            "description": "Операция 6",
        },
        {
            "date": "03.12.2021",
            "amount": 300.0,
            "category": "Категория 3",
            "description": "Операция 3",
        },
        {
            "date": "05.12.2021",
            "amount": 200.0,
            "category": "Категория 5",
            "description": "Операция 5",
        },
    ]


def test_main_page() -> None:
    transactions = [
        {
            "Дата операции": "30.11.2021 12:00:00",
            "Номер карты": "*7197",
            "Сумма платежа": -1000.0,
            "Категория": "Супермаркеты",
            "Описание": "Магазин 1",
        },
        {
            "Дата операции": "15.12.2021 12:00:00",
            "Номер карты": "*7197",
            "Сумма платежа": -500.0,
            "Категория": "Супермаркеты",
            "Описание": "Магазин 2",
        },
        {
            "Дата операции": "25.12.2021 12:00:00",
            "Номер карты": "*7197",
            "Сумма платежа": -2000.0,
            "Категория": "Супермаркеты",
            "Описание": "Магазин 3",
        },
    ]

    with (
        patch("src.views.read_xlsx_file", return_value=transactions),
        patch(
            "src.views.read_user_settings",
            return_value={
                "user_currencies": ["USD"],
                "user_stocks": ["AAPL"],
            },
        ),
        patch(
            "src.views.get_currency_rates",
            return_value=[{"currency": "USD", "rate": 80.5}],
        ),
        patch(
            "src.views.get_stock_prices",
            return_value=[{"stock": "AAPL", "price": 344.31}],
        ),
    ):
        response = main_page("2021-12-20 15:30:00")
        data = json.loads(response)

        assert data["cards"][0]["last_digits"] == "7197"

        assert data["cards"][0]["total_spent"] == 500
        assert data["cards"][0]["cashback"] == 5

        assert len(data["top_transactions"]) == 1
        assert data["top_transactions"][0]["amount"] == -500
        assert isinstance(response, str)
        assert data["greeting"] == "Добрый день"
        assert data["currency_rates"] == [{"currency": "USD", "rate": 80.5}]
        assert data["stock_prices"] == [{"stock": "AAPL", "price": 344.31}]

        assert data["top_transactions"][0]["date"] == "15.12.2021"
        assert data["top_transactions"][0]["description"] == "Магазин 2"


@pytest.mark.parametrize(
    "transaction_date, expected_count",
    [
        ("30.11.2021 23:59:59", 0),
        ("01.12.2021 00:00:00", 1),
        ("20.12.2021 15:30:00", 1),
        ("20.12.2021 15:30:01", 0),
    ],
)
def test_filter_transactions_date_boundaries(
    transaction_date: str,
    expected_count: int,
) -> None:
    transactions = [{"Дата операции": transaction_date}]

    result = filter_transactions_by_date(
        transactions,
        "2021-12-20 15:30:00",
    )

    assert len(result) == expected_count


def test_get_top_transactions_with_negative_amounts() -> None:
    transactions = [
        {
            "Дата операции": "01.12.2021 10:00:00",
            "Сумма платежа": 1000.0,
            "Категория": "Пополнения",
            "Описание": "Пополнение",
        },
        {
            "Дата операции": "02.12.2021 10:00:00",
            "Сумма платежа": -9000.0,
            "Категория": "Переводы",
            "Описание": "Перевод",
        },
        {
            "Дата операции": "03.12.2021 10:00:00",
            "Сумма платежа": 200.0,
            "Категория": "Пополнения",
            "Описание": "Пополнение",
        },
    ]

    result = get_top_transactions(transactions)

    assert [item["amount"] for item in result] == [
        1000.0,
        200.0,
        -9000.0,
    ]
