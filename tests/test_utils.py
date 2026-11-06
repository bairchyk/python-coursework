import json
from pathlib import Path

import pandas as pd

from src.utils import filter_transactions_by_date, read_user_settings, read_xlsx_file


def test_read_xlsx_file(tmp_path: Path) -> None:
    "Проверка чтения Excel-файла."
    # Создаём путь к файлу
    file_path = tmp_path / "test.xlsx"

    data = [
        {"name": "Alice", "amount": 100},
        {"name": "Bob", "amount": 200},
    ]

    # Создаём DataFrame и сохраняем в Excel
    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False)

    # Читаем обратно и проверяем
    result = read_xlsx_file(str(file_path))

    assert result == [
        {"name": "Alice", "amount": 100},
        {"name": "Bob", "amount": 200},
    ]


def test_filter_transactions_by_date() -> None:
    transactions = [
        {"Дата операции": "01.11.2026 15:30:00", "Сумма платежа": 100},
        {"Дата операции": "10.11.2026 15:30:00", "Сумма платежа": 200},
        {"Дата операции": "25.11.2026 15:30:00", "Сумма платежа": 300},
        {"Дата операции": "31.10.2026 15:30:00", "Сумма платежа": 400},
    ]
    date = "2026-11-21 15:30:00"

    result = filter_transactions_by_date(transactions, date)
    assert result == [
        {"Дата операции": "01.11.2026 15:30:00", "Сумма платежа": 100},
        {"Дата операции": "10.11.2026 15:30:00", "Сумма платежа": 200},
    ]


def test_read_user_settings(tmp_path: Path) -> None:
    file_path = tmp_path / "test_user.json"

    settings = {
        "user_currencies": ["USD", "EUR"],
        "user_stocks": ["AAPL", "TSLA"],
    }

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(settings, file)

    result = read_user_settings(str(file_path))

    assert result == settings
