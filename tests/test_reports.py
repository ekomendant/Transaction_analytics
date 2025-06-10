from datetime import datetime
from unittest.mock import patch

import pandas as pd
from freezegun import freeze_time

from src.reports import spending_by_category, spending_by_weekday, spending_by_workday, write_report

""" Тестирование декоратора src.reports.write_report """


@patch("builtins.open")
@patch(
    "json.dump",
    return_value=[
        {"Сумма платежа": 131.2, "Валюта платежа": "RUB"},
        {"Сумма платежа": -2.07, "Валюта платежа": "RUB"},
    ],
)
def test_write_report(mock_dump, mock_open):
    file = mock_open.return_value.__enter__.return_value

    @write_report("test_file.json")
    def my_test_function():
        df = pd.DataFrame({"Сумма платежа": [131.20, -2.07], "Валюта платежа": ["RUB", "RUB"]})
        return df

    # Проверка работы декоратора с записью отчета в файл
    assert my_test_function() == [
        {"Сумма платежа": 131.2, "Валюта платежа": "RUB"},
        {"Сумма платежа": -2.07, "Валюта платежа": "RUB"},
    ]

    mock_open.assert_called_once_with("test_file.json", "w", encoding="utf-8")
    mock_dump.assert_called_once_with(
        [{"Сумма платежа": 131.2, "Валюта платежа": "RUB"}, {"Сумма платежа": -2.07, "Валюта платежа": "RUB"}],
        file,
        indent=4,
        ensure_ascii=False,
    )


""" Тестирование функции src.reports.spending_by_category """


@patch("src.utils.format_date")
def test_spending_by_category_mock(mock_format_date, reports_by_category_df, reports_by_category):
    date_object = datetime.strptime("19.12.2021 20:02:48", "%d.%m.%Y %H:%M:%S")
    mock_format_date.return_value = date_object
    assert spending_by_category(reports_by_category_df, "Связь", "19.12.2021 20:02:48") == reports_by_category


def test_spending_by_category(reports_by_category_df, reports_by_category):
    # Тестирование с аргументом иного типа (кроме datetime и str)
    with freeze_time("19.12.2021 20:02:48"):
        assert spending_by_category(reports_by_category_df, "Связь") == reports_by_category

    # Проверка при переданном пустом DataFrame
    with freeze_time("19.12.2021 20:02:48"):
        assert spending_by_category(pd.DataFrame(), "Связь") == []


""" Тестирование функции src.reports.spending_by_weekday """


@patch("src.utils.format_date")
def test_spending_by_weekday_mock(mock_format_date, reports_by_weekday_df, reports_by_weekday):
    date_object = datetime.strptime("25.12.2021 20:02:48", "%d.%m.%Y %H:%M:%S")
    mock_format_date.return_value = date_object
    assert spending_by_weekday(reports_by_weekday_df, "25.12.2021 20:02:48") == reports_by_weekday


def test_spending_by_weekday(reports_by_weekday_df, reports_by_weekday, reports_no_filter_df):
    # Тестирование с аргументом иного типа (кроме datetime и str)
    with freeze_time("25.12.2021 20:02:48"):
        assert spending_by_weekday(reports_by_weekday_df) == reports_by_weekday

    # Проверка при переданном пустом DataFrame
    with freeze_time("25.12.2021 20:02:48"):
        assert spending_by_weekday(pd.DataFrame()) == []

    # Проверка, если фильтрация не дала результата
    with freeze_time("25.12.2021 20:02:48"):
        assert spending_by_weekday(reports_no_filter_df) == []


""" Тестирование функции src.reports.spending_by_workday """


@patch("src.utils.format_date")
def test_spending_by_workday_mock(mock_format_date, reports_by_weekday_df, reports_by_workday):
    date_object = datetime.strptime("25.12.2021 20:02:48", "%d.%m.%Y %H:%M:%S")
    mock_format_date.return_value = date_object
    assert spending_by_workday(reports_by_weekday_df, "25.12.2021 20:02:48") == reports_by_workday


def test_spending_by_workday(reports_by_weekday_df, reports_by_workday, reports_no_filter_df):
    # Тестирование с аргументом иного типа (кроме datetime и str)
    with freeze_time("25.12.2021 20:02:48"):
        assert spending_by_workday(reports_by_weekday_df) == reports_by_workday

    # Проверка при переданном пустом DataFrame
    with freeze_time("25.12.2021 20:02:48"):
        assert spending_by_workday(pd.DataFrame()) == []

    # Проверка, если фильтрация не дала результата
    with freeze_time("25.12.2021 20:02:48"):
        assert spending_by_workday(reports_no_filter_df) == []
