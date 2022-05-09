from datetime import datetime

from kivy.core.window import Window
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.snackbar import Snackbar
from sqlalchemy import desc

from project.database import DataBase, CostControl
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import ThreeLineAvatarIconListItem

Window.size = (370, 720)


class MainWindow(MDBoxLayout):
    pass


class DropdownMenuFunctionsOfReport(MDDropdownMenu):
    pass


class IfNoRecords(MDLabel):
    pass


class DropDownMenuReportsBox(MDDropdownMenu):
    pass


class BoxItemEditReport(MDBoxLayout):
    def __init__(self, db, report_id, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.report = self.db.connection.query(CostControl).get(report_id)
        self.default_values()

    def default_values(self):
        self.ids.changed_description.set_text(instance=None, text=self.report.description)
        self.ids.drop_item_category.set_item(self.report.category)
        self.ids.drop_item_costs.set_item(self.report.costs)
        self.ids.changed_price.set_text(instance=None, text=str(self.report.price))

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

    def apply_change(self, description, category, cost, price):
        self.report.description = description
        self.report.category = category
        self.report.costs = cost
        self.report.price = price
        self.report.date = str(datetime.now())[:19]
        self.db.connection.add(self.report)
        self.db.connection.commit()
        Snackbar(text=25 * " " + f"Record {self.report.id} updated!", font_size=18).open()
        app = MDApp.get_running_app()
        app.all_reports()


class MainNavigationItem(ThreeLineAvatarIconListItem):
    def __init__(self, report_id, db, **kwargs):
        super(MainNavigationItem, self).__init__(**kwargs)
        self.db = db
        self.report_id = report_id
        self.report = self.db.connection.query(CostControl).get(self.report_id)

    def show_menu(self):
        items = [{"text": "Show", "viewclass": "OneLineListItem", "on_release": lambda: self.show_report()},
                 {"text": "Edit", "viewclass": "OneLineListItem", "on_release": lambda: self.edit_report()},
                 {"text": "Remove", "viewclass": "OneLineListItem", "on_release": lambda: self.delete_report()}
                 ]
        self.menu = DropdownMenuFunctionsOfReport(caller=self.ids.button, items=items)
        self.menu.open()

    def show_report(self):  # Применить Item или content_cls
        self.menu.dismiss()
        dialog_show_report = MDDialog(
            title=12 * " " + 'All information',
            text=f"Description:       {self.report.description}\n\n"
                 f"Category:           {self.report.category}\n\n"
                 f"Cost:                   {self.report.costs}\n\n"
                 f"Price:                  {self.report.price}\n\n"
                 f"Date:                   {self.report.date}"
        )
        dialog_show_report.open()

    def edit_report(self):
        self.menu.dismiss()
        dialog_edit_report = MDDialog(
            title=18 * " " + "Edit report",
            type="custom",
            content_cls=BoxItemEditReport(db=self.db, report_id=self.report.id),
        )
        dialog_edit_report.open()

    def delete_report(self):
        self.db.connection.query(CostControl).filter_by(id=self.report_id).delete()
        self.parent.remove_widget(self)
        self.menu.dismiss()
        # self.db.connection.commit()


class CostControlApp(MDApp):
    def __init__(self, db, **kwargs):
        super(CostControlApp, self).__init__(**kwargs)
        self.db = db

    def all_reports(self):
        result = self.db.connection.query(CostControl).order_by(desc(CostControl.date)).all()
        self.show_results(result)

    def searching_results(self, query):
        query = f'%{query}%'
        result = self.db.connection.query(CostControl).filter(
            CostControl.description.ilike(query)).order_by(desc(CostControl.date)).all()
        self.show_results(result)

    def show_results(self, query):
        app = MDApp.get_running_app()
        result_list_widget = app.root.ids.show_result
        result_list_widget.clear_widgets()
        if query:
            for report in query:
                space = 27 - len(report.costs) - len(str(report.price))
                result_list_widget.add_widget(
                    MainNavigationItem(text=f'{report.description}',
                                       secondary_text=report.costs + space * " " + str(report.price) + ' BYN',
                                       report_id=report.id, db=db, tertiary_text=f'{report.date}')
                )
        else:
            result_list_widget.add_widget(IfNoRecords())

    def insert_data(self, description, category, cost, price):
        self.db.insert_data(description, category, cost, price)

        app = MDApp.get_running_app()
        screen_manager = app.root.ids.bottom_nav
        self.all_reports()
        screen_manager.switch_tab("screen main")

    def build(self):
        return MainWindow()


if __name__ == '__main__':
    db = DataBase()
    CostControlApp(db).run()
