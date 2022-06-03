import requests
from kivy.core.window import Window
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.snackbar import Snackbar
from project.database import DataBase, ValidateData
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import ThreeLineAvatarIconListItem

db = DataBase()


class MainWindow(MDBoxLayout):
    """Основное окно"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_exist_report = db.show_currency()
        self.currency = self.is_exist_report[1] if self.is_exist_report else "BYN"
        if not self.is_exist_report:
            db.create_report_in_current_currency()
        self.set_title_toolbar(self.currency)

    def show_menu_courses(self):
        """Меню работы с записями"""

        items = [
            {"text": "RUB", "viewclass": "OneLineListItem", "on_release": lambda x="RUB": self.set_currency(x)},
            {"text": "BYN", "viewclass": "OneLineListItem", "on_release": lambda x="BYN": self.set_currency(x)},
            {"text": "USD", "viewclass": "OneLineListItem", "on_release": lambda x="USD": self.set_currency(x)}
        ]
        self.menu_courses = DropDownMenuReportsBox(caller=self.ids.tool, items=items, max_height="147sp",
                                                   width_mult=1.3, hor_growth="left")
        self.menu_courses.open()

    def set_currency(self, x):
        """Установить курс"""

        self.currency = x
        self.menu_courses.dismiss()
        db.update_report_of_current_currency(self.currency)
        self.set_title_toolbar(self.currency)
        self.ids.main_nav.all_reports(self.currency)
        self.ids.cost_nav.set_values(self.currency)
        self.ids.exchange_nav.set_course_api(change_course=True)

    def set_title_toolbar(self, currency):
        """Установить название"""

        self.ids.tool.title = f"Cost Control({currency})"

    @staticmethod
    def clear_db():
        """Удаление всех записей с БД"""

        delete_dialog = MDDialog(title=3 * " " + "Удалить все записи?",
                                 text="Это действие безвозвартно удалит все записи!",
                                 radius=[20, 20, 20, 20])
        delete_dialog.buttons = [
            ButtonToDeleteAllReports(text="OK", instance=delete_dialog),
            ButtonToDeleteAllReports(text="Cancel", instance=delete_dialog)
        ]
        delete_dialog.create_buttons()
        delete_dialog.ids.root_button_box.height = "40sp"
        delete_dialog.open()


class DropDownMenuReportsBox(MDDropdownMenu):
    """Виджет меню выбора значения для поля"""


class IfNoRecords(MDLabel):
    """Установить метку, если нет записей"""


class CostDataLabel(MDLabel):
    """Метка вкладки расчетов"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_size = "18sp"
        self.halign = "center"


class ButtonToApplyChangesToReport(MDRaisedButton):
    """Кнопки модального окна изменения записи"""

    def __init__(self, obj_dialog, box_item_edit=None, obj_report=None, **kwargs):
        super().__init__(**kwargs)
        self.font_size = "16sp"

        self.app = MDApp.get_running_app()
        self.obj_dialog = obj_dialog
        self.box_item_edit = box_item_edit
        self.obj_report = obj_report

    def apply_change(self, description, category, cost, price):
        """Обновить запись"""

        if ValidateData().validate_data(description, price):
            if self.obj_report[1:-2] != (description, category, cost, float(price)):
                db.update(self.obj_report, description, category, cost, price)
                Snackbar(text=20 * " " + f"Запись {self.obj_report[0]} обновлена!", font_size="18sp",
                         snackbar_y=Window.width * 2, snackbar_animation_dir="Top").open()
            self.obj_dialog.dismiss()

    def on_press(self):
        """Действие при нажатии на кнопку"""

        if self.box_item_edit:
            self.apply_change(
                self.box_item_edit.ids.changed_description.text,
                self.box_item_edit.ids.drop_item_category.ids.label_item.text,
                self.box_item_edit.ids.drop_item_costs.ids.label_item.text,
                self.box_item_edit.ids.changed_price.text
            )
            self.app.root.ids.main_nav.all_reports(self.app.root.currency)
        else:
            self.obj_dialog.dismiss()


class ButtonToDeleteAllReports(MDFlatButton):
    """Кнопки модального окна удаления всех записей """

    def __init__(self, instance, **kwargs):
        super().__init__(**kwargs)
        self.font_size = "16sp"
        self.instance = instance
        self.app = MDApp.get_running_app()

    def on_press(self):
        """Действие при нажатии на кнопку"""

        if self.text == "OK":
            db.delete_all_reports()
            screen_manager = self.app.root.ids.bottom_nav
            screen_manager.switch_tab("screen main")
        self.instance.dismiss()


class AbstractClassForDropDownMenu(MDBoxLayout):
    """Абстрактный класс для полей category и costs"""

    def drop_down_category_menu(self):
        """Выбор значения для категории записи"""

        category = ('---------', 'продукты', 'транспорт', 'медицина', 'связь', 'хобби', 'дом', 'копилка')
        menu_items = [{"text": item, "viewclass": "OneLineListItem",
                       "on_release": lambda item=item: self.set_item(item)} for item in category]
        self.menu = DropDownMenuReportsBox(caller=self.ids.drop_item_category, items=menu_items, max_height="230sp",
                                           width_mult=2.2)
        self.menu.open()

    def drop_down_cost_menu(self):
        """Выбор значения для типа записи"""

        costs = ('Расход', 'Доход')
        menu_items = [{"text": item, "viewclass": "OneLineListItem",
                       "on_release": lambda item=item: self.set_item(item)} for item in costs]
        self.menu = DropDownMenuReportsBox(caller=self.ids.drop_item_costs, items=menu_items, max_height="98sp",
                                           width_mult=1.9)
        self.menu.open()

    def set_item(self, item):
        """Установить значение для поля"""

        if item in ('Расход', 'Доход'):
            self.ids.drop_item_costs.set_item(item)
        else:
            self.ids.drop_item_category.set_item(item)
        self.menu.dismiss()


class BoxItemEditReport(AbstractClassForDropDownMenu):
    """Класс определяющий модальное окно обновление записи"""

    def __init__(self, report_id, **kwargs):
        super().__init__(**kwargs)
        self.report = db.retrieve(report_id)
        self.default_values()

    def default_values(self):
        """Вывод значения по умолчанию"""

        self.ids.changed_description.set_text(instance=None, text=self.report[1])
        self.ids.drop_item_category.set_item(self.report[2])
        self.ids.drop_item_costs.set_item(self.report[3])
        self.ids.changed_price.set_text(instance=None, text=str(self.report[4]))


class RecordWidget(ThreeLineAvatarIconListItem):
    """Класс отвечающий за функционал записей"""

    def __init__(self, instance, **kwargs):
        super(RecordWidget, self).__init__(**kwargs)
        self.instance = instance
        if self.instance[3] == "Расход":
            self.ids.md_icon.icon = "minus"
        else:
            self.ids.md_icon.icon = "plus"

    def show_menu(self):
        """Меню работы с записями"""

        items = [
            {"text": "Просмотр", "viewclass": "OneLineListItem", "on_release": lambda: self.show_report()},
            {"text": "Изменить", "viewclass": "OneLineListItem", "on_release": lambda: self.edit_report()},
            {"text": "Удалить", "viewclass": "OneLineListItem", "on_release": lambda: self.delete_report()}
             ]
        self.menu = DropDownMenuReportsBox(caller=self.ids.button, items=items, max_height="147sp", width_mult=2.2)
        self.menu.open()

    def show_report(self):
        """Модальное окно показа полной информации записи"""

        self.menu.dismiss()
        dialog_show_report = MDDialog(
            title=4 * " " + 'Полная информация',
            text=f"Описание:         {self.instance[1]}\n\n"
                 f"Категория:        {self.instance[2]}\n\n"
                 f"Тип:                    {self.instance[3]}\n\n"
                 f"Цена:                 {self.instance[4]} {self.instance[5]}\n\n"
                 f"Дата:                 {self.instance[6]}",
        )
        dialog_show_report.open()

    def edit_report(self):
        """Модальное окно обновление записи"""

        self.menu.dismiss()
        box_item_edit = BoxItemEditReport(report_id=self.instance[0])
        dialog_edit_report = MDDialog(title=6 * " " + "Изменить запись",
                                      type="custom",
                                      content_cls=box_item_edit)
        dialog_edit_report.buttons = [
            ButtonToApplyChangesToReport(text="Apply", obj_dialog=dialog_edit_report, box_item_edit=box_item_edit,
                                         obj_report=self.instance),
            ButtonToApplyChangesToReport(text="Cancel", obj_dialog=dialog_edit_report,
                                         text_color=(0.1, 0.1, 1, 1), md_bg_color=(0.86, 0.81, 0.81, 1))
        ]
        dialog_edit_report.create_buttons()
        dialog_edit_report.ids.root_button_box.height = "50sp"
        dialog_edit_report.open()

    def delete_report(self):
        """Удалить запись"""

        db.delete(self.instance[0])
        self.parent.remove_widget(self)
        self.menu.dismiss()


class MainNavigationItem(MDBoxLayout):
    """Вкладка с записями"""

    def searching_results(self, query, currency):
        """Вывод записей по поиску"""

        query = f'%{query}%'
        result = db.list(currency, query)
        self.show_results(result)

    def all_reports(self, currency):
        """Вывод всех записей"""

        result = db.list(currency)
        self.show_results(result)

    def show_results(self, query):
        """Логика вывода записей"""

        result_list_widget = self.ids.show_result
        result_list_widget.clear_widgets()
        if query:
            for report in query:
                space = 27 - len(report[3]) - len(str(report[4]))
                result_list_widget.add_widget(
                    RecordWidget(text=f'{report[1]}',
                                 secondary_text=report[3] + space * " " + str(report[4]) + f" {report[5]}",
                                 instance=report, tertiary_text=f'{report[6]}')
                )
        else:
            result_list_widget.add_widget(IfNoRecords())


class AddNavigationItem(AbstractClassForDropDownMenu):

    def insert_data(self, description, category, cost, price):
        """Добавление записи в BD"""

        if ValidateData().validate_data(description, price):
            app = MDApp.get_running_app()
            db.insert_data(description, category, cost, price, currency=app.root.currency)
            screen_manager = app.root.ids.bottom_nav
            self.clearing_text_widgets()
            screen_manager.switch_tab("screen main")

    def clearing_text_widgets(self):
        """Очистка текста виджетов после добавления записи"""

        self.ids.add_description.set_text(instance=None, text="")
        self.ids.drop_item_category.set_item("---------")
        self.ids.drop_item_costs.set_item("Расход")
        self.ids.add_price.set_text(instance=None, text="0")

    def cleaning_on_focus(self):
        """очистка поля при фокусировке"""

        if self.ids.add_price.text == "0":
            self.ids.add_price.text = ""


class CostNavigationItem(MDBoxLayout):
    """Вкладка расчетов"""

    def set_values(self, currency):
        """Установка текстовых значений"""

        reports = db.cost_data(currency)
        profit, income, expenditure = self.calculate_price(reports)
        self.ids.set_profit.text = f"Осталось:   {str(profit)} {currency}"
        self.ids.set_income.text = f"Заработано:   {str(income)} {currency}"
        self.ids.set_expenditure.text = f"Потрачено:   {str(expenditure)} {currency}"
        self.ids.set_description.text = self.description(reports, profit)

    @staticmethod
    def calculate_price(reports):
        """Расчет финансов"""

        profit = round(sum([price for cost, price in reports]), 2)
        income = round(sum([price for cost, price in reports if cost == 'Доход']), 2)
        expenditure = round(sum([price for cost, price in reports if cost == 'Расход']), 2)
        return profit, income, expenditure

    @staticmethod
    def description(reports, profit):
        """Дополнительная информация при расчете"""

        if not reports:
            text = 'Нет Записей'
        elif profit < 0:
            text = 'Ваш доход ушел за границу нуля.\nВам срочно нужен дополнительный заработок!'
        elif profit == 0:
            text = 'От зарплаты до зарплаты?'
        elif 0 < profit < 300:
            text = 'Пока что все под контролем.\nТак держать!'
        else:
            text = f'Все под контролем.\nПримерно допустимая сумма затрат {profit - 300} BYN!'
        return text

    @staticmethod
    def full_info_of_reports(currency):
        """Подробная информация расходов"""

        reports = db.full_info_of_reports_for_cost(currency)
        info_dict = {'продукты': 0, 'транспорт': 0, 'медицина': 0, 'связь': 0,
                     'хобби': 0, 'дом': 0, 'копилка': 0, 'другое': 0}

        for report in reports:
            if report[0] == "---------":
                info_dict["другое"] -= report[1]
            else:
                info_dict[report[0]] -= report[1]

        dialog_full_information = MDDialog(
            title="Подробная информация",
            text=f"  Продукты:        {info_dict['продукты']} {currency}\n\n"
                 f"  Транспорт:       {info_dict['транспорт']} {currency}\n\n"
                 f"  Медицина:       {info_dict['медицина']} {currency}\n\n"
                 f"  Связь:               {info_dict['связь']} {currency}\n\n"
                 f"  Хобби:               {info_dict['хобби']} {currency}\n\n"
                 f"  Дом:                  {info_dict['дом']} {currency}\n\n"
                 f"  Копилка:          {info_dict['копилка']} {currency}\n\n"
                 f"  Другое:             {info_dict['другое']} {currency}"
        )
        dialog_full_information.open()


class ExchangeNavigationItem(MDBoxLayout):
    """Вкладка курса валют"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not db.records_output_from_exchange_db():
            data = self.get_api()
            if data:
                db.insert_data_in_exchange_db(data)

    @staticmethod
    def error_with_internet():
        """Ошибка при отсутствии интернета"""

        snacbar = ValidateData().snackbar
        snacbar.text = "Требуется подключение к интернету!"
        snacbar.open()

    def get_api(self, change_course=False):
        """Получение API курса"""

        try:
            course_api = requests.get(url="https://cdn.cur.su/api/cbr.json").json()["rates"]
        except requests.exceptions.ConnectionError:
            if not change_course:
                self.error_with_internet()
        else:
            request_db = db.show_currency()
            currency = request_db[1] if request_db else "BYN"
            if currency == "BYN":
                byn_eur_in = round(course_api["BYN"] / course_api["EUR"], 4)
                byn_rub_in = round(course_api["BYN"] / course_api["RUB"] * 100, 4)
                data = [
                    ("USD", round(course_api["BYN"], 4), round(course_api["BYN"] + 0.1, 4)),
                    ("EUR", byn_eur_in, byn_eur_in + 0.1),
                    ("RUB", byn_rub_in - 0.9, byn_rub_in)
                ]
            elif currency == "RUB":
                rub_eur_in = round(course_api["RUB"] / course_api["EUR"], 4)
                rub_byn_in = round(course_api["RUB"] / course_api["BYN"], 4)
                data = [
                    ("USD", course_api["RUB"], course_api["RUB"] + 1.2),
                    ("EUR", rub_eur_in, rub_eur_in + 1.2),
                    ("BYN", rub_byn_in - 2.3, rub_byn_in)
                ]
            else:
                usd_byn_in = round(course_api["USD"] / course_api["BYN"], 4)
                usd_eur_in = round(course_api["USD"] / course_api["EUR"], 4)
                usd_rub_in = round(course_api["USD"] / course_api["RUB"] * 100, 4)
                data = [
                    ("BYN", usd_byn_in - 0.03, usd_byn_in),
                    ("EUR", usd_eur_in, usd_eur_in + 0.02),
                    ("RUB", usd_rub_in, usd_rub_in + 0.025)
                ]
            return data

    def set_default_values(self):
        """Установка значений по умолчанию"""

        courses = db.records_output_from_exchange_db()
        if courses:
            self.ids.currency_1_1.text = courses[0][1]
            self.ids.currency_1_2.text = courses[0][2]
            self.ids.currency_1_3.text = courses[0][3]

            self.ids.currency_2_1.text = courses[1][1]
            self.ids.currency_2_2.text = courses[1][2]
            self.ids.currency_2_3.text = courses[1][3]

            self.ids.currency_3_1.text = courses[2][1]
            self.ids.currency_3_2.text = courses[2][2]
            self.ids.currency_3_3.text = courses[2][3]
            self.ids.update_time.text = f"Обновлено {courses[0][4]}"

    def set_course_api(self, change_course=False):
        """Обновление курса валют"""

        data = self.get_api(change_course)
        if data:
            db.update_data_in_exchange_db(data=data)
            self.set_default_values()


class CostControlApp(MDApp):
    """Основное приложение"""

    def build(self):
        return MainWindow()
