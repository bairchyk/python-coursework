from unittest.mock import patch

import pytest

from src.external_api import get_currency_rates, get_stock_prices


def test_get_currency_rates() -> None:
    """Проверяет получение курса валюты из успешного ответа API."""
    with patch("src.external_api.API_KEY", "test_key"), patch("src.external_api.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {
            "success": True,
            "info": {
                "rate": 80.5,
            },
        }

        result = get_currency_rates(["USD"])

        assert result == [{"currency": "USD", "rate": 80.5}]


def test_get_stock_prices() -> None:
    """Проверяет получение цены акции из успешного ответа API."""
    with (
        patch("src.external_api.TWELVE_DATA_API_KEY", "test_key"),
        patch("src.external_api.requests.get") as mock_get,
    ):
        mock_get.return_value.json.return_value = {"price": "344.31"}

        result = get_stock_prices(["AAPL"])

        assert result == [
            {"stock": "AAPL", "price": 344.31},
        ]


def test_get_currency_rates_without_key() -> None:
    """Проверяет исключение при отсутствии ключа валютного API."""
    with patch("src.external_api.API_KEY", None):
        with pytest.raises(ValueError):
            get_currency_rates(["USD"])


def test_get_currency_rates_api_error() -> None:
    """Проверяет пустой результат, если валютный API сообщил об ошибке."""
    with (
        patch("src.external_api.API_KEY", "test_key"),
        patch("src.external_api.requests.get") as mock_get,
    ):
        mock_get.return_value.json.return_value = {
            "success": False,
            "error": "API request failed",
        }

        result = get_currency_rates(["USD"])

        assert result == []


def test_get_stock_prices_without_key() -> None:
    """Проверяет исключение при отсутствии ключа API цен акций."""
    with patch(
        "src.external_api.TWELVE_DATA_API_KEY",
        None,
    ):
        with pytest.raises(ValueError):
            get_stock_prices(["AAPL"])


def test_get_stock_prices_http_error() -> None:
    """Проверяет обработку HTTP-ошибки при запросе цены акции."""
    with (
        patch("src.external_api.TWELVE_DATA_API_KEY", "test_key"),
        patch("src.external_api.requests.get") as mock_get,
    ):
        mock_get.return_value.ok = False
        mock_get.return_value.status_code = 401

        mock_get.return_value.json.return_value = {"message": "Invalid API key"}

        result = get_stock_prices(["AAPL"])

        assert result == []


def test_get_stock_prices_zero_price() -> None:
    """Проверяет исключение нулевой цены акции из результата."""
    with patch("src.external_api.TWELVE_DATA_API_KEY", "test_key"), patch("src.external_api.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"price": "0"}

        result = get_stock_prices(["AAPL"])

        assert result == []


def test_get_currency_rates_nan() -> None:
    """Проверяет, что некорректный курс NaN не возвращается пользователю."""
    with (
        patch("src.external_api.API_KEY", "test_key"),
        patch("src.external_api.requests.get") as mock_get,
    ):
        mock_get.return_value.json.return_value = {
            "success": True,
            "info": {"rate": float("nan")},
        }

        result = get_currency_rates(["USD"])

        assert result == []


def test_get_stock_prices_nan() -> None:
    """Проверяет, что некорректная цена NaN не возвращается пользователю."""
    with (
        patch("src.external_api.TWELVE_DATA_API_KEY", "test_key"),
        patch("src.external_api.requests.get") as mock_get,
    ):
        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = {
            "price": float("nan"),
        }

        result = get_stock_prices(["AAPL"])

        assert result == []
