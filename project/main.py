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

Window.size = (370, 720)


class MainWindow(MDBoxLayout):
    pass


class DropdownMenuFunctionsOfReport(MDDropdownMenu):
    pass


class DropDownMenuReportsBox(MDDropdownMenu):
    pass


class IfNoRecords(MDLabel):
    pass


class CostDataLabel(MDLabel):
    font_size = 18


class ButtonToApplyChangesToReport(MDRaisedButton):
    def __init__(self, obj_dialog, box_item_edit=None, obj_report=None, **kwargs):
        super().__init__(**kwargs)
        self.font_size = 16

        self.app = MDApp.get_running_app()
        self.obj_dialog = obj_dialog
        self.box_item_edit = box_item_edit
        self.obj_report = obj_report

    def apply_change(self, description, category, cost, price):
        if ValidateData().validate_data(description, price):
            db.update(self.obj_report, description, category, cost, price)
            Snackbar(text=25 * " " + f"Record {self.obj_report.id} updated!", font_size=18,
                     snackbar_y=660, snackbar_animation_dir="Top").open()

    def on_press(self):
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
    def __init__(self, instance, **kwargs):
        super().__init__(**kwargs)
        self.font_size = 16
        self.instance = instance
        self.app = MDApp.get_running_app()

    def on_press(self):
        if self.text == "OK":
            db.delete_all_reports()
            screen_manager = self.app.root.ids.bottom_nav
            screen_manager.switch_tab("screen main")
        self.instance.dismiss()


class AbstractClassForDropDownMenu(MDBoxLayout):

    def drop_down_category_menu(self):
        category = ('---------', 'продукты', 'транспорт', 'связь', 'работа', 'хобби', 'дом', 'копилка')
        menu_items = [{"text": item, "viewclass": "OneLineListItem",
                       "on_release": lambda item=item: self.set_item(item)} for item in category]
        self.menu = DropDownMenuReportsBox(caller=self.ids.drop_item_category, items=menu_items)
        self.menu.open()

    def drop_down_costs_menu(self):
        costs = ('Расход', 'Доход')
        menu_items = [{"text": item, "viewclass": "OneLineListItem",
                       "on_release": lambda item=item: self.set_item(item)} for item in costs]
        self.menu = DropDownMenuReportsBox(caller=self.ids.drop_item_costs, items=menu_items, max_height=98)
        self.menu.open()

    def set_item(self, item):
        if item in ('Расход', 'Доход'):
            self.ids.drop_item_costs.set_item(item)
        else:
            self.ids.drop_item_category.set_item(item)
        self.menu.dismiss()


class BoxItemEditReport(AbstractClassForDropDownMenu):

    def __init__(self, report_id, **kwargs):
        super().__init__(**kwargs)
        self.report = db.retrieve(report_id)
        self.default_values()

    def default_values(self):
        self.ids.changed_description.set_text(instance=None, text=self.report.description)
        self.ids.drop_item_category.set_item(self.report.category)
        self.ids.drop_item_costs.set_item(self.report.costs)
        self.ids.changed_price.set_text(instance=None, text=str(self.report.price))


class RecordWidget(ThreeLineAvatarIconListItem):

    def __init__(self, instance, **kwargs):
        super(RecordWidget, self).__init__(**kwargs)
        self.instance = instance
        if self.instance.costs == "Расход":
            self.ids.md_icon.icon = "minus"
        else:
            self.ids.md_icon.icon = "plus"

    def show_menu(self):
        items = [{"text": "Show", "viewclass": "OneLineListItem", "on_release": lambda: self.show_report()},
                 {"text": "Edit", "viewclass": "OneLineListItem", "on_release": lambda: self.edit_report()},
                 {"text": "Remove", "viewclass": "OneLineListItem", "on_release": lambda: self.delete_report()}
                 ]
        self.menu = DropdownMenuFunctionsOfReport(caller=self.ids.button, items=items)
        self.menu.open()

    def show_report(self):
        self.menu.dismiss()
        dialog_show_report = MDDialog(
            title=12 * " " + 'All information',
            text=f"Description:       {self.instance.description}\n\n"
                 f"Category:           {self.instance.category}\n\n"
                 f"Cost:                   {self.instance.costs}\n\n"
                 f"Price:                  {self.instance.price} BYN\n\n"
                 f"Date:                   {self.instance.date}"
        )
        dialog_show_report.open()

    def edit_report(self):
        self.menu.dismiss()
        box_item_edit = BoxItemEditReport(report_id=self.instance.id)
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
        db.delete(self.instance.id)
        self.parent.remove_widget(self)
        self.menu.dismiss()


class MainNavigationItem(MDBoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()

    def searching_results(self, query):
        query = f'%{query}%'
        result = db.list(query)
        self.show_results(result)

    def all_reports(self):
        result = db.list()
        self.show_results(result)

    def show_results(self, query):
        result_list_widget = self.app.root.ids.show_result
        result_list_widget.clear_widgets()
        if query:
            for report in query:
                space = 27 - len(report.costs) - len(str(report.price))
                result_list_widget.add_widget(
                    RecordWidget(text=f'{report.description}',
                                 secondary_text=report.costs + space * " " + str(report.price) + ' BYN',
                                 instance=report, tertiary_text=f'{report.date}')
                )
        else:
            result_list_widget.add_widget(IfNoRecords())


class AddNavigationItem(AbstractClassForDropDownMenu):

    def insert_data(self, description, category, cost, price):
        if ValidateData().validate_data(description, price):
            db.insert_data(description, category, cost, price)
            app = MDApp.get_running_app()
            screen_manager = app.root.ids.bottom_nav
            self.clearing_text_widgets()
            screen_manager.switch_tab("screen main")

    def clearing_text_widgets(self):
        self.ids.add_description.set_text(instance=None, text="")
        self.ids.drop_item_category.set_item("---------")
        self.ids.drop_item_costs.set_item("Расход")
        self.ids.add_price.set_text(instance=None, text="0")


class CostNavigationItem(MDBoxLayout):

    def set_values(self):
        reports = db.cost_data()
        profit, income, expenditure = self.calculate_price(reports)
        self.ids.set_profit.text = str(profit)
        self.ids.set_income.text = str(income)
        self.ids.set_expenditure.text = str(expenditure)
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
    def graphic_design():
        graphic_dialog = MDDialog()
        graphic_dialog.open()


class CostControlApp(MDApp):

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


if __name__ == '__main__':
    db = DataBase()
    CostControlApp().run()
