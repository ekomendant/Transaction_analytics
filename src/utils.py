import json
import logging
import os
from datetime import datetime, timedelta
from json import JSONDecodeError
from typing import Any

import pandas as pd
import requests
from dotenv import load_dotenv
from pandas import DataFrame

from config import PATH_LOGS

load_dotenv()
API_KEY_APILAYER = os.getenv("API_KEY_APILAYER")
API_KEY_ALPHAVANTAGE = os.getenv("API_KEY_ALPHAVANTAGE")

logger = logging.getLogger("utils")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(PATH_LOGS / "utils.log", "w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def format_date(input_date: str | datetime) -> datetime:
    """
    Функция переводит дату из типа str в datetime
    :param input_date: дата в виде строки
    :return: дата в виде datetime
    """

    logger.info("Функция utils.format_date запущена.")
    try:
        if isinstance(input_date, datetime):
            modified_date = input_date
            logger.info("Работа функции завершена. Использована исходная дата.")
        elif isinstance(input_date, str):
            modified_date = datetime.strptime(input_date, "%Y-%m-%d %H:%M:%S")
            logger.info("Работа функции завершена. Дата преобразована из строки.")
        else:
            modified_date = datetime.now()
            logger.error("Работа функции завершена. Не удалось преобразовать дату, использована текущая дата.")
        return modified_date
    except Exception:
        logger.error("Работа функции завершена. Не удалось преобразовать дату, использована текущая дата.")
        return datetime.now()


def get_greeting(time: datetime) -> str | None:
    """
    Функция определяет время суток по дате/времени и возвращает приветствие
    :param time: дата и время
    :return: приветствие (добрый день/вечер/ночь/утро)
    """

    logger.info("Функция utils.get_greeting запущена.")
    if isinstance(time, datetime):
        hour = time.hour
        greeting = (
            "Доброе утро"
            if 5 <= hour < 12
            else "Добрый день" if 12 <= hour < 18 else "Добрый вечер" if 18 <= hour < 23 else "Доброй ночи"
        )
        logger.info("Работа функции завершена. Время суток успешно определено.")
        return greeting
    else:
        logger.error("Работа функции завершена. Не удалось преобразовать дату, использовано время суток по умолчанию.")
        return "Добрый день"


def import_excel_operations(file: str) -> DataFrame:
    """
    Функция принимает на вход путь до файла EXCEL и возвращает DataFrame с данными о финансовых операциях
    :param file: путь до файла EXCEL
    :return: DataFrame с операциями, либо пустой DataFrame (если файла не существует или не содержит данные)
    """

    logger.info("Функция utils.import_excel_operations запущена.")
    try:
        logger.info(f"Открытие файла {file}.")
        operations = pd.read_excel(file)

        logger.info("Преобразование формата даты и суммы платежа")
        operations["Дата операции"] = pd.to_datetime(operations["Дата операции"], dayfirst=True)
        operations["Сумма платежа"] = operations["Сумма платежа"].astype(float)

        logger.info("Данные успешно извлечены из EXCEL и преобразованы.")
        return operations
    except FileNotFoundError:
        logger.error("Файл не существует, получить данные не удалось.")
        empty_df = pd.DataFrame()
        return empty_df


def read_json(file_json: str) -> Any:
    """
    Функция принимает на вход путь до JSON-файла и возвращает список словарей с данными.
    :param file_json: Путь до JSON-файла.
    :return: Список словарей с данными файла.
    """

    logger.info("Функция utils.convert_json_transactions запущена.")
    try:
        logger.info(f"Открытие файла {file_json}.")
        with open(file_json, "r", encoding="utf-8") as json_file:
            logger.info("Преобразование JSON-данных.")
            try:
                info = json.load(json_file)
                logger.info("Данные успешно преобразованы.")
                return info
            except JSONDecodeError:
                logger.error("Файл не содержал JSON-данных, невозможно преобразовать.")
                return {}
    except FileNotFoundError:
        logger.error("Файл не существует, получить данные не удалось.")
        return {}


def filter_by_date(operations: DataFrame, input_date: datetime, period: str = "M") -> DataFrame:
    """
    Функция фильтрует перечень операций по дате операции согласно переданным атрибутам
    :param operations: DataFrame с операциями
    :param input_date: максимальная дата для фильтрации
    :param period: условное обозначение начала периода для фильтрации (неделя/месяц/год, на который приходится дата)
    :return: отфильтрованный по дате перечень операций
    """

    logger.info("Функция utils.filter_by_date запущена.")
    if operations.empty:
        logger.error("Работа функции завершена. На вход подан пустой DataFrame.")
        return operations
    else:
        logger.info("Определение периода фильтрации.")
        if isinstance(input_date, datetime):
            finish_date = input_date
        else:
            finish_date = datetime.now()

        if period == "W":
            monday = finish_date - timedelta(days=finish_date.weekday())
            start_date = monday.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "M":
            start_date = finish_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == "Y":
            start_date = finish_date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = operations["Дата операции"].min()

        filtered_operations = operations[
            (operations["Дата операции"] >= start_date) & (operations["Дата операции"] <= finish_date)
        ]

        logger.info("Работа функции завершена. Фильтрация по заданному периоду успешно проведена.")
        return filtered_operations


def get_cards(operations_df: DataFrame) -> list:
    """
    Функция обрабатывает перечень операций и выводит по каждой карте сумму расходов в рублях и сумму кэшбэка
    :param operations_df: DataFrame с операциями для анализа
    :return: список словарей с номерами карт, суммой расходов и кэшбэка
    """

    logger.info("Функция utils.get_cards запущена.")
    if len(operations_df) > 0:
        logger.info("Фильтрация данных.")
        cards_expenses = operations_df[
            (operations_df["Валюта платежа"] == "RUB")
            & (operations_df["Статус"] == "OK")
            & (operations_df["Сумма платежа"] < 0)
            & (operations_df["Номер карты"].notnull())
        ]

        if len(cards_expenses) > 0:
            logger.info("Преобразование данных и расчет суммы расходов.")
            cards_expenses = (
                cards_expenses[["Номер карты", "Сумма платежа"]].groupby("Номер карты").sum().reset_index()
            )
            cards_expenses["Номер карты"] = cards_expenses["Номер карты"].map(lambda x: x[1:])
            cards_expenses["Сумма платежа"] = abs(round(cards_expenses["Сумма платежа"], 2))
            cards_expenses["Кэшбэк"] = round(cards_expenses["Сумма платежа"] / 100, 2)
            new_names = {"Номер карты": "last_digits", "Сумма платежа": "total_spent", "Кэшбэк": "cashback"}
            cards_expenses = cards_expenses.rename(columns=new_names)

            logger.info("Работа функции завершена. Данные по картам успешно получены.")
            return cards_expenses.to_dict(orient="records")
        else:
            logger.error("Работа функции завершена. Фильтрация не дала результатов.")
            return []
    else:
        logger.error("Работа функции завершена. На вход подан пустой DataFrame.")
        return []


def get_top_transactions(operations_df: DataFrame) -> list:
    """
    Функция возвращает топ-5 операций по сумме платежа
    :param operations_df: DataFrame с операциями
    :return: топ-5 операций по сумме платежа
    """

    logger.info("Функция utils.get_top_transactions запущена.")
    if len(operations_df) > 0:
        logger.info("Фильтрация данных.")
        filtered_operations = operations_df[
            (operations_df["Валюта платежа"] == "RUB") & (operations_df["Статус"] == "OK")
        ]

        if len(filtered_operations) > 0:
            logger.info("Определение ТОП-5 транзакций.")
            sorted_operations = filtered_operations.sort_values(
                by="Сумма платежа", key=lambda x: abs(x), ascending=False
            )[:5]
            top_operations = sorted_operations.to_dict(orient="records")
            top_list = []

            for operation in top_operations:
                new_dict = {
                    "date": operation["Дата операции"].strftime("%d.%m.%Y"),
                    "amount": round(operation["Сумма платежа"], 2),
                    "category": operation["Категория"],
                    "description": operation["Описание"],
                }
                top_list.append(new_dict)

            logger.info("Работа функции завершена. Данные по ТОП-5 транзакций успешно получены.")
            return top_list
        else:
            logger.error("Работа функции завершена. Фильтрация не дала результатов.")
            return []
    else:
        logger.error("Работа функции завершена. На вход подан пустой DataFrame.")
        return []


def get_exchange_rates(base_currency: str, user_currencies: list) -> Any:
    """
    Функция делает запрос к API https://api.apilayer.com/exchangerates_data/ для определения курса запрашиваемых валют.
    :param base_currency: Базовая валюта, к которой необходимо получить курс.
    :param user_currencies: Список валют, курсы которых необходимо привести к базовой валюте.
    :return: Список словарей с курсами валют.
    """

    logger.info("Функция utils.get_exchange_rates запущена.")
    logger.info("Определение списка валют.")
    if isinstance(user_currencies, list):
        symbols = "%2C".join(user_currencies)
    else:
        user_currencies = ["USD", "EUR"]
        symbols = "%2C".join(user_currencies)

    logger.info("Запрос к API.")
    url = f"https://api.apilayer.com/exchangerates_data/latest?symbols={symbols}&base={base_currency}"
    headers = {"apikey": API_KEY_APILAYER}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        logger.info("Ответ API успешно получен, обработка результата.")
        data = response.json()

        rates = []

        for currency in user_currencies:
            price = data.get("rates", {}).get(currency)
            if price is not None:
                rate = {"currency": currency, "rate": round(1 / price, 2)}
            else:
                rate = {"currency": currency, "rate": "Нет данных"}
            rates.append(rate)

        logger.info("Работа функции завершена. Данные по курсам валют успешно получены.")
        return rates
    else:
        logger.error("Работа функции завершена. Запрос к API не дал результата.")
        return [{"currency": "USD", "rate": "Нет данных"}, {"currency": "EUR", "rate": "Нет данных"}]


def get_stock_price(user_stocks: list) -> list:
    """
    Функция делает запрос к API https://www.alphavantage.co/ для получения актуальной стоимости по списку акций
    :param user_stocks: список акций
    :return: список словарей со стоимостью акций
    """

    logger.info("Функция utils.get_stock_price запущена.")
    if isinstance(user_stocks, list) and len(user_stocks) > 0:
        final_stocks = []
        logger.info("Запрос к API.")
        for stock in user_stocks:
            logger.info(f"Запрос к API по акции {stock}.")
            url = (
                f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={API_KEY_ALPHAVANTAGE}"
            )
            response = requests.get(url)
            if response.status_code == 200:
                logger.info(f"Ответ API по акции {stock} успешно получен, обработка результата.")
                data = response.json()
                price = data.get("Global Quote", {}).get("05. price")
                if price is not None:
                    stock_price = {"stock": stock, "price": float(price)}
                else:
                    stock_price = {"stock": stock, "price": "Нет данных"}
            else:
                logger.error(f"Запрос к API по акции {stock} не дал результата.")
                stock_price = {"stock": stock, "price": "Нет данных"}
            final_stocks.append(stock_price)

        logger.info("Работа функции завершена. Вывод результата.")
        return final_stocks
    else:
        logger.error("Работа функции завершена. Список акций не содержит данных.")
        return [{"stock": "Нет данных", "price": "Нет данных"}]


def get_expenses(operations_df: DataFrame) -> dict:
    """
    Функция определяет общую сумму расходов и распределяет расходы по категориям
    :param operations_df: DataFrame с операциями
    :return: сумма расходов и детализация расходов по категориям в виде словаря
    """

    logger.info("Функция utils.get_expenses запущена.")
    if len(operations_df) > 0:
        logger.info("Фильтрация списка операций.")
        filtered_operations = operations_df[
            (operations_df["Валюта платежа"] == "RUB")
            & (operations_df["Статус"] == "OK")
            & (operations_df["Сумма платежа"] < 0)
        ]

        if len(filtered_operations) > 0:
            logger.info("Определение общей суммы расходов.")
            total_amount = round(abs(float(filtered_operations["Сумма платежа"].sum())), 2)

            logger.info("Группировка данных по категориям.")
            categories = filtered_operations[["Категория", "Сумма платежа"]].groupby("Категория").sum().reset_index()
            categories["Сумма платежа"] = abs(round(categories["Сумма платежа"], 2))
            sorted_operations = categories.sort_values(by="Сумма платежа", key=lambda x: x, ascending=False)
            new_names = {"Категория": "category", "Сумма платежа": "amount"}
            categories_list = sorted_operations.rename(columns=new_names)

            # Формируем список расходов по категориям
            categories_for_main = categories_list[
                (categories_list["category"] != "Переводы") & (categories_list["category"] != "Наличные")
            ]

            if len(categories_for_main) > 7:
                expenses_by_category = categories_for_main[:7].reset_index(drop=True)
                others = categories_for_main[7:]
                others_amount = round(abs(float(others["amount"].sum())), 2)
                expenses_by_category.loc[7] = ["Остальное", others_amount]

            else:
                expenses_by_category = categories_for_main

            logger.info("Расходы по категориям получены.")
            main = expenses_by_category.to_dict(orient="records")

            # Формируем список переводов и наличных
            categories_for_transfers = categories_list[
                (categories_list["category"] == "Переводы") | (categories_list["category"] == "Наличные")
            ]
            logger.info("Данные по переводам и налисным получен.")
            transfers_and_cash = categories_for_transfers.to_dict(orient="records")

            # Формируем результат обработки
            expenses = {
                "total_amount": total_amount,
                "main": main,
                "transfers_and_cash": transfers_and_cash,
            }
            logger.info("Работа функции завершена. Данные успешно получены.")
            return expenses
        else:
            logger.error("Работа функции завершена. Фильтрация не дала результата.")
            return {}
    else:
        logger.error("Работа функции завершена. Перечень операций не содержит данных.")
        return {}


def get_income(operations_df: DataFrame) -> dict:
    """
    Функция определяет общую сумму доходов и распределяет доходы по категориям
    :param operations_df: DataFrame с операциями
    :return: сумма доходов и детализация доходов по категориям в виде словаря
    """

    logger.info("Функция utils.get_income запущена.")
    if len(operations_df) > 0:
        logger.info("Фильтрация списка операций.")
        filtered_operations = operations_df[
            (operations_df["Валюта платежа"] == "RUB")
            & (operations_df["Статус"] == "OK")
            & (operations_df["Сумма платежа"] > 0)
        ]

        if len(filtered_operations) > 0:
            logger.info("Определение общей суммы доходов.")
            total_amount = round(float(filtered_operations["Сумма платежа"].sum()), 2)

            logger.info("Группировка данных по категориям.")
            categories = filtered_operations[["Категория", "Сумма платежа"]].groupby("Категория").sum().reset_index()
            categories["Сумма платежа"] = round(categories["Сумма платежа"], 2)
            sorted_operations = categories.sort_values(by="Сумма платежа", key=lambda x: x, ascending=False)
            new_names = {"Категория": "category", "Сумма платежа": "amount"}
            categories_list = sorted_operations.rename(columns=new_names)
            main = categories_list.to_dict(orient="records")

            income = {
                "total_amount": total_amount,
                "main": main,
            }
            logger.info("Работа функции завершена. Данные успешно получены.")
            return income
        else:
            logger.error("Работа функции завершена. Фильтрация не дала результата.")
            return {}
    else:
        logger.error("Работа функции завершена. Перечень операций не содержит данных.")
        return {}
