from datetime import datetime
from tkinter import messagebox
from sqlalchemy import Column, String, Integer, create_engine, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class CostControl(Base):
    __tablename__ = 'CostControl'

    id = Column(Integer, primary_key=True)
    description = Column(String(50), nullable=False)
    category = Column(String(50))
    costs = Column(String(50))
    price = Column(Float, default=0)
    date = Column(String, default=str(datetime.now())[:19])

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

    def insert_data(self, description, category, costs, price):
        """Добавление записей в базу"""
        if costs == 'Доход':
            category = '---------'
        cost = CostControl(description=description, category=category, costs=costs, price=price)
        self.connection.add(cost)
        self.connection.commit()

    def apply_change(self, instance, description, category, cost, price):
        instance.description = description
        instance.category = category
        instance.costs = cost
        instance.price = price
        instance.date = str(datetime.now())[:19]
        self.connection.add(instance)
        self.connection.commit()


class ValidateData:
    """Валидатор полей"""

    @staticmethod
    def validate_data(category, costs, price):
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

    @staticmethod
    def control_of_filling_the_price(cost, price):
        """Конроль знака в зависимости от действия"""
        if cost == 'Расход' and price[0] != '-':
            price = '-' + price
        elif cost == 'Доход' and price[0] == '-':
            price = price[1:]
        return round(float(price), 2)
