"""Точка входа в приложение для анализа банковских транзакций."""

from pathlib import Path

import pandas as pd

from src.reports import spending_by_category
from src.services import count_transactions_by_category, search_transactions
from src.utils import read_xlsx_file
from src.views import main_page

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "operations.xls"


def main() -> None:
    """Запускает основные функции приложения."""

    date = "2021-12-20 15:30:00"

    # 1. Загрузка транзакций
    transactions = read_xlsx_file(str(DATA_PATH))

    # 2. Главная страница
    print("=== ГЛАВНАЯ СТРАНИЦА ===")
    print(main_page(date))

    # 3. Простой поиск
    print("\n=== ПОИСК ТРАНЗАКЦИЙ ===")
    search_result = search_transactions(transactions, "кино")
    categories_result = count_transactions_by_category(
        transactions,
        [
            "Супермаркеты",
            "Транспорт",
            "Такси",
            "Аптеки",
            "Связь",
            "Кино",
            "Рестораны",
        ],
    )
    print(search_result)
    print(categories_result)

    # 4. Отчёт по категории
    print("\n=== ОТЧЁТ ПО КАТЕГОРИИ ===")
    df = pd.DataFrame(transactions)

    report = spending_by_category(
        transactions=df,
        category="Такси",
        date="2021-12-20",
    )

    print(report)
    print("\nОтчёт сохранён в spending_by_category.xlsx")


if __name__ == "__main__":
    main()
