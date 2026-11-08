# Курсовая работа — анализ банковских транзакций

Приложение на Python для анализа банковских операций из Excel-файла. Проект формирует JSON-данные для страницы «Главная», предоставляет поиск по транзакциям и создаёт Excel-отчёт по расходам.

В рамках курсовой работы выполнено по одному заданию из каждой обязательной категории: **«Главная»**, **«Простой поиск»** и **«Траты по категории»**.

## Возможности

### 1. Веб-страницы — «Главная»

Функция `main_page(date)` из `src/views.py` принимает дату и время в формате `YYYY-MM-DD HH:MM:SS` и возвращает JSON со следующими полями:

- `greeting` — приветствие по времени суток;
- `cards` — последние четыре цифры карты, сумма расходов и расчётный кешбэк (1%);
- `top_transactions` — пять транзакций с наибольшим значением суммы платежа, отсортированных по убыванию;
- `currency_rates` — курсы валют к рублю;
- `stock_prices` — цены акций.

Для страницы рассматриваются операции с начала месяца до указанной даты и времени. Валюты и акции выбираются в `user_settings.json`.

### 2. Сервисы — «Простой поиск»

Функция `search_transactions(transactions, search_string)` из `src/services.py` ищет подстроку в полях **«Описание»** и **«Категория»** без учёта регистра. Возвращает JSON со всеми подходящими транзакциями. Отсутствующие числовые значения (`NaN`) преобразуются в `null`, чтобы JSON оставался корректным.

### 3. Отчёты — «Траты по категории»

Функция `spending_by_category(transactions, category, date=None)` из `src/reports.py` принимает `pandas.DataFrame`, название категории и необязательную дату. Возвращает строки с расходами выбранной категории за последние три месяца относительно указанной даты. Если дата не задана, используется текущая.

Декоратор `save_report` автоматически сохраняет результат функции в Excel (`.xlsx`). Он поддерживает как использование без параметров (`@save_report`), так и с именем файла (`@save_report("example.xlsx")`). Отчёт по категории сохраняется в `spending_by_category.xlsx` в текущем рабочем каталоге.

## Технологии

- Python 3.13
- Poetry — управление зависимостями
- Pandas, python-calamine, openpyxl — чтение и создание Excel-файлов
- Requests — запросы к внешним API
- python-dotenv — переменные окружения
- Pytest, pytest-cov — тестирование и оценка покрытия
- Black, isort, flake8, mypy — форматирование и статический анализ

## Установка

Требуются **Python 3.13** и **Poetry**.

1. Клонируйте репозиторий и перейдите в папку проекта:

   ```powershell
   git clone https://github.com/bairchyk/python-coursework.git
   cd python-coursework
   git switch develop
   ```

   В этом репозитории рабочая версия курсовой ведётся в ветке `develop`; перед сдачей в неё необходимо объединить все завершённые изменения, включая отчёты.

2. Установите зависимости:

   ```powershell
   poetry install
   ```

3. Создайте в корне проекта файл `.env` с ключами для внешних сервисов:

   ```dotenv
   EXCHANGE_RATES_API_KEY=your_exchange_rates_api_key
   TWELVE_DATA_API_KEY=your_twelve_data_api_key
   ```

   Используются API [APILayer Exchange Rates Data](https://apilayer.com/marketplace/exchangerates_data-api) и [Twelve Data](https://twelvedata.com/). Ключи нужно получить самостоятельно. **Не добавляйте `.env` с настоящими ключами в Git.**

4. Создайте папку `data` (если её нет) и поместите туда учебный Excel-файл с операциями под именем **`operations.xls`**:

   ```text
   python-coursework/
   └── data/
       └── operations.xls
   ```

   Файл операций берётся из материалов курсового задания. Папка `data/` исключена из Git, чтобы не публиковать финансовые данные.

## Настройки

В `user_settings.json` перечислены валюты и акции для страницы «Главная»:

```json
{
  "user_currencies": ["USD", "EUR"],
  "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
}
```

## Запуск приложения

Из корня проекта выполните:

```powershell
poetry run python -m src.main
```

`main.py` демонстрирует три задания: формирует JSON главной страницы, выполняет поиск по транзакциям и создаёт Excel-отчёт. В демонстрационном запуске используется дата из учебного набора операций.

Отдельный вызов главной страницы:

```powershell
poetry run python -c "from src.views import main_page; print(main_page('2021-12-20 15:30:00'))"
```

Пример поиска:

```python
from src.services import search_transactions

transactions = [
    {"Категория": "Кино", "Описание": "Билеты в кино"},
    {"Категория": "Супермаркеты", "Описание": "Покупка продуктов"},
]
print(search_transactions(transactions, "кино"))
```

Пример создания отчёта:

```python
import pandas as pd
from src.reports import spending_by_category

transactions = pd.read_excel("data/operations.xls", engine="calamine")
report = spending_by_category(transactions, "Супермаркеты", "2021-12-20")
print(report.head())
```

**Примечание об API:** курсы валют и цены акций загружаются из внешних сервисов во время выполнения. При сетевых ошибках, ограничениях API или недоступности сервиса соответствующие значения могут отсутствовать в JSON; ошибки записываются в журнал. Программа не подставляет вымышленные котировки.

## Тестирование и проверка качества

Выполните из корня проекта:

```powershell
poetry run pytest -v
poetry run pytest --cov=src --cov-report=term-missing
poetry run black --check src tests
poetry run isort --check-only src tests
poetry run flake8 src tests
poetry run mypy src tests
```

В тестах внешние API подменяются с помощью `unittest.mock.patch`, поэтому для их запуска реальные ключи и доступ к сети не требуются.

## Структура проекта

```text
python-coursework/
├── src/
│   ├── main.py          # Точка входа и демонстрация возможностей
│   ├── views.py         # JSON главной страницы
│   ├── services.py      # Поиск транзакций
│   ├── reports.py       # Excel-отчёт и декоратор
│   ├── external_api.py  # Курсы валют и цены акций
│   └── utils.py         # Загрузка данных и настройки, фильтрация дат
├── tests/               # Автоматические тесты
├── data/                # Локальный Excel-файл (не хранится в Git)
├── user_settings.json   # Выбранные валюты и акции
├── pyproject.toml       # Зависимости и настройки инструментов
├── poetry.lock          # Зафиксированные версии зависимостей
├── .gitignore
└── README.md
```
