import sqlite3
from datetime import datetime
from kivy.core.window import Window
from kivymd.uix.button import MDIconButton
from kivymd.uix.snackbar import Snackbar


class DataBase:
    """Создание/вызов базы данных"""

    def __init__(self):
        self.connection = sqlite3.connect(r"project/cost_control.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS CostControl (
            id INTEGER PRIMARY KEY,
            description TEXT,
            category TEXT,
            costs TEXT,
            price REAL,
            date TEXT);
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS exchange (
            id INTEGER PRIMARY KEY,
            name TEXT,
            buy TEXT,
            sell TEXT,
            date TEXT);
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS current_currency (
            id INTEGER PRIMARY KEY, 
            name TEXT);
            """
        )
        self.connection.commit()

    def show_currency(self):
        """"""
        current_currency = self.cursor.execute("""SELECT * FROM current_currency""").fetchone()
        return current_currency

    def create_report_in_current_currency(self):
        self.cursor.execute("""INSERT INTO current_currency (name) VALUES (?)""", ("BYN",))
        self.connection.commit()

    def update_report_of_current_currency(self, currency):
        self.cursor.execute("""UPDATE current_currency SET  name=? WHERE id=?""", (currency, 1))
        self.connection.commit()

    def records_output_from_exchange_db(self):
        """Вывод записей из exchange table"""

        reports = self.cursor.execute("""SELECT * FROM exchange""")
        return reports.fetchall()

    def insert_data_in_exchange_db(self, data):
        """Добавление записей в exchange table"""

        for report in data:
            self.cursor.execute(
                """INSERT INTO exchange (name, buy, sell, date) VALUES (?, ?, ?, ?)""",
                (report[0], report[1], report[2], str(datetime.now().strftime("%d.%m.%Y %H:%M")))
            )
        self.connection.commit()

    def update_data_in_exchange_db(self, data):
        """Обновление записей в exchange table"""

        for report in data:
            self.cursor.execute(
                """UPDATE exchange SET  buy=?, sell=?, date=? WHERE name=?""",
                (report[1], report[2], str(datetime.now().strftime("%d.%m.%Y %H:%M")), report[0])
            )
        self.connection.commit()

    def cost_data(self):
        """Поиск цены и тип каждой записи для расчетов"""

        reports = self.cursor.execute("""SELECT costs, price FROM CostControl""")
        return reports.fetchall()

    def full_info_of_reports_for_cost(self):
        """Вывод записей с расходом"""

        reports = self.cursor.execute("""SELECT category, price FROM CostControl WHERE costs=?""", ("Расход",))
        return reports.fetchall()

    def retrieve(self, report_id):
        """Поиск записи в BD"""

        report = self.cursor.execute(f"""SELECT * FROM CostControl WHERE id=?""", (report_id,))
        return report.fetchone()

    def list(self, query=None):
        """Поиск записей в BD в зависимости от атрибута query"""

        if query:
            reports = self.cursor.execute(
                f"""SELECT * FROM CostControl WHERE description LIKE ? ORDER BY id DESC""",
                (query,)
            )
        else:
            reports = self.cursor.execute(f"""SELECT * FROM CostControl ORDER BY id DESC""")
        return reports.fetchall()

    def insert_data(self, description, category, cost, price):
        """Добавление записей в базу"""

        category, price = ValidateData.control_of_filling_the_price_and_category(category, cost, price)
        self.cursor.execute(
            """INSERT INTO CostControl (description, category, costs, price, date) VALUES (?, ?, ?, ?, ?)""",
            (description, category, cost, price, str(datetime.now().strftime("%d.%m.%Y %H:%M")))
        )
        self.connection.commit()

    def update(self, instance, description, category, cost, price):
        """Обновление записи"""

        category, price = ValidateData.control_of_filling_the_price_and_category(category, cost, price)
        self.cursor.execute(
            """UPDATE CostControl SET description=?, category=?, costs=?, price=?, date=? WHERE ID=?""",
            (description, category, cost, price, str(datetime.now().strftime("%d.%m.%Y %H:%M")), instance[0])
        )
        self.connection.commit()

    def delete(self, report_id):
        """Удаление записи из BD"""

        self.cursor.execute("""DELETE FROM CostControl WHERE id=?""", (report_id,))
        self.connection.commit()

    def delete_all_reports(self):
        """Удаление всех записей из BD"""

        self.cursor.execute("""DELETE FROM CostControl""")
        self.connection.commit()


class ValidateData:
    """Валидатор полей"""

    def __init__(self, **kwargs):
        self.snackbar = Snackbar(font_size="14sp", snackbar_y=Window.width * 2, snackbar_animation_dir="Top",
                                 bg_color=(.85, .14, .23, 1))
        self.snackbar.buttons = [
            MDIconButton(icon="close", pos_hint={"center_y": .5}, on_release=self.snackbar.dismiss)
        ]

    def validate_description(self, description):
        """Валидация поля description"""

        if not description:
            self.snackbar.text = "Поле 'описание' не может быть пустым!"
            self.snackbar.open()
        elif len(description) > 100:
            self.snackbar.text = "Слишком много символов в описании!"
            self.snackbar.open()
        else:
            return True

    def validate_price(self, price):
        """Валидация поля price"""

        if not price:
            self.snackbar.text = "Поле 'цена' не может быть пустым!"
            self.snackbar.open()
        else:
            try:
                float(price)
            except Exception:
                self.snackbar.text = "Поле 'цена' принимает числа и точку!"
                self.snackbar.open()
            else:
                return True

    def validate_data(self, description, price):
        """Валидатор полей"""

        if self.validate_description(description):
            if self.validate_price(price):
                return True

    @staticmethod
    def control_of_filling_the_price_and_category(category, cost, price):
        """Конроль знака в зависимости от действия"""

        if cost == 'Доход':
            category = '---------'
        if cost == 'Расход' and price[0] != '-':
            price = '-' + price
        elif cost == 'Доход' and price[0] == '-':
            price = price[1:]
        return category, round(float(price), 2)
