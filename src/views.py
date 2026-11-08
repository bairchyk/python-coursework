import json
from datetime import datetime
from pathlib import Path

import pandas as pd

from src.external_api import get_currency_rates, get_stock_prices
from src.utils import filter_transactions_by_date, read_user_settings, read_xlsx_file

BASE_DIR = Path(__file__).resolve().parent.parent


def get_greeting(date: str) -> str:
    """Возвращает приветствие в зависимости от времени."""
    hour = datetime.strptime(date, "%Y-%m-%d %H:%M:%S").hour

    if 18 <= hour < 23:
        return "Добрый вечер"
    elif 6 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    else:
        return "Доброй ночи"


def get_cards_info(transactions: list[dict]) -> list[dict]:
    """Получение информации о картах"""
    cards = {}

    for transaction in transactions:
        card_number = transaction["Номер карты"]
        amount = transaction["Сумма платежа"]

        if pd.isna(card_number):
            continue

        if not pd.isna(amount) and amount < 0:
            last_digits = card_number[-4:]
            spent = abs(amount)

            if last_digits not in cards:
                cards[last_digits] = 0

            cards[last_digits] += spent

    result = []

    for last_digits, total_spent in cards.items():
        result.append(
            {
                "last_digits": last_digits,
                "total_spent": round(total_spent, 2),
                "cashback": round(total_spent / 100, 2),
            }
        )

    return result


def get_top_transactions(transactions: list[dict]) -> list[dict]:
    """Функция сортирует по сумме"""
    sorted_transactions = sorted(transactions, key=lambda transaction: transaction["Сумма платежа"], reverse=True)
    top_five = sorted_transactions[:5]
    result = []
    for transaction in top_five:
        date_object = datetime.strptime(
            transaction["Дата операции"],
            "%d.%m.%Y %H:%M:%S",
        )
        formatted_date = date_object.strftime("%d.%m.%Y")
        result.append(
            {
                "date": formatted_date,
                "amount": transaction["Сумма платежа"],
                "category": transaction["Категория"],
                "description": transaction["Описание"],
            }
        )
    return result


def main_page(date: str) -> str:
    """Формирует JSON-ответ для главной страницы приложения."""
    transactions = read_xlsx_file(str(BASE_DIR / "data" / "operations.xls"))

    filtered_transactions = filter_transactions_by_date(transactions, date)

    settings = read_user_settings(str(BASE_DIR / "user_settings.json"))

    result = {
        "greeting": get_greeting(date),
        "cards": get_cards_info(filtered_transactions),
        "top_transactions": get_top_transactions(filtered_transactions),
        "currency_rates": get_currency_rates(settings["user_currencies"]),
        "stock_prices": get_stock_prices(settings["user_stocks"]),
    }

    return json.dumps(result, ensure_ascii=False)
