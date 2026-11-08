import logging
import math
import os

import requests
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


load_dotenv()

API_KEY = os.getenv("EXCHANGE_RATES_API_KEY")
TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")

API_URL = "https://api.apilayer.com/exchangerates_data/convert"
STOCK_API_URL = "https://api.twelvedata.com/price"


def get_currency_rates(currencies: list[str]) -> list[dict]:
    """Запрос через API на актуальный курс валют"""
    result = []

    if not API_KEY:
        raise ValueError("Exchange rates API key is required")

    for currency in currencies:

        try:

            headers = {"apikey": API_KEY or ""}

            params: dict[str, str | int] = {
                "from": currency,
                "to": "RUB",
                "amount": 1,
            }

            response = requests.get(
                API_URL,
                headers=headers,
                params=params,
                timeout=10,
            )
            response.raise_for_status()

            data = response.json()

            if not data.get("success", False):
                logger.warning(
                    "API не выполнил запрос для %s: %s",
                    currency,
                    data.get("error", "Неизвестная ошибка"),
                )
                continue

            rate = float(data["info"]["rate"])

            if not math.isfinite(rate) or rate <= 0:
                continue

            result.append(
                {
                    "currency": currency,
                    "rate": rate,
                }
            )

        except (requests.RequestException, KeyError, TypeError, ValueError) as error:
            logger.error(
                "Error while getting currency rates %s : %s",
                currency,
                type(error).__name__,
            )
            continue

    return result


def get_stock_prices(stocks: list[str]) -> list[dict]:
    """Возвращает стоимости акций"""
    result = []

    if not TWELVE_DATA_API_KEY:
        raise ValueError("Twelve Data API key is required")

    for stock in stocks:

        try:
            response = requests.get(
                STOCK_API_URL,
                params={
                    "symbol": stock,
                    "apikey": TWELVE_DATA_API_KEY,
                },
                timeout=10,
            )

            if not response.ok:
                try:
                    error_data = response.json()
                except ValueError:
                    error_data = {}

                logger.error(
                    "Twelve Data: HTTP %s, акция %s, причина: %s",
                    response.status_code,
                    stock,
                    error_data.get("message", "Описание отсутствует"),
                )
                continue

            response.raise_for_status()
            data = response.json()

            if data.get("status") == "error":
                logger.warning(
                    "Twelve Data error for %s: %s",
                    stock,
                    data.get("message", "Unknown error"),
                )
                continue

            price = float(data["price"])

            if not math.isfinite(price) or price <= 0:
                continue

            result.append(
                {
                    "stock": stock,
                    "price": round(price, 2),
                }
            )

        except (requests.RequestException, KeyError, TypeError, ValueError) as error:
            logger.error(
                "Error while getting stock rates %s : %s",
                stock,
                type(error).__name__,
            )

    return result
