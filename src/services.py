"""Сервисы для поиска и анализа банковских транзакций."""

import json
import logging
import math
from collections import Counter
from typing import Any

logger = logging.getLogger(__name__)


def _json_safe(value: Any) -> Any:
    """Заменить Nan на нули в JSON"""
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


def search_transactions(
    transactions: list[dict],
    search_string: str,
) -> str:
    """Возвращает JSON транзакций по описанию или категории"""
    query = search_string.casefold()

    def matches(transaction: dict) -> bool:
        description = transaction.get("Описание")
        category = transaction.get("Категория")

        return any(query in value.casefold() for value in (description, category) if isinstance(value, str))

    filtered_transactions = list(filter(matches, transactions))

    return json.dumps(
        _json_safe(filtered_transactions),
        ensure_ascii=False,
        allow_nan=False,
    )


def count_transactions_by_category(
    transactions: list[dict],
    categories: list[str],
) -> dict[str, int]:
    """Подсчитывает число транзакций из указанных категорий"""
    descriptions = [transaction.get("Категория", "") for transaction in transactions]
    counts = Counter(descriptions)
    result = {}
    for category in categories:
        result[category] = counts[category]
    return result
