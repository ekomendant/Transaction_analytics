import os
from datetime import datetime
from json import JSONDecodeError
from unittest.mock import patch

import pandas as pd
from dotenv import load_dotenv
from freezegun import freeze_time

from src.utils import (
    API_KEY_APILAYER,
    filter_by_date,
    format_date,
    get_cards,
    get_exchange_rates,
    get_expenses,
    get_greeting,
    get_income,
    get_stock_price,
    get_top_transactions,
    import_excel_operations,
    read_json,
)

load_dotenv()
API_KEY_ALPHAVANTAGE = os.getenv("API_KEY_ALPHAVANTAGE")

""" Тестирование функции src.utils.format_date """


def test_format_date():
    date = datetime.strptime("2025-05-31 09:42:13", "%Y-%m-%d %H:%M:%S")

    # Тестирование с аргументом типа datetime
    assert format_date(date) == date

    # Тестирование с аргументом типа str
    assert format_date("2025-05-31 09:42:13") == date

    # Тестирование с аргументом иного типа (кроме datetime и str)
    with freeze_time("2025-05-31 09:42:13"):
        assert format_date(123) == date

    # Тестирование, если в аргументе передана несуществующая дата
    with freeze_time("2025-05-31 09:42:13"):
        assert format_date("2025-05-32 09:42:13") == date


""" Тестирование функции src.utils.get_greeting """


def test_get_greeting():
    # Тестирование с аргументом типа datetime
    date = datetime.strptime("2025-05-31 09:42:13", "%Y-%m-%d %H:%M:%S")
    assert get_greeting(date) == "Доброе утро"

    # Тестирование с аргументом иного типа, кроме datetime
    assert get_greeting(123) == "Добрый день"


""" Тестирование функции src.utils.import_excel_operations """


# Проверка успешного открытия и чтения файла EXCEL
@patch("pandas.read_excel")
def test_import_excel_operations_success(mock_read_excel):
    mock_df = pd.DataFrame(
        {
            "Дата операции": ["06.07.2019 00:26:13", "04.07.2019 16:50:25"],
            "Сумма платежа": ["131.20", "2.07"],
        }
    )
    mock_read_excel.return_value = mock_df
    assert import_excel_operations("test_file.xlsx").equals(mock_df)
    mock_read_excel.assert_called_once_with("test_file.xlsx")


# Проверка функции, если файл EXCEL не найден
@patch("pandas.read_excel", side_effect=FileNotFoundError)
def test_import_excel_operations_no_file(mock_read_excel):
    assert import_excel_operations("test_file.xlsx").empty is True


""" Тестирование функции src.utils.read_json """


