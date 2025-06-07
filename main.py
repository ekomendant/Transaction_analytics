from config import PATH_DATA
from src import reports, services, utils, views


def main() -> None:
    """
    Функция объединяет проект и позволяет выбрать, какой именно отчет получить.
    :return: None
    """

    print(
        "Выберите необходимый отчет:"
        '\n1. Получить JSON-ответ для страницы "Главная".'
        '\n2. Получить JSON-ответ для страницы "События".'
        "\n3. Получить JSON-ответ с выгодными категориями повышенного кэшбэка."
        "\n4. Отчет о расходах по категории за три месяца."
        "\n5. Отчет о средних расходах по дням недели за три месяца."
        "\n6. Отчет о средних расходах по рабочим/нерабочим дням за три месяца."
    )

    menu_selection = input("\nВведите номер соответствующего пункта: ")

    while int(menu_selection) < 1 or int(menu_selection) > 6:
        menu_selection = input("Номер пункта выбран неверно, введите цифру от 1 до 6: ")

    if int(menu_selection) == 1:
        date_input = input("\nВведите дату в формате YYYY-MM-DD HH:MM:SS: ")
        print("\nОтчет по заданным параметрам\n")
        print(views.show_home_page(date_input))
        # "2021-12-31 09:42:13"

    elif int(menu_selection) == 2:
        date_input = input("\nВведите дату в формате YYYY-MM-DD HH:MM:SS: ")
        period_input = input("Выберите период (W - неделя, M - месяц, Y - год, ALL - весь период: ")
        print("\nОтчет по заданным параметрам\n")
        print(views.show_events_page(date_input, period_input))

    elif 3 <= int(menu_selection) <= 6:
        file_excel = str(PATH_DATA / "operations.xlsx")
        operations = utils.import_excel_operations(file_excel)

        if int(menu_selection) == 3:
            year_input = int(input("\nВведите год: "))
            month_input = int(input("Введите месяц: "))

            transactions = operations.to_dict(orient="records")

            print("\nОтчет по заданным параметрам\n")
            print(services.profitable_categories(transactions, year_input, month_input))

        elif int(menu_selection) == 4:
            category_input = input("\nВведите категорию расходов: ")
            date_input = input("Введите дату в формате YYYY-MM-DD HH:MM:SS: ")

            print("\nОтчет по заданным параметрам\n")
            print(reports.spending_by_category(operations, category_input, date_input))

        elif int(menu_selection) == 5:
            date_input = input("\nВведите дату в формате YYYY-MM-DD HH:MM:SS: ")

            print("\nОтчет по заданным параметрам\n")
            print(reports.spending_by_weekday(operations, date_input))

        elif int(menu_selection) == 6:
            date_input = input("\nВведите дату в формате YYYY-MM-DD HH:MM:SS: ")

            print("\nОтчет по заданным параметрам\n")
            print(reports.spending_by_workday(operations, date_input))
