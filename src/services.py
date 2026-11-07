import json
import re
from collections import Counter

transactions = [
    {"Описание": "Покупка в Пятёрочке"},
    {"Описание": "Перевод Ивану"},
    {"Описание": "ПЯТЁРОЧКА"},
]

transactions_1 = [
    {
        "Описание": "Покупка в Пятёрочке",
        "Категория": "Супермаркеты",
    },
    {
        "Описание": "Поездка на такси",
        "Категория": "Транспорт",
    },
]

categories = ["Супермаркеты", "такси", "Пятерочке"]


def search_transactions(
    transactions: list[dict],
    search_string: str,
) -> str:
    result = []

    for transaction in transactions:
        description = transaction.get("Описание", "")
        category = transaction.get("Категория", "")

        match_description = re.search(
            re.escape(search_string),
            description,
            flags=re.IGNORECASE,
        )

        match_category = re.search(
            re.escape(search_string),
            category,
            flags=re.IGNORECASE,
        )

        if match_description or match_category:
            result.append(transaction)

    return json.dumps(result, ensure_ascii=False)


def count_transactions_by_category(
    transactions: list[dict],
    categories: list[str],
) -> dict[str, int]:

    descriptions = [transaction.get("Категория", "") for transaction in transactions]
    counts = Counter(descriptions)
    result = {}
    for category in categories:
        result[category] = counts[category]
    return result
