import sqlite3
from datetime import datetime
from tkinter import messagebox


class DataBase:
    """Создание/вызов базы данных"""
    def __init__(self):
        self.connection = sqlite3.connect("control.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS control (
            id integer primary key,
            description text,
            category text,
            costs text,
            price real,
            date text)
            """
        )
        self.connection.commit()

    def insert_data(self, description, category, costs, price):
        """Добавление записей в базу"""
        if costs == 'Доход':
            category = '---------'
        self.cursor.execute(
            """INSERT INTO control (description, category, costs, price, date) VALUES (?, ?, ?, ?, ?)""",
            (description, category, costs, price, str(datetime.now())[:19])
        )
        self.connection.commit()


class ValidateData:
    """Валидатор полей"""

    def validate_data(self, category, costs, price):
        """Валидатор полей"""
        information = 'P.S. Десятичные писать через точку!'
        if category not in ('---------', 'продукты', 'транспорт', 'связь', 'работа', 'хобби', 'дом', 'копилка'):
            messagebox.showwarning("Ошибка заполнения!", f"Нет такой категории - '{category}'!")
        elif not costs:
            messagebox.showwarning("Ошибка заполнения!", "Обязаное поле для заполенения!")
        elif costs == '---------':
            messagebox.showwarning("Ошибка заполнения!", "Выберите действие!")
        elif costs not in ('Расход', 'Доход'):
            messagebox.showwarning("Ошибка заполнения!", f"Нет такого действия - '{costs}'!")
        elif not price:
            messagebox.showwarning("Ошибка заполнения!", "Сумма не может быть пустой!")
        elif price:
            try:
                float(price)
            except Exception:
                messagebox.showwarning("Ошибка заполнения!",
                                       f"Допустимы только числа(простые и десятичные) - '{price}'!\n{information}")
            else:
                return True

    def control_of_filling_the_price(self, cost, price):
        """Конроль знака в зависимости от действия"""
        if cost == 'Расход' and price[0] != '-':
            price = '-' + price
        elif cost == 'Доход' and price[0] == '-':
            price = price[1:]
        return round(float(price), 2)
