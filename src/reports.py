from collections.abc import Callable
from functools import wraps
from typing import Any

import pandas as pd


def save_report(
    func_or_filename: Callable[..., pd.DataFrame] | str = "report.xlsx",
) -> Any:
    """Сохраняет результат функции-отчёта в Excel."""

    def decorator(func: Callable[..., pd.DataFrame]) -> Callable[..., pd.DataFrame]:

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> pd.DataFrame:
            result = func(*args, **kwargs)
            result.to_excel(filename, index=False)
            return result

        return wrapper

    if callable(func_or_filename):
        filename = "report.xlsx"
        return decorator(func_or_filename)

    filename = func_or_filename
    return decorator


@save_report("spending_by_category.xlsx")
def spending_by_category(
    transactions: pd.DataFrame,
    category: str,
    date: str | None = None,
) -> pd.DataFrame:
    """Возвращает расходы по категории за последние три месяца."""

    end_date = pd.to_datetime(date).normalize() if date is not None else pd.Timestamp.now().normalize()

    start_date = end_date - pd.DateOffset(months=3)

    transaction_dates = pd.to_datetime(
        transactions["Дата операции"],
        format="%d.%m.%Y %H:%M:%S",
        errors="coerce",
    )

    amounts = pd.to_numeric(
        transactions["Сумма платежа"],
        errors="coerce",
    )

    filtered = transactions.loc[
        (transaction_dates >= start_date)
        & (transaction_dates < end_date + pd.Timedelta(days=1))
        & (transactions["Категория"] == category)
        & (amounts < 0)
    ]

    return filtered.copy()
