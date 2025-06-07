import json
import logging
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Optional

from dateutil.relativedelta import relativedelta
from pandas import DataFrame

from config import PATH_DATA, PATH_LOGS, REPORT
from src import utils

logger = logging.getLogger("reports")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(PATH_LOGS / "reports.log", "w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def write_report(filename: str = str(REPORT)) -> Callable:
    """
    Декоратор для функций-отчетов, который записывает в файл результат функции, формирующей отчет.
    :param filename: Имя файла для записи отчета.
    :return: На выходе записывает отчет в файл.
    """

    def wrapper(function: Callable) -> Callable:
        @wraps(function)
        def inner(*args: Any, **kwargs: Any) -> Any | None:
            logger.info("Декоратор reports.write_report запущен.")
            logger.info(f"Вызов функции {function.__name__}.")
            result = function(*args, **kwargs).to_dict(orient="records")
            logger.info(f"Преобразование данных в JSON и запись в {filename}.")
            with open(filename, "w", encoding="utf-8") as file:
                json.dump(result, file, indent=4, ensure_ascii=False)
            return result

        return inner

    return wrapper


@write_report(filename=str(PATH_DATA / "spending_by_category.json"))
def spending_by_category(transactions: DataFrame, category: str, date: Optional[str] = None) -> DataFrame:
    """
    Функция возвращает траты по заданной категории за последние три месяца (от переданной даты).
    :param transactions: DataFrame с операциями для фильтрации.
    :param category: Категория, по которой фильтруются операции.
    :param date: Дата завершения анализируемого периода.
    :return: DataFrame с отфильтрованными по условию операциями.
    """

    logger.info("Функция reports.spending_by_category запущена.")
    logger.info("Определение периода анализа данных.")
    if date is not None:
        finish_date = utils.format_date(date)
    else:
        finish_date = datetime.now()

    start_date = finish_date - relativedelta(months=3)

    if len(transactions) > 0:
        logger.info("Фильтрация перечня транзакций.")
        filtered_operations = transactions[
            (transactions["Дата операции"] >= start_date)
            & (transactions["Дата операции"] <= finish_date)
            & (transactions["Категория"] == category)
            & (transactions["Валюта платежа"] == "RUB")
            & (transactions["Статус"] == "OK")
            & (transactions["Сумма платежа"] < 0)
        ].reset_index()

        filtered_operations["Дата операции"] = filtered_operations["Дата операции"].apply(
            lambda x: x.strftime("%d.%m.%Y %H:%M:%S")
        )

        result = filtered_operations[
            ["Дата операции", "Номер карты", "Сумма платежа", "Валюта платежа", "Категория", "Описание"]
        ]

        logger.info("Работа функции завершена. Данные по категории успешно получены.")
        return result
    else:
        logger.error("Работа функции завершена. Перечень операций не содержит данных.")
        return transactions


@write_report(filename=str(PATH_DATA / "spending_by_weekday.json"))
def spending_by_weekday(transactions: DataFrame, date: Optional[str] = None) -> DataFrame:
    """
    Функция возвращает средние траты в каждый из дней недели за последние три месяца (от переданной даты).
    :param transactions: DataFrame с операциями для фильтрации.
    :param date: Дата завершения анализируемого периода.
    :return: DataFrame с отфильтрованными по условию операциями.
    """

    logger.info("Функция reports.spending_by_weekday запущена.")
    logger.info("Определение периода анализа данных.")
    if date is not None:
        finish_date = utils.format_date(date)
    else:
        finish_date = datetime.now()

    start_date = finish_date - relativedelta(months=3)

    if len(transactions) > 0:
        logger.info("Фильтрация перечня транзакций.")
        filtered_operations = transactions[
            (transactions["Дата операции"] >= start_date)
            & (transactions["Дата операции"] <= finish_date)
            & (transactions["Валюта платежа"] == "RUB")
            & (transactions["Статус"] == "OK")
            & (transactions["Сумма платежа"] < 0)
        ].reset_index()

        if len(filtered_operations) > 0:
            logger.info("Группировка данных по дням недели.")
            weekdays = {1: "1. ПН", 2: "2. ВТ", 3: "3. СР", 4: "4. ЧТ", 5: "5. ПТ", 6: "6. СБ", 7: "7. ВС"}

            filtered_operations["День недели"] = filtered_operations["Дата операции"].dt.dayofweek + 1
            filtered_operations["День недели"] = filtered_operations["День недели"].map(weekdays)

            expenses_by_weekday = (
                filtered_operations[["День недели", "Сумма платежа"]].groupby("День недели").mean().reset_index()
            )
            expenses_by_weekday["Сумма платежа"] = abs(round(expenses_by_weekday["Сумма платежа"], 2))
            new_names = {"День недели": "День недели", "Сумма платежа": "Средняя сумма платежей"}
            expenses_by_weekday = expenses_by_weekday.rename(columns=new_names)

            logger.info("Работа функции завершена. Средние расходы по дням недели успешно получены.")
            return expenses_by_weekday
        else:
            logger.error("Работа функции завершена. Фильтрация данных не дала результата.")
            return filtered_operations
    else:
        logger.error("Работа функции завершена. Перечень операций не содержит данных.")
        return transactions


@write_report(filename=str(PATH_DATA / "spending_by_workday.json"))
def spending_by_workday(transactions: DataFrame, date: Optional[str] = None) -> DataFrame:
    """
    Функция выводит средние траты в рабочий и в выходной день за последние три месяца (от переданной даты).
    :param transactions: DataFrame с операциями для фильтрации.
    :param date: Дата завершения анализируемого периода.
    :return: DataFrame с отфильтрованными по условию операциями.
    """

    logger.info("Функция reports.spending_by_workday запущена.")
    logger.info("Определение периода анализа данных.")
    if date is not None:
        finish_date = utils.format_date(date)
    else:
        finish_date = datetime.now()

    start_date = finish_date - relativedelta(months=3)

    if len(transactions) > 0:
        logger.info("Фильтрация перечня транзакций.")
        filtered_operations = transactions[
            (transactions["Дата операции"] >= start_date)
            & (transactions["Дата операции"] <= finish_date)
            & (transactions["Валюта платежа"] == "RUB")
            & (transactions["Статус"] == "OK")
            & (transactions["Сумма платежа"] < 0)
        ].reset_index()

        if len(filtered_operations) > 0:
            logger.info("Группировка данных по рабочим и выходным дням.")
            workdays = {
                1: "Рабочий",
                2: "Рабочий",
                3: "Рабочий",
                4: "Рабочий",
                5: "Рабочий",
                6: "Выходной",
                7: "Выходной",
            }

            filtered_operations["День недели"] = filtered_operations["Дата операции"].dt.dayofweek + 1
            filtered_operations["День недели"] = filtered_operations["День недели"].map(workdays)

            expenses_by_workday = (
                filtered_operations[["День недели", "Сумма платежа"]].groupby("День недели").mean().reset_index()
            )
            expenses_by_workday["Сумма платежа"] = abs(round(expenses_by_workday["Сумма платежа"], 2))
            new_names = {"День недели": "День недели", "Сумма платежа": "Средняя сумма платежей"}
            expenses_by_workday = expenses_by_workday.rename(columns=new_names)

            logger.info("Работа функции завершена. Средние расходы по рабочим и выходным дням успешно получены.")
            return expenses_by_workday
        else:
            logger.error("Работа функции завершена. Фильтрация данных не дала результата.")
            return filtered_operations
    else:
        logger.error("Работа функции завершена. Перечень операций не содержит данных.")
        return transactions
