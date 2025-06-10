import calendar
import json
import logging
from datetime import datetime
from typing import Any

from pandas import DataFrame

from config import PATH_LOGS

logger = logging.getLogger("services")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(PATH_LOGS / "services.log", "w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def profitable_categories(data: list, year: int, month: int) -> Any:
    """
    Функция определяет выгодные категории повышенного кэшбэка, основываясь на сумме расходов по каждой категории за
    выбранный месяц.
    :param data: Список словарей с операциями.
    :param year: Год для определения месяца анализа.
    :param month: Месяц за который необходимо провести анализ.
    :return: JSON-ответ с перечнем категорий и суммой потенциального кэшбэка.
    """

    logger.info("Функция services.profitable_categories запущена.")
    if len(data) == 0:
        logger.error("Работа функции завершена. Список операций не содержит данных.")
        return json.dumps({}, indent=4, ensure_ascii=False)
    else:
        if month < 1 or month > 12:
            logger.error("Работа функции завершена. Указан несуществующий месяц.")
            return json.dumps({}, indent=4, ensure_ascii=False)
        else:
            _, last_day = calendar.monthrange(year, month)
            start_date = datetime(year, month, 1, 0, 0, 0)
            finish_date = datetime(year, month, last_day, 23, 59, 59)

            df = DataFrame(data)

            logger.info("Фильтрация данных по заданным параметрам.")
            filtered_operations = df[
                (df["Валюта платежа"] == "RUB")
                & (df["Статус"] == "OK")
                & (df["Сумма платежа"] < 0)
                & (df["Дата операции"] <= finish_date)
                & (df["Дата операции"] >= start_date)
                & (df["Категория"] != "Переводы")
                & (df["Категория"] != "Наличные")
                & (df["Категория"] != "Другое")
            ]

            if len(filtered_operations) > 0:
                categories = (
                    filtered_operations[["Категория", "Сумма платежа"]].groupby("Категория").sum().reset_index()
                )
                categories["Сумма платежа"] = round(abs(categories["Сумма платежа"]) / 100, 2)
                sorted_operations = categories.sort_values(
                    by="Сумма платежа", key=lambda x: x, ascending=False
                ).reset_index()
                result = dict(zip(sorted_operations["Категория"], sorted_operations["Сумма платежа"]))

                logger.info("Работа функции завершена. Данные успешно получены.")
                return json.dumps(result, indent=4, ensure_ascii=False)
            else:
                logger.error("Работа функции завершена. Фильтрация не дала результата.")
                return json.dumps({}, indent=4, ensure_ascii=False)
