from datetime import datetime
from kivymd.uix.button import MDIconButton
from kivymd.uix.snackbar import Snackbar
from kivy.core.window import Window
from sqlalchemy import Column, String, Integer, create_engine, Float, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class CostControl(Base):
    """Таблица для DB"""

    __tablename__ = 'CostControl'

    id = Column(Integer, primary_key=True)
    description = Column(String(100), nullable=False)
    category = Column(String())
    costs = Column(String)
    price = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    date = Column(String)

    def __repr__(self):
        return f'{self.id} - {self.description}: {self.costs} - {self.price}'

    def __str__(self):
        return self.description


class Exchange(Base):
    """Таблица для DB"""

    __tablename__ = 'Exchange'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    buy = Column(String, nullable=False)
    sell = Column(String, nullable=False)
    date = Column(String)

    def __repr__(self):
        return f'{self.id} - {self.name}: {self.buy} - {self.sell}'

    def __str__(self):
        return self.name


class CurrentCurrency(Base):
    """Таблица для DB"""

    __tablename__ = 'CurrentCurrency'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    def __repr__(self):
        return f'{self.id} - {self.name}'

    def __str__(self):
        return self.name


class DataBase:
    """Создание/вызов базы данных"""

    def __init__(self):
        engine = create_engine('postgresql+psycopg2://postgres:karmavdele@localhost/cost_control')
        Base.metadata.create_all(engine)
        session = sessionmaker(engine)
        self.connection = session()

    def show_currency(self):
        """Получить название валюты"""

        current_currency = self.connection.query(CurrentCurrency).first()
        return current_currency

    def create_report_in_current_currency(self):
        """Создать запись с курсом"""

        current = CurrentCurrency(name="BYN")
        self.connection.add(current)
        self.connection.commit()

    def update_report_of_current_currency(self, currency, instance):
        """Обновить курс"""

        instance.name = currency
        self.connection.add(instance)
        self.connection.commit()

    def records_output_from_exchange_db(self):
        """Вывод записей из exchange table"""

        reports = self.connection.query(Exchange).all()
        return reports

    def insert_data_in_exchange_db(self, reports):
        """Добавление записей в exchange table"""

        list_reports = []
        for item in reports:
            report = Exchange(name=item[0], buy=item[1], sell=item[2],
                              date=str(datetime.now().strftime("%d.%m.%Y %H:%M")))
            list_reports.append(report)
        self.connection.add_all(list_reports)
        self.connection.commit()

    def update_data_in_exchange_db(self, reports, instances):
        """Обновление записей в exchange table"""

        for id_currency, item in enumerate(reports, 0):
            instances[id_currency].name = item[0]
            instances[id_currency].buy = item[1]
            instances[id_currency].sell = item[2]
            instances[id_currency].date = str(datetime.now().strftime("%d.%m.%Y %H:%M"))
        self.connection.add_all(instances)
        self.connection.commit()

    def cost_data(self, currency):
        """Поиск цены и тип каждой записи для расчетов"""

        reports = self.connection.query(CostControl.costs,
                                        CostControl.price).filter(CostControl.currency == currency).all()
        return reports

    def full_info_of_reports_for_cost(self, currency):
        """Вывод записей с расходом"""

        reports = self.connection.query(
            CostControl.category,
            CostControl.price).filter(CostControl.costs == "Расход", CostControl.currency == currency).all()
        return reports

    def retrieve(self, report_id):
        """Поиск записи в BD"""

        report = self.connection.query(CostControl).get(report_id)
        return report

    def list(self, currency, query=None):
        """Поиск записей в BD в зависимости от атрибута query"""

        if query:
            reports = self.connection.query(CostControl).filter(
                CostControl.description.ilike(query),
                CostControl.currency == currency).order_by(desc(CostControl.id)).all()
        else:
            reports = self.connection.query(CostControl).filter(
                CostControl.currency == currency).order_by(desc(CostControl.id)).all()
        return reports

    def insert_data(self, description, category, cost, price, currency):
        """Добавление записей в базу"""

        category, price = ValidateData.control_of_filling_the_price_and_category(category, cost, price)
        report = CostControl(description=description, category=category, costs=cost, price=price, currency=currency,
                             date=str(datetime.now().strftime("%d.%m.%Y %H:%M")))
        self.connection.add(report)
        self.connection.commit()

    def update(self, instance, description, category, cost, price):
        """Обновление записи"""

        category, price = ValidateData.control_of_filling_the_price_and_category(category, cost, price)
        instance.description = description
        instance.category = category
        instance.costs = cost
        instance.price = price
        instance.date = str(datetime.now().strftime("%d.%m.%Y %H:%M"))
        self.connection.add(instance)
        self.connection.commit()

    def delete(self, report_id):
        """Удаление записи из BD"""

        self.connection.query(CostControl).filter_by(id=report_id).delete()
        self.connection.commit()

    def delete_all_reports(self):
        """Удаление всех записей из BD"""

        self.connection.query(CostControl).delete()
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
