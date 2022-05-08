from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivymd.uix.button import MDFloatingActionButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.textfield import MDTextField

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


class BoxSelectItemEditReport(MDBoxLayout):
    def __init__(self, name, value, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.value = value
        self.default_values()

    def default_values(self):
        self.ids.drop_item_category.set_item(self.value)
        self.ids.drop_item_costs.set_item("hi")

    def drop_down_category_menu(self):
        category = ('---------', 'продукты', 'транспорт', 'связь', 'работа', 'хобби', 'дом', 'копилка')
        menu_items = [{"text": item, "viewclass": "OneLineListItem",
                       "on_release": lambda x=item: self.set_item_category(x)} for item in category]
        self.menu = DropDownMenuReportsBox(caller=self.ids.drop_item_category, items=menu_items)
        self.menu.open()

    def drop_down_costs_menu(self):
        costs = ('Расход', 'Доход')
        menu_items = [{"text": item, "viewclass": "OneLineListItem",
                       "on_release": lambda x=item: self.set_item_costs(x)} for item in costs]
        self.menu = DropDownMenuReportsBox(caller=self.ids.drop_item_category, items=menu_items)
        self.menu.open()

    def set_item_category(self, item):
        self.ids.drop_item_category.set_item(item)
        self.menu.dismiss()

    def set_item_costs(self, item):
        self.ids.drop_item_costs.set_item(item)
        self.menu.dismiss()


class BoxItemEditReport(MDBoxLayout):
    def __init__(self, name, value, **kwargs):
        super().__init__(**kwargs)
        self.required = True
        self.name = name
        self.value = value
        self.add_box_item()

    def add_box_item(self):
        self.add_widget(MDLabel(text=self.name))
        self.add_widget(MDTextField(text=self.value))


class ClassEditReport(MDBoxLayout):
    def __init__(self, db, report_id, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.report_id = report_id
        self.box_widget()

    def box_widget(self):
        report = self.db.connection.query(CostControl).filter_by(id=self.report_id)
        for item in report:
            self.add_widget(BoxItemEditReport(name='Description', value=item.description))
            self.add_widget(BoxSelectItemEditReport(name='Category', value=item.category))
            self.add_widget(BoxItemEditReport(name='Price', value=str(item.price)))
            self.add_widget(Widget())
            self.add_widget(MDFloatingActionButton(icon="plus"))


class MainNavigationItem(ThreeLineAvatarIconListItem):
    def __init__(self, report_id, db, **kwargs):
        super(MainNavigationItem, self).__init__(**kwargs)
        self.db = db
        self.report_id = report_id

    def show_menu(self):
        items = [{"text": "Show", "viewclass": "OneLineListItem", "on_release": lambda: self.show_report()},
                 {"text": "Edit", "viewclass": "OneLineListItem", "on_release": lambda: self.edit_report()},
                 {"text": "Remove", "viewclass": "OneLineListItem", "on_release": lambda: self.delete_report()}
                 ]
        self.menu = DropdownMenuFunctionsOfReport(caller=self.ids.button, items=items)
        self.menu.open()

    def show_report(self):  # Применить Item или content_cls
        self.menu.dismiss()
        report = self.db.connection.query(CostControl).filter_by(id=self.report_id)
        for item in report:
            self.dialog = MDDialog(
                title=12 * " " + 'All information',
                text=f"Description:       {item.description}\n\n"
                     f"Category:           {item.category}\n\n"
                     f"Cost:                   {item.costs}\n\n"
                     f"Price:                  {item.price}\n\n"
                     f"Date:                   {item.date}"
            )
        self.dialog.open()

    def edit_report(self):
        self.menu.dismiss()
        dialog = MDDialog(
            title=18 * " " + "Edit report",
            type="custom",
            content_cls=ClassEditReport(self.db, self.report_id)
        )
        dialog.open()

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
        result = self.db.connection.query(CostControl).all()
        self.show_results(result)

    def searching_results(self, query):
        query = f'%{query}%'
        result = self.db.connection.query(CostControl).filter(CostControl.description.ilike(query)).all()
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
