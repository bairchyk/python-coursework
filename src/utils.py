import json
from datetime import datetime

import pandas as pd


def read_xlsx_file(path: str) -> list[dict]:
    """Считывает финансовые операции из Excel-файла и возвращает список словарей."""
    df = pd.read_excel(path, engine="calamine")  # открывает excel-файл через заданный путь
    return df.to_dict(orient="records")  # преобразует excel-файл в словарь и возвращает в функцию


def filter_transactions_by_date(
    transactions: list[dict],
    date: str,
) -> list[dict]:
    """Фильтрует транзакции с начала месяца до указанной даты."""
    end_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    filtered_transactions = []

    for transaction in transactions:
        transaction_date = datetime.strptime(
            transaction["Дата операции"],
            "%d.%m.%Y %H:%M:%S",
        )
        if start_date <= transaction_date <= end_date:
            filtered_transactions.append(transaction)

    return filtered_transactions


def read_user_settings(path: str) -> dict:
    """Читает пользовательские настройки из JSON-файла."""

    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, dict):
            return data

        return {}

    except (FileNotFoundError, json.JSONDecodeError):
        return {}
