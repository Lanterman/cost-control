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
            costs text,
            price real,
            date text)
            """
        )
        self.connection.commit()

    def insert_data(self, description, costs, price):
        """Добавление записей в базу"""
        self.cursor.execute(
            """INSERT INTO control (description, costs, price, date) VALUES (?, ?, ?, ?)""",
            (description, costs, price, str(datetime.now())[:19])
        )
        self.connection.commit()


class ValidateData:
    """Валидатор полей"""

    def validate_data(self, costs, price):
        """Валидатор полей"""
        information = 'P.S. Десятичные писать через точку!'
        if costs not in ('Расход', 'Доход'):
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
