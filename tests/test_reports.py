from pathlib import Path

import pandas as pd
import pytest

from src.reports import save_report, spending_by_category


def test_spending_by_category(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    transactions = pd.DataFrame(
        [
            {
                "Дата операции": "20.09.2021 10:00:00",
                "Категория": "Супермаркеты",
                "Сумма платежа": -500.0,
                "Описание": "Магнит",
            },
            {
                "Дата операции": "15.12.2021 12:00:00",
                "Категория": "Супермаркеты",
                "Сумма платежа": -700.0,
                "Описание": "Пятёрочка",
            },
            {
                "Дата операции": "15.12.2021 13:00:00",
                "Категория": "Такси",
                "Сумма платежа": -300.0,
                "Описание": "Яндекс Такси",
            },
            {
                "Дата операции": "19.09.2021 10:00:00",
                "Категория": "Супермаркеты",
                "Сумма платежа": -200.0,
                "Описание": "Старый платёж",
            },
            {
                "Дата операции": "18.12.2021 10:00:00",
                "Категория": "Супермаркеты",
                "Сумма платежа": 1000.0,
                "Описание": "Возврат денег",
            },
        ]
    )

    result = spending_by_category(
        transactions,
        "Супермаркеты",
        "2021-12-20",
    )

    assert len(result) == 2
    assert result["Описание"].tolist() == [
        "Магнит",
        "Пятёрочка",
    ]
    assert result["Сумма платежа"].sum() == -1200.0
    report_path = tmp_path / "spending_by_category.xlsx"

    assert report_path.exists()

    saved_report = pd.read_excel(
        report_path,
        engine="openpyxl",
    )
    assert saved_report["Сумма платежа"].tolist() == [-500.0, -700.0]

    @save_report("custom_report.xlsx")
    def example_report() -> pd.DataFrame:
        return pd.DataFrame({"amount": [300, 400]})

    result = example_report()

    report_path = tmp_path / "custom_report.xlsx"

    assert report_path.exists()
    assert result["amount"].tolist() == [300, 400]

    saved_report = pd.read_excel(
        report_path,
        engine="openpyxl",
    )
    assert saved_report["amount"].tolist() == [300, 400]


def test_save_report_default(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)

    @save_report
    def example_report() -> pd.DataFrame:
        return pd.DataFrame({"amount": [100, 200]})

    result = example_report()

    assert (tmp_path / "report.xlsx").exists()
    assert result["amount"].tolist() == [100, 200]
