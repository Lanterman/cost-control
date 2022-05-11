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
        self.report = db.connection.query(CostControl).get(report_id)
        self.default_values()

    def default_values(self):
        self.ids.changed_description.set_text(instance=None, text=self.report.description)
        self.ids.drop_item_category.set_item(self.report.category)
        self.ids.drop_item_costs.set_item(self.report.costs)
        self.ids.changed_price.set_text(instance=None, text=str(self.report.price))

    def apply_change(self, description, category, cost, price):
        db.apply_change(self.report, description, category, cost, price)
        Snackbar(text=25 * " " + f"Record {self.report.id} updated!", font_size=18).open()
        app = MDApp.get_running_app()
        app.all_reports()


class RecordWidget(ThreeLineAvatarIconListItem):
    def __init__(self, instance, **kwargs):
        super(RecordWidget, self).__init__(**kwargs)
        self.instance = instance

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
        dialog_edit_report = MDDialog(
            title=18 * " " + "Edit report",
            type="custom",
            content_cls=BoxItemEditReport(report_id=self.instance.id),
        )
        dialog_edit_report.open()

    def delete_report(self):
        db.connection.query(CostControl).filter_by(id=self.instance.id).delete()
        self.parent.remove_widget(self)
        self.menu.dismiss()
        db.connection.commit()


class MainNavigationItem(MDBoxLayout):

    @staticmethod
    def searching_results(query):
        query = f'%{query}%'
        result = db.connection.query(CostControl).filter(
            CostControl.description.ilike(query)).order_by(desc(CostControl.date)).all()
        app = MDApp.get_running_app()
        app.show_results(result)


class AddNavigationItem(AbstractClassForDropDownMenu):

    @staticmethod
    def insert_data(description, category, cost, price):
        db.insert_data(description, category, cost, price)
        app = MDApp.get_running_app()
        screen_manager = app.root.ids.bottom_nav
        app.all_reports()
        screen_manager.switch_tab("screen main")


class CostControlApp(MDApp):
    def __init__(self, **kwargs):
        super(CostControlApp, self).__init__(**kwargs)

    def all_reports(self):
        result = db.connection.query(CostControl).order_by(desc(CostControl.date)).all()
        self.show_results(result)

    @staticmethod
    def show_results(query):
        app = MDApp.get_running_app()
        result_list_widget = app.root.ids.show_result
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

    def build(self):
        return MainWindow()


if __name__ == '__main__':
    db = DataBase()
    CostControlApp().run()
