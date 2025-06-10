import json

from src.services import profitable_categories

""" Тестирование функции src.services.profitable_categories """


def test_profitable_categories(top_transactions_original, top_transactions_no_filter):
    data = top_transactions_original.to_dict(orient="records")
    data_no_filter = top_transactions_no_filter.to_dict(orient="records")
    result = json.dumps({"Аптеки": 3.15, "Каршеринг": 1.28, "Связь": 0.18}, indent=4, ensure_ascii=False)
    result_null = json.dumps({}, indent=4, ensure_ascii=False)

    # Проверка работы функции с корректными параметрами
    assert profitable_categories(data, 2021, 12) == result

    # Проверка работы функции с пустым списком операций
    assert profitable_categories([], 2021, 12) == result_null

    # Проверка работы функции с некорректной датой
    assert profitable_categories(data, 2021, 13) == result_null

    # Проверка работы функции, если фильтрация не дала результата
    assert profitable_categories(data_no_filter, 2021, 12) == result_null
