import sqlite3
from datetime import datetime
from kivymd.uix.button import MDIconButton
from kivymd.uix.snackbar import Snackbar
# from sqlalchemy import Column, String, Integer, create_engine, Float, desc
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
#
# Base = declarative_base()
#
#
# class CostControl(Base):
#     """Таблица для DB"""
#
#     __tablename__ = 'CostControl'
#
#     id = Column(Integer, primary_key=True)
#     description = Column(String(50), nullable=False)
#     category = Column(String())
#     costs = Column(String())
#     price = Column(Float, nullable=False)
#     date = Column(String)
#
#     def __repr__(self):
#         return f'{self.id} - {self.description}: {self.costs} - {self.price}'
#
#     def __str__(self):
#         return self.description


class DataBase:
    """Создание/вызов базы данных"""

    def __init__(self):
        self.connection = sqlite3.connect("project/cost_control.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS CostControl (
            id integer primary key,
            description text,
            category text,
            costs text,
            price real,
            date text)
            """
        )
        self.connection.commit()
        # engine = create_engine('postgresql+psycopg2://postgres:karmavdele@localhost/cost_control')
        # Base.metadata.create_all(engine)
        # session = sessionmaker(engine)
        # self.connection = session()

    def cost_data(self):
        """Поиск цены и тип каждой записи для расчетов"""

        reports = self.cursor.execute("""SELECT costs, price FROM CostControl""")
        # reports = self.connection.query(CostControl.costs, CostControl.price).all()
        return reports.fetchall()

    def full_info_of_reports_for_cost(self):
        reports = self.cursor.execute("""SELECT category, price FROM CostControl WHERE costs=?""", ("Расход",))
        return reports.fetchall()

    def retrieve(self, report_id):
        """Поиск записи в BD"""

        report = self.cursor.execute(f"""SELECT * FROM CostControl WHERE id=?""", (report_id,))
        # report = self.connection.query(CostControl).get(report_id)
        return report.fetchone()

    def list(self, query=None):
        """Поиск записей в BD в зависимости от атрибута query"""

        if query:
            reports = self.cursor.execute(f"""SELECT * FROM CostControl WHERE description LIKE ? ORDER BY date DESC""",
                                          (query,))
            # reports = self.connection.query(CostControl).filter(
            #     CostControl.description.ilike(query)).order_by(desc(CostControl.date)).all()
        else:
            reports = self.cursor.execute(f"""SELECT * FROM CostControl ORDER BY date DESC""")
            # reports = self.connection.query(CostControl).order_by(desc(CostControl.date)).all()
        return reports.fetchall()

    def insert_data(self, description, category, cost, price):
        """Добавление записей в базу"""

        category, price = ValidateData.control_of_filling_the_price_and_category(category, cost, price)
        # cost = CostControl(description=description, category=category, costs=cost, price=price,
        #                    date=str(datetime.now())[:19])
        self.cursor.execute(
            """INSERT INTO CostControl (description, category, costs, price, date) VALUES (?, ?, ?, ?, ?)""",
            (description, category, cost, price, str(datetime.now())[:19])
        )
        # self.connection.add(cost)
        self.connection.commit()

    def update(self, instance, description, category, cost, price):
        """Обновление записи"""

        category, price = ValidateData.control_of_filling_the_price_and_category(category, cost, price)
        self.cursor.execute(
            """UPDATE CostControl SET description=?, category=?, costs=?, price=?, date=? WHERE ID=?""",
            (description, category, cost, price, str(datetime.now())[:19], instance[0]))
        # instance.description = description
        # instance.category = category
        # instance.costs = cost
        # instance.price = price
        # instance.date = str(datetime.now())[:19]
        # self.connection.add(instance)
        self.connection.commit()

    def delete(self, report_id):
        """Удаление записи из BD"""

        self.cursor.execute("""DELETE FROM CostControl WHERE id=?""", (report_id,))
        # self.connection.query(CostControl).filter_by(id=report_id).delete()
        self.connection.commit()

    def delete_all_reports(self):
        """Удаление всех записей из BD"""

        self.cursor.execute("""DELETE FROM CostControl""")
        # self.connection.query(CostControl).delete()
        # self.connection.commit()


class ValidateData:
    """Валидатор полей"""

    def __init__(self, **kwargs):
        self.snackbar = Snackbar(font_size=14, snackbar_y=660, snackbar_animation_dir="Top",
                                 bg_color=(.85, .14, .23, 1))
        self.snackbar.buttons = [
            MDIconButton(icon="close", pos_hint={"center_y": .5}, on_release=self.snackbar.dismiss)
        ]

    def validate_description(self, description):
        """Валидация поля description"""

        if not description:
            self.snackbar.text = "Поле description не может быть пустым!"
            self.snackbar.open()
        elif len(description) > 50:
            self.snackbar.text = "Слишком много символов в description!"
            self.snackbar.open()
        else:
            return True

    def validate_price(self, price):
        """Валидация поля price"""

        if not price:
            self.snackbar.text = "Поле price не может быть пустым!"
            self.snackbar.open()
        else:
            try:
                float(price)
            except Exception:
                self.snackbar.text = "Поле price принимает только числа и точку!"
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
