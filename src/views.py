import json
import logging
from datetime import datetime
from typing import Any

from config import PATH_DATA, PATH_LOGS
from src import utils

logger = logging.getLogger("views")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(PATH_LOGS / "views.log", "w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def show_home_page(input_date: str | datetime) -> Any:
    """
    Функция формирует JSON-ответ с данными для заполнения главной страницы онлайн-банка (приветствие, данные о расходах
    по картам, ТОП-5 транзакций по сумме, курсы валют, стоимость акций).
    :param input_date: Дата, на которую выводится результат.
    :return: JSON-ответ с данными.
    """

    logger.info("Функция views.show_home_page запущена.")

    # Переводим дату из строки в datetime
    logger.info("Перевод даты из строки в datetime.")
    date = utils.format_date(input_date)

    # Определяем приветствие по дате и времени
    logger.info("Определение приветствия по дате и времени.")
    greeting = utils.get_greeting(date)

    # Извлекаем список операций из EXCEL
    logger.info("Извлечение списка операций из EXCEL.")
    file_excel = str(PATH_DATA / "operations.xlsx")
    operations = utils.import_excel_operations(file_excel)

    # Фильтруем список операций по дате
    logger.info("Фильтрация списка операций по дате.")
    operations_by_date = utils.filter_by_date(operations, date, period="M")

    # Получаем данные по картам и определяем ТОП-5 операций
    logger.info("Получение данных по картам и определение ТОП-5 операций.")
    if len(operations) > 0:
        cards = utils.get_cards(operations_by_date)
        top = utils.get_top_transactions(operations_by_date)
    else:
        cards = []
        top = []

    # Получаем список валют и акций из JSON-файла
    logger.info("Получение списка валют и акций из JSON-файла.")
    file_json = str(PATH_DATA / "user_settings.json")
    info = utils.read_json(file_json)
    user_currencies = info.get("user_currencies")
    user_stocks = info.get("user_stocks")

    # Получаем данные по курсам валют
    logger.info("Получение данных по курсам валют.")
    rates = utils.get_exchange_rates("RUB", user_currencies)

    # Получаем стоимость акций
    logger.info("Получение данных по стоимости акций.")
    stock_prices = utils.get_stock_price(user_stocks)

    # Формируем JSON-ответ
    result = {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top,
        "currency_rates": rates,
        "stock_prices": stock_prices,
    }

    logger.info("Работа функции завершена. JSON-ответ с полученными данными сформирован.")
    return json.dumps(result, indent=4, ensure_ascii=False)


def show_events_page(input_date: str | datetime, period: str = "M") -> Any:
    """
    Функция формирует JSON-ответ с данными для заполнения страницы онлайн-банка "События" (данные о расходах и доходах,
    курсы валют, стоимость акций).
    :param input_date: Дата, на которую выводится результат.
    :param period: Период, за который необходимо провести аналитику (с начала недели/месяца/года/за весь период до
    указанной даты).
    :return: JSON-ответ с данными.
    """

    logger.info("Функция views.show_events_page запущена.")

    # Переводим дату из строки в datetime
    logger.info("Перевод даты из строки в datetime.")
    date = utils.format_date(input_date)

    # Извлекаем список операций из EXCEL
    logger.info("Извлечение списка операций из EXCEL.")
    file_excel = str(PATH_DATA / "operations.xlsx")
    operations = utils.import_excel_operations(file_excel)

    # Фильтруем список операций по дате
    logger.info("Фильтрация списка операций по дате.")
    operations_by_date = utils.filter_by_date(operations, date, period)

    # Получаем данные о расходах
    logger.info("Получение данных о расходах.")
    expenses = utils.get_expenses(operations_by_date)

    # Получаем данные о доходах
    logger.info("Получение данных о доходах.")
    income = utils.get_income(operations_by_date)

    # Получаем список валют и акций из JSON-файла
    logger.info("Получение списка валют и акций из JSON-файла.")
    file_json = str(PATH_DATA / "user_settings.json")
    info = utils.read_json(file_json)
    user_currencies = info.get("user_currencies")
    user_stocks = info.get("user_stocks")

    # Получаем данные по курсам валют
    logger.info("Получение данных по курсам валют.")
    rates = utils.get_exchange_rates("RUB", user_currencies)

    # Получаем стоимость акций
    logger.info("Получение данных по стоимости акций.")
    stock_prices = utils.get_stock_price(user_stocks)

    # Формируем JSON-ответ
    result = {
        "expenses": expenses,
        "income": income,
        "currency_rates": rates,
        "stock_prices": stock_prices,
    }

    logger.info("Работа функции завершена. JSON-ответ с полученными данными сформирован.")
    return json.dumps(result, indent=4, ensure_ascii=False)
