from kivy.core.window import Window
from kivymd.uix.button import MDFlatButton
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
        self.report = db.retrieve(report_id)
        self.default_values()

    def default_values(self):
        self.ids.changed_description.set_text(instance=None, text=self.report.description)
        self.ids.drop_item_category.set_item(self.report.category)
        self.ids.drop_item_costs.set_item(self.report.costs)
        self.ids.changed_price.set_text(instance=None, text=str(self.report.price))

    def apply_change(self, description, category, cost, price):
        if ValidateData().validate_data(description, price):
            db.update(self.report, description, category, cost, price)
            Snackbar(text=25 * " " + f"Record {self.report.id} updated!", font_size=18).open()
            app = MDApp.get_running_app()
            app.root.ids.main_nav.all_reports()


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


class CostControlApp(MDApp):

    @staticmethod
    def clear_db():
        menu = MDDialog(title=9 * " " + "Удалить все записи?",
                        text="Это действие безвозвартно удалит все записи!",
                        radius=[20, 20, 20, 20])
        menu.buttons = [
            ButtonToDeleteAllReports(text="OK", instance=menu),
            ButtonToDeleteAllReports(text="Cancel", instance=menu)
        ]
        menu.create_buttons()
        menu.ids.root_button_box.height = 40
        menu.open()

    def build(self):
        return MainWindow()


if __name__ == '__main__':
    db = DataBase()
    print("подумать над методом dismiss")
    CostControlApp().run()