# Проверка успешного открытия и чтения JSON-файла
@patch("builtins.open")
@patch(
    "json.load",
    return_value=[{"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]}],
)
def test_read_json_success(mock_load, mock_open):
    file = mock_open.return_value.__enter__.return_value
    assert read_json("test_file.json") == [
        {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]}
    ]

    mock_open.assert_called_once_with("test_file.json", "r", encoding="utf-8")
    mock_load.assert_called_once_with(file)


# Проверка функции, если файл пустой
@patch("builtins.open")
@patch("json.load", side_effect=JSONDecodeError("Expecting value", "", 0))
def test_read_json_no_data(mock_load, mock_open):
    file = mock_open.return_value.__enter__.return_value
    assert read_json("test_file.json") == {}

    mock_open.assert_called_once_with("test_file.json", "r", encoding="utf-8")
    mock_load.assert_called_once_with(file)


# Проверка функции, если файл не найден
@patch("builtins.open", side_effect=FileNotFoundError)
def test_read_json_no_file(mock_open):
    assert read_json("test_file.json") == {}


""" Тестирование функции src.utils.filter_by_date """


def test_filter_by_date(date_filter_main, date_filter_week, date_filter_month, date_filter_year):
    date = datetime.strptime("26.12.2021 12:26:13", "%d.%m.%Y %H:%M:%S")

    # Проверка при корректно переданных атрибутах
    assert filter_by_date(date_filter_main, date, "W").equals(date_filter_week)
    assert filter_by_date(date_filter_main, date, "M").equals(date_filter_month)
    assert filter_by_date(date_filter_main, date, "Y").equals(date_filter_year)
    assert filter_by_date(date_filter_main, date, "ALL").equals(date_filter_main)

    # Проверка при переданном пустом DataFrame
    assert filter_by_date(pd.DataFrame(), date, "M").empty is True

    # Проверка, если не передана дата
    with freeze_time("26.12.2021 12:26:13"):
        assert filter_by_date(date_filter_main, "", "W").equals(date_filter_week)


""" Тестирование функции src.utils.get_cards """


def test_get_cards(cards_original, cards_result, cards_no_filter):
    # Проверка при корректно переданных атрибутах
    assert get_cards(cards_original) == cards_result

    # Проверка при пустом DataFrame после фильтрации
    assert get_cards(cards_no_filter) == []

    # Проверка при переданном пустом DataFrame
    assert get_cards(pd.DataFrame()) == []


""" Тестирование функции src.utils.get_cards """


def test_get_top_transactions(top_transactions_original, top_transactions_result, top_transactions_no_filter):
    # Проверка при корректно переданных атрибутах
    assert get_top_transactions(top_transactions_original) == top_transactions_result

    # Проверка при пустом DataFrame после фильтрации
    assert get_top_transactions(top_transactions_no_filter) == []

    # Проверка при переданном пустом DataFrame
    assert get_top_transactions(pd.DataFrame()) == []


""" Тестирование функции src.utils.get_exchange_rates """


# Проверка успешного выполнения функции с корректным ответом API
@patch("requests.get")
def test_get_exchange_rates_success(mock_get):
    mock_get.return_value.json.return_value = {"rates": {"EUR": 10.00, "USD": 20.00}}
    headers = {"apikey": API_KEY_APILAYER}
    mock_get.return_value.status_code = 200
    assert get_exchange_rates("RUB", ["USD", "EUR"]) == [
        {"currency": "USD", "rate": 0.05},
        {"currency": "EUR", "rate": 0.10},
    ]
    mock_get.assert_called_once_with(
        "https://api.apilayer.com/exchangerates_data/latest?symbols=USD%2CEUR&base=RUB",
        headers=headers,
    )


# Проверка функции, если API вернул ошибку
@patch("requests.get")
def test_get_exchange_rates_error(mock_get):
    headers = {"apikey": API_KEY_APILAYER}
    mock_get.return_value.status_code = 500
    assert get_exchange_rates("RUB", ["USD", "EUR"]) == [
        {"currency": "USD", "rate": "Нет данных"},
        {"currency": "EUR", "rate": "Нет данных"},
    ]
    mock_get.assert_called_once_with(
        "https://api.apilayer.com/exchangerates_data/latest?symbols=USD%2CEUR&base=RUB",
        headers=headers,
    )


# Проверка выполнения функции, если на вход не передан список валют
@patch("requests.get")
def test_get_exchange_rates_no_list(mock_get):
    mock_get.return_value.json.return_value = {"rates": {"EUR": 10.00, "USD": 20.00}}
    headers = {"apikey": API_KEY_APILAYER}
    mock_get.return_value.status_code = 200
    assert get_exchange_rates("RUB", 1) == [
        {"currency": "USD", "rate": 0.05},
        {"currency": "EUR", "rate": 0.10},
    ]
    mock_get.assert_called_once_with(
        "https://api.apilayer.com/exchangerates_data/latest?symbols=USD%2CEUR&base=RUB",
        headers=headers,
    )


# Проверка выполнения функции, если ответ API не содержит данных о курсе
@patch("requests.get")
def test_get_exchange_rates_no_rates(mock_get):
    mock_get.return_value.json.return_value = {"rates": {}}
    headers = {"apikey": API_KEY_APILAYER}
    mock_get.return_value.status_code = 200
    assert get_exchange_rates("RUB", ["USD", "EUR"]) == [
        {"currency": "USD", "rate": "Нет данных"},
        {"currency": "EUR", "rate": "Нет данных"},
    ]
    mock_get.assert_called_once_with(
        "https://api.apilayer.com/exchangerates_data/latest?symbols=USD%2CEUR&base=RUB",
        headers=headers,
    )


""" Тестирование функции src.utils.get_stock_price """


# Проверка успешного выполнения функции с корректным ответом API
@patch("requests.get")
def test_get_stock_price_success(mock_get):
    mock_get.return_value.json.return_value = {"Global Quote": {"05. price": "150.12"}}
    mock_get.return_value.status_code = 200
    assert get_stock_price(["AAPL"]) == [{"stock": "AAPL", "price": 150.12}]
    mock_get.assert_called_once_with(
        f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=AAPL&apikey={API_KEY_ALPHAVANTAGE}",
    )


# Проверка функции, если API вернул ошибку
@patch("requests.get")
def test_get_stock_price_error(mock_get):
    mock_get.return_value.status_code = 500
    assert get_stock_price(["AAPL"]) == [{"stock": "AAPL", "price": "Нет данных"}]
    mock_get.assert_called_once_with(
        f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=AAPL&apikey={API_KEY_ALPHAVANTAGE}",
    )


# Проверка выполнения функции, если на вход не передан список акций
def test_get_stock_price_no_list():
    assert get_stock_price(1) == [{"stock": "Нет данных", "price": "Нет данных"}]
    assert get_stock_price([]) == [{"stock": "Нет данных", "price": "Нет данных"}]


# Проверка выполнения функции, если ответ API не содержит данных о стоимости акций
@patch("requests.get")
def test_get_stock_price_no_rates(mock_get):
    mock_get.return_value.json.return_value = {"Global Quote": {}}
    mock_get.return_value.status_code = 200
    assert get_stock_price(["AAPL"]) == [{"stock": "AAPL", "price": "Нет данных"}]
    mock_get.assert_called_once_with(
        f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=AAPL&apikey={API_KEY_ALPHAVANTAGE}",
    )


""" Тестирование функции src.utils.get_expenses """


def test_get_expenses(
    expenses_original, expenses_result, expenses_no_filter, expenses_less_seven_origin, expenses_result_less_seven
):
    # Проверка при корректно переданных атрибутах, категорий более 7
    assert get_expenses(expenses_original) == expenses_result

    # Проверка при корректно переданных атрибутах, категорий менее 7
    assert get_expenses(expenses_less_seven_origin) == expenses_result_less_seven

    # Проверка при пустом DataFrame после фильтрации
    assert get_expenses(expenses_no_filter) == {}

    # Проверка при переданном пустом DataFrame
    assert get_expenses(pd.DataFrame()) == {}


""" Тестирование функции src.utils.get_income """


def test_get_income(income_origin, income_result, income_no_filter):
    # Проверка при корректно переданных атрибутах
    assert get_income(income_origin) == income_result

    # Проверка при пустом DataFrame после фильтрации
    assert get_income(income_no_filter) == {}

    # Проверка при переданном пустом DataFrame
    assert get_income(pd.DataFrame()) == {}
