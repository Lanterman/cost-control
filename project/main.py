from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.list import IRightBody, TwoLineAvatarIconListItem, ThreeLineAvatarIconListItem
from kivymd.uix.menu import MDDropdownMenu

from project.database import DataBase, CostControl


class MainWindow(MDBoxLayout):
    pass


class RightButton(IRightBody, MDIconButton):
    pass


class SearchResultItem(ThreeLineAvatarIconListItem):
    def __init__(self, report_id, db, **kwargs):
        super(SearchResultItem, self).__init__(**kwargs)
        self.db = db
        self.report_id = report_id

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
        result_list_widget = app.root.ids.all_report
        result_list_widget.clear_widgets()
        for report in result:
            result_list_widget.add_widget(
                SearchResultItem(text=f'{report.description}',
                                 secondary_text=f'{report.category} {report.costs} {report.price}BYN',
                                 report_id=report.id, db=db, tertiary_text=f'{report.date}')
            )

    def searching_results(self, query):
        query = f'%{query}%'
        result = self.db.connection.query(CostControl).filter(CostControl.description.ilike(query))
        app = MDApp.get_running_app()
        result_list_widget = app.root.ids.search_result
        result_list_widget.clear_widgets()
        for report in result:
            result_list_widget.add_widget(
                SearchResultItem(text=f'{report.description} {report.date}', secondary_text='tel',
                                 report_id=report.id, db=db)
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
