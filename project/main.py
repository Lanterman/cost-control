from kivy.core.window import Window
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu

from project.database import DataBase, CostControl
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.list import IRightBody, ThreeLineAvatarIconListItem

Window.size = (370, 720)


class MainWindow(MDBoxLayout):
    pass


class RightButton(IRightBody, MDIconButton):
    pass


class SearchResultItem(ThreeLineAvatarIconListItem):
    def __init__(self, report_id, db, **kwargs):
        super(SearchResultItem, self).__init__(**kwargs)
        self.db = db
        self.report_id = report_id
        self.app = MDApp.get_running_app()
        menu_items = [
            {
                "text": f"Item {i}",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"Item {i}": self.menu_callback(x),
            } for i in range(5)
        ]
        self.menu = MDDropdownMenu(

            items=menu_items,
            width_mult=4
        )

    def menu_callback(self, text_item):
        print(text_item)

    def delete_report(self):
        self.db.connection.query(CostControl).filter_by(id=self.report_id).delete()
        self.parent.remove_widget(self)
        self.db.connection.commit()


class CostControlApp(MDApp):
    def __init__(self, db, **kwargs):
        super(CostControlApp, self).__init__(**kwargs)
        self.db = db

    def all_reports(self):
        result = self.db.connection.query(CostControl).all()
        app = MDApp.get_running_app()
        result_list_widget = app.root.ids.show_result
        result_list_widget.clear_widgets()
        if result:
            for report in result:
                space = 27 - len(report.costs) - len(str(report.price))
                result_list_widget.add_widget(
                    SearchResultItem(text=f'{report.description}',
                                     secondary_text=report.costs + space * " " + str(report.price) + ' BYN',
                                     report_id=report.id, db=db, tertiary_text=f'{report.date}')
                )
        else:
            result_list_widget.add_widget(MDLabel(text="Нет записей", halign='center'))

    def searching_results(self, query):
        query = f'%{query}%'
        result = self.db.connection.query(CostControl).filter(CostControl.description.ilike(query))
        app = MDApp.get_running_app()
        result_list_widget = app.root.ids.show_result
        result_list_widget.clear_widgets()
        for report in result:
            space = 27 - len(report.costs) - len(str(report.price))
            result_list_widget.add_widget(
                SearchResultItem(text=f'{report.description}',
                                 secondary_text=report.costs + space * " " + str(report.price) + ' BYN',
                                 report_id=report.id, db=db, tertiary_text=f'{report.date}')
            )

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
1