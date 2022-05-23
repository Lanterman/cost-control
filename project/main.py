from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.snackbar import Snackbar
from project.database import DataBase, ValidateData
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import ThreeLineAvatarIconListItem

from kivy.config import Config
Config.set('graphics', 'width', '370')
Config.set('graphics', 'height', '650')
Config.write()

db = DataBase()


class MainWindow(MDBoxLayout):
    """Основное окно"""


class DropdownMenuFunctionsOfReport(MDDropdownMenu):
    """Виджет меню кнопок для каждой записи"""


class DropDownMenuReportsBox(MDDropdownMenu):
    """Виджет меню выбора значения для поля"""


class IfNoRecords(MDLabel):
    """Установить метку, если нет записей"""


class CostDataLabel(MDLabel):
    """Метка вкладки расчетов"""

    font_size = 18


class FullInfoOfReportsLabel(MDLabel):
    """Метка вкладки расчетов"""

    font_size = 18
    theme_text_color = "Custom"
    text_color = (0.64, 0.64, 0.64, 1)


class ButtonToApplyChangesToReport(MDRaisedButton):
    """Кнопки модального окна изменения записи"""

    def __init__(self, obj_dialog, box_item_edit=None, obj_report=None, **kwargs):
        super().__init__(**kwargs)
        self.font_size = 16

        self.app = MDApp.get_running_app()
        self.obj_dialog = obj_dialog
        self.box_item_edit = box_item_edit
        self.obj_report = obj_report

    def apply_change(self, description, category, cost, price):
        """Обновить запись"""

        if ValidateData().validate_data(description, price):
            db.update(self.obj_report, description, category, cost, price)
            Snackbar(text=25 * " " + f"Record {self.obj_report[0]} updated!", font_size=18,
                     snackbar_y=660, snackbar_animation_dir="Top").open()

    def on_press(self):
        """Действие при нажатии на кнопку"""

        if self.box_item_edit:
            self.apply_change(
                self.box_item_edit.ids.changed_description.text,
                self.box_item_edit.ids.drop_item_category.ids.label_item.text,
                self.box_item_edit.ids.drop_item_costs.ids.label_item.text,
                self.box_item_edit.ids.changed_price.text
            )
            self.app.root.ids.main_nav.all_reports()
        self.obj_dialog.dismiss()


class ButtonToDeleteAllReports(MDFlatButton):
    """Кнопки модального окна удаления всех записей """

    def __init__(self, instance, **kwargs):
        super().__init__(**kwargs)
        self.font_size = 16
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

        category = ('---------', 'продукты', 'транспорт', 'медицина', 'связь', 'работа', 'хобби', 'дом', 'копилка')
        menu_items = [{"text": item, "viewclass": "OneLineListItem",
                       "on_release": lambda item=item: self.set_item(item)} for item in category]
        self.menu = DropDownMenuReportsBox(caller=self.ids.drop_item_category, items=menu_items)
        self.menu.open()

    def drop_down_costs_menu(self):
        """Выбор значения для типа записи"""

        costs = ('Расход', 'Доход')
        menu_items = [{"text": item, "viewclass": "OneLineListItem",
                       "on_release": lambda item=item: self.set_item(item)} for item in costs]
        self.menu = DropDownMenuReportsBox(caller=self.ids.drop_item_costs, items=menu_items, max_height=98)
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


class BoxItemFullInfoOfReports(MDBoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reports = db.full_info_of_reports_for_cost()
        self.info_dict = {'продукты': 0, 'транспорт': 0, 'медицина': 0, 'связь': 0,
                          'хобби': 0, 'дом': 0, 'копилка': 0, 'другое': 0}
        self.set_values()

    def set_values(self):
        """Установка значений"""

        for report in self.reports:
            if report[0] == "---------":
                self.info_dict["другое"] -= report[1]
            else:
                self.info_dict[report[0]] -= report[1]

        self.ids.per_product.text = str(self.info_dict["продукты"]) + " BYN"
        self.ids.per_transport.text = str(self.info_dict["транспорт"]) + " BYN"
        self.ids.per_medicine.text = str(self.info_dict["медицина"]) + " BYN"
        self.ids.per_phone.text = str(self.info_dict["связь"]) + " BYN"
        self.ids.per_hobby.text = str(self.info_dict["хобби"]) + " BYN"
        self.ids.per_home.text = str(self.info_dict["дом"]) + " BYN"
        self.ids.per_moneybox.text = str(self.info_dict["копилка"]) + " BYN"
        self.ids.per_other.text = str(self.info_dict["другое"]) + " BYN"


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

        items = [{"text": "Show", "viewclass": "OneLineListItem", "on_release": lambda: self.show_report()},
                 {"text": "Edit", "viewclass": "OneLineListItem", "on_release": lambda: self.edit_report()},
                 {"text": "Remove", "viewclass": "OneLineListItem", "on_release": lambda: self.delete_report()}
                 ]
        self.menu = DropdownMenuFunctionsOfReport(caller=self.ids.button, items=items)
        self.menu.open()

    def show_report(self):
        """Модальное окно показа полной информации записи"""

        self.menu.dismiss()
        dialog_show_report = MDDialog(
            title=12 * " " + 'All information',
            text=f"Description:       {self.instance[1]}\n\n"
                 f"Category:           {self.instance[2]}\n\n"
                 f"Cost:                   {self.instance[3]}\n\n"
                 f"Price:                  {self.instance[4]} BYN\n\n"
                 f"Date:                   {self.instance[5]}"
        )
        dialog_show_report.open()

    def edit_report(self):
        """Модальное окно обновление записи"""

        self.menu.dismiss()
        box_item_edit = BoxItemEditReport(report_id=self.instance[0])
        dialog_edit_report = MDDialog(title=18 * " " + "Edit report",
                                      type="custom",
                                      content_cls=box_item_edit)
        dialog_edit_report.buttons = [
            ButtonToApplyChangesToReport(text="Apply", obj_dialog=dialog_edit_report, box_item_edit=box_item_edit,
                                         obj_report=self.instance),
            ButtonToApplyChangesToReport(text="Cancel", obj_dialog=dialog_edit_report,
                                         text_color=(0.1, 0.1, 1, 1), md_bg_color=(0.86, 0.81, 0.81, 1))
        ]
        dialog_edit_report.create_buttons()
        dialog_edit_report.ids.root_button_box.height = 50
        dialog_edit_report.open()

    def delete_report(self):
        """Удалить запись"""

        db.delete(self.instance[0])
        self.parent.remove_widget(self)
        self.menu.dismiss()


class MainNavigationItem(MDBoxLayout):
    """Вкладка с записями"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()

    def searching_results(self, query):
        """Вывод записей по поиску"""

        query = f'%{query}%'
        result = db.list(query)
        self.show_results(result)

    def all_reports(self):
        """Вывод всех записей"""

        result = db.list()
        self.show_results(result)

    def show_results(self, query):
        """Логика вывода записей"""

        result_list_widget = self.app.root.ids.show_result
        result_list_widget.clear_widgets()
        if query:
            for report in query:
                space = 27 - len(report[3]) - len(str(report[4]))
                result_list_widget.add_widget(
                    RecordWidget(text=f'{report[1]}',
                                 secondary_text=report[3] + space * " " + str(report[4]) + ' BYN',
                                 instance=report, tertiary_text=f'{report[5]}')
                )
        else:
            result_list_widget.add_widget(IfNoRecords())


class AddNavigationItem(AbstractClassForDropDownMenu):

    def insert_data(self, description, category, cost, price):
        """Добавление записи в BD"""

        if ValidateData().validate_data(description, price):
            db.insert_data(description, category, cost, price)
            app = MDApp.get_running_app()
            screen_manager = app.root.ids.bottom_nav
            self.clearing_text_widgets()
            screen_manager.switch_tab("screen main")

    def clearing_text_widgets(self):
        """Очистка текста виджетов после добавления записи"""

        self.ids.add_description.set_text(instance=None, text="")
        self.ids.drop_item_category.set_item("---------")
        self.ids.drop_item_costs.set_item("Расход")
        self.ids.add_price.set_text(instance=None, text="0")


class CostNavigationItem(MDBoxLayout):

    def set_values(self):
        """Установка текстовых значений"""

        reports = db.cost_data()
        profit, income, expenditure = self.calculate_price(reports)
        self.ids.set_profit.text = str(profit) + " BYN"
        self.ids.set_income.text = str(income) + " BYN"
        self.ids.set_expenditure.text = str(expenditure) + " BYN"
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
    def full_info_of_reports():
        """Запуск гистограммы"""

        dialog_full_information = MDDialog(title=2 * " " + "Full information of reports",
                                           type="custom",
                                           content_cls=BoxItemFullInfoOfReports())
        dialog_full_information.open()


class CostControlApp(MDApp):
    """Основное приложение"""

    title = "Cost Control"

    @staticmethod
    def clear_db():
        delete_dialog = MDDialog(title=9 * " " + "Удалить все записи?",
                                 text="Это действие безвозвартно удалит все записи!",
                                 radius=[20, 20, 20, 20])
        delete_dialog.buttons = [
            ButtonToDeleteAllReports(text="OK", instance=delete_dialog),
            ButtonToDeleteAllReports(text="Cancel", instance=delete_dialog)
        ]
        delete_dialog.create_buttons()
        delete_dialog.ids.root_button_box.height = 40
        delete_dialog.open()

    def build(self):
        return MainWindow()
