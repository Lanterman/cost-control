import sqlite3
from datetime import datetime


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
