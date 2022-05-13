from datetime import datetime
from kivymd.uix.button import MDIconButton
from kivymd.uix.snackbar import Snackbar
from sqlalchemy import Column, String, Integer, create_engine, Float, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class CostControl(Base):
    """Таблица для DB"""
    __tablename__ = 'CostControl'

    id = Column(Integer, primary_key=True)
    description = Column(String(50), nullable=False)
    category = Column(String())
    costs = Column(String())
    price = Column(Float, nullable=False)
    date = Column(String)

    def __repr__(self):
        return f'{self.id} - {self.description}: {self.costs} - {self.price}'

    def __str__(self):
        return self.description


class DataBase:
    """Создание/вызов базы данных"""
    def __init__(self):
        engine = create_engine('postgresql+psycopg2://postgres:karmavdele@localhost/cost_control')
        Base.metadata.create_all(engine)
        session = sessionmaker(engine)
        self.connection = session()

    def retrieve(self, report_id):
        """Поиск записи в BD"""
        report = self.connection.query(CostControl).get(report_id)
        return report

    def list(self, query=None):
        """Поиск записей в BD в зависимости от атрибута query"""
        if query:
            reports = self.connection.query(CostControl).filter(
                CostControl.description.ilike(query)).order_by(desc(CostControl.date)).all()
        else:
            reports = self.connection.query(CostControl).order_by(desc(CostControl.date)).all()
        return reports

    def insert_data(self, description, category, cost, price):
        """Добавление записей в базу"""
        category, price = ValidateData.control_of_filling_the_price_and_category(category, cost, price)
        cost = CostControl(description=description, category=category, costs=cost, price=price,
                           date=str(datetime.now())[:19])
        self.connection.add(cost)
        self.connection.commit()

    def update(self, instance, description, category, cost, price):
        """Обновление записи"""
        category, price = ValidateData.control_of_filling_the_price_and_category(category, cost, price)
        instance.description = description
        instance.category = category
        instance.costs = cost
        instance.price = price
        instance.date = str(datetime.now())[:19]
        self.connection.add(instance)
        self.connection.commit()

    def delete(self, report_id):
        """Удаление записи из BD"""
        self.connection.query(CostControl).filter_by(id=report_id).delete()
        self.connection.commit()


class ValidateData:
    """Валидатор полей"""

    def __init__(self, **kwargs):
        self.snackbar = Snackbar(font_size=14, snackbar_y=660, snackbar_animation_dir="Top",
                                 bg_color=(.85, .14, .23, 1))
        self.snackbar.buttons = [
            MDIconButton(icon="close", pos_hint={"center_y": .5}, on_release=self.snackbar.dismiss)]

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
