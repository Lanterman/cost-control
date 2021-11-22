import tkinter as tk
import matplotlib as mpl
import matplotlib.pyplot as plt
from datetime import datetime
from tkinter import ttk, messagebox

from database import DataBase, ValidateData


class Main(tk.Frame):
    """Главное окно"""

    def __init__(self, window):
        super().__init__(window)
        self.init_main()
        self.database = database
        self.view_records()

    def init_main(self):
        """Инициализация главного окна"""
        toolbar = tk.Frame(bg='#d7d8e0', bd=10)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # primary actions
        self.add_img = tk.PhotoImage(file='img/add.gif')
        btn_open_dialog = tk.Button(master=toolbar, text='Add', command=self.open_the_dialog, bg='#d7d8e0',
                                    bd=1, compound=tk.TOP, image=self.add_img, width=55, height=55)
        btn_open_dialog.pack(side=tk.LEFT)

        self.search_img = tk.PhotoImage(file='img/search.gif')
        btn_search = tk.Button(master=toolbar, text='Search', bg='#d7d8e0', bd=1, image=self.search_img,
                               compound=tk.TOP, command=self.open_the_search, width=55, height=55)
        btn_search.pack(side=tk.LEFT)

        self.refresh_img = tk.PhotoImage(file='img/refresh.gif')
        btn_refresh = tk.Button(master=toolbar, text='Refresh', bg='#d7d8e0', bd=1, image=self.refresh_img,
                                compound=tk.TOP, command=self.view_records, width=55, height=55)
        btn_refresh.pack(side=tk.LEFT)

        self.delete_all_img = tk.PhotoImage(file='img/delete.gif')
        btn_delete_all = tk.Button(master=toolbar, text='Clean', bg='#d7d8e0', bd=1, width=55, height=55,
                                   image=self.delete_all_img, compound=tk.TOP, command=self.clean_the_mark)
        btn_delete_all.pack(side=tk.LEFT)

        # additional actions
        self.delete_img = tk.PhotoImage(file='img/delete.gif')
        btn_delete = tk.Button(master=toolbar, text='Delete', bg='#d7d8e0', bd=1, image=self.delete_img,
                               compound=tk.TOP, command=self.delete_records, width=55, height=55)
        btn_delete.pack(side=tk.RIGHT)

        self.update_img = tk.PhotoImage(file='img/update.gif')
        btn_edit_dialog = tk.Button(master=toolbar, text='Edit', bg='#d7d8e0', bd=1, image=self.update_img,
                                    compound=tk.TOP, command=self.open_the_update, width=55, height=55)
        btn_edit_dialog.pack(side=tk.RIGHT)

        self.calculate_img = tk.PhotoImage(file='img/dollar.gif')
        btn_calculate = tk.Button(master=toolbar, text='Calculate', bg='#d7d8e0', bd=1, image=self.calculate_img,
                                  compound=tk.TOP, command=self.open_the_calculate, width=55, height=55)
        btn_calculate.pack(side=tk.RIGHT)

        self.tree = ttk.Treeview(self, columns=('ID', 'description', 'category', 'costs', 'price', 'date'), height=15,
                                 show='headings')

        self.tree.column('ID', width=25, anchor=tk.CENTER)
        self.tree.column('description', width=250, anchor=tk.CENTER)
        self.tree.column('category', width=135, anchor=tk.CENTER)
        self.tree.column('costs', width=110, anchor=tk.CENTER)
        self.tree.column('price', width=100, anchor=tk.CENTER)
        self.tree.column('date', width=150, anchor=tk.CENTER)

        self.tree.heading('ID', text='ID')
        self.tree.heading('description', text='Описание')
        self.tree.heading('category', text='Категория')
        self.tree.heading('costs', text='Действие')
        self.tree.heading('price', text='Сумма')
        self.tree.heading('date', text='дата')

        self.tree.pack(side=tk.LEFT)

        scroll = tk.Scrollbar(self, command=self.tree.yview)
        scroll.pack(side=tk.LEFT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scroll.set)

    def clean_the_mark(self):
        """Удаление всех записей"""
        if messagebox.askokcancel('Подтверждение действия', 'Вы действительно хотите удалить все записи?'):
            self.database.cursor.execute('''DELETE FROM control''')
            self.database.connection.commit()
            self.view_records()

    def delete_records(self):
        """Удаление выбранных записей"""
        if self.tree.selection():
            for selection_item in self.tree.selection():
                self.database.cursor.execute('''DELETE FROM control WHERE id=?''',
                                             (self.tree.set(selection_item, '#1'),))
        else:
            messagebox.showwarning("Ошибка", "Выберите запись(-и) для удаления!")
        self.database.connection.commit()
        self.view_records()

    def view_records(self):
        """Вывод всех записей на главном окне"""
        self.database.cursor.execute("""SELECT * FROM control""")
        [self.tree.delete(i) for i in self.tree.get_children()]
        [self.tree.insert('', 'end', values=row) for row in self.database.cursor.fetchall()]

    def open_the_dialog(self):
        """Вызов окна добавления записей"""
        Child()

    def open_the_update(self):
        """Вызов окна изменения записей"""
        Update()

    def open_the_search(self):
        """Вызов окна поиска записей"""
        Search()

    def open_the_calculate(self):
        """Вызов окна расчета"""
        Calculate()


class Child(tk.Toplevel):
    """Окно добавления записей"""

    def __init__(self):
        super().__init__(window)
        self.view = app
        self.validate = validate
        self.init_the_child()

    def init_the_child(self):
        """Инициализация окна добавления"""
        self.title('Добавить расходы/доходы')
        self.geometry('400x230+400+300')
        self.resizable(False, False)

        lbl_description = tk.Label(self, text='Описание')
        lbl_description.place(x=50, y=40)
        lbl_description = tk.Label(self, text='Категория')
        lbl_description.place(x=50, y=70)
        lbl_costs = tk.Label(self, text='Действие')
        lbl_costs.place(x=50, y=100)
        lbl_price = tk.Label(self, text='Сумма')
        lbl_price.place(x=50, y=130)

        self.entry_description = ttk.Entry(self)
        self.entry_description.place(x=200, y=40)

        self.category = ttk.Combobox(self, values=['---------', 'покупки', 'транспорт'])
        self.category.current(0)
        self.category.place(x=200, y=70)

        self.actions = ttk.Combobox(self, values=['---------', 'Доход', 'Расход'])
        self.actions.current(0)
        self.actions.place(x=200, y=100)

        self.entry_price = ttk.Entry(self)
        self.entry_price.insert(0, 0)
        self.entry_price.place(x=200, y=130)

        self.btn_save_and_continue = ttk.Button(self, text='Сохранить и продолжить', command=self.add_the_mark)
        self.btn_save_and_continue.place(x=57, y=185)

        self.btn_add = ttk.Button(self, text='Добавить')
        self.btn_add.place(x=210, y=185)
        self.btn_add.bind('<Button-1>', lambda event: self.add_the_mark())
        self.btn_add.bind('<Button-1>', lambda event: self.destroy(), add='+')

        btn_cancel = ttk.Button(self, text='Отмена', command=self.destroy)
        btn_cancel.place(x=290, y=185)

        self.grab_set()
        self.focus_get()

    def add_the_mark(self):
        """Логика кнопок добавления"""
        self.records(self.entry_description.get(), self.category.get(), self.actions.get(), self.entry_price.get())

    def records(self, description, category, costs, price):
        """Добавление записи"""
        if self.validate.validate_data(category, costs, price):
            price = self.validate.control_of_filling_the_price(costs, price)
            self.view.database.insert_data(description, category, costs, price)
            self.view.view_records()


class Update(Child):
    """Окно редактирования записей"""

    def __init__(self):
        super().__init__()
        self.init_the_edit()
        self.database = database
        self.default_data()

    def init_the_edit(self):
        """Инициализация окна редактирования"""
        self.title('Редактировать')
        btn_edit = ttk.Button(self, text='Редактировать')
        btn_edit.place(x=195, y=185)
        btn_edit.bind('<Button-1>', lambda event: self.update_records(self.entry_description.get(),
                                                                      self.category.get(),
                                                                      self.actions.get(),
                                                                      self.entry_price.get()))
        btn_edit.bind('<Button-1>', lambda event: self.destroy(), add='+')

        self.btn_save_and_continue.destroy()
        self.btn_add.destroy()

    def update_records(self, description, category, costs, price):
        """Обновление записи"""
        if self.validate.validate_data(category, costs, price):
            price = self.validate.control_of_filling_the_price(costs, price)
            if costs == 'Доход':
                category = '---------'

            self.database.cursor.execute(
                """UPDATE control SET description=?, category=?, costs=?, price=?, date=? WHERE ID=?""",
                (description, category, costs, price, str(datetime.now())[:19],
                 self.view.tree.set(self.view.tree.selection(), '#1'),))
            self.database.connection.commit()
            self.view.view_records()

    def default_data(self):
        """Заполнение полей по умолчанию"""
        if len(self.view.tree.selection()) > 1:
            self.destroy()
            messagebox.showwarning("Ошибка", "За раз можно обновить 1 запись!")
        else:
            try:
                self.database.cursor.execute('''SELECT * FROM control WHERE id=?''',
                                             (self.view.tree.set(self.view.tree.selection()[0], '#1'),))
                row = self.database.cursor.fetchone()

                self.category.delete(0, tk.END)
                self.actions.delete(0, tk.END)
                self.entry_price.delete(0, tk.END)

                self.entry_description.insert(0, row[1])
                self.category.insert(0, row[2])
                self.actions.insert(0, row[3])
                self.entry_price.insert(0, row[4])

            except IndexError:
                self.destroy()
                messagebox.showwarning("Ошибка", "Выберите запись для изменения!")


class Search(tk.Toplevel):
    """Окно поиска записей"""

    def __init__(self):
        super().__init__()
        self.init_the_search()
        self.view = app

    def init_the_search(self):
        """Инициализация окна поиска"""
        self.title('Поиск')
        self.geometry('300x100+400+300')
        self.resizable(False, False)

        lbl_search = tk.Label(self, text='Поиск')
        lbl_search.place(x=50, y=20)

        entry_search = ttk.Entry(self)
        entry_search.place(x=105, y=20, width=150)

        btn_cancel = ttk.Button(self, text='Закрыть', command=self.destroy)
        btn_cancel.place(x=185, y=50)

        btn_search = ttk.Button(self, text='Поиск')
        btn_search.place(x=105, y=50)
        btn_search.bind('<Button-1>', lambda event: self.search_records(entry_search.get()))
        btn_search.bind('<Button-1>', lambda event: self.destroy(), add='+')

        self.grab_set()
        self.focus_get()

    def search_records(self, description):
        """Поиск записей"""
        description = ('%' + description + '%',)
        self.view.database.cursor.execute('''SELECT * FROM control WHERE description LIKE ?''', description)
        [self.view.tree.delete(i) for i in self.view.tree.get_children()]
        [self.view.tree.insert('', 'end', values=row) for row in self.view.database.cursor.fetchall()]


class Calculate(tk.Toplevel):
    """Окно расчета"""

    def __init__(self):
        super().__init__()
        self.database = database
        self.init_the_calculate()

    def init_the_calculate(self):
        """Инициализация окна расчета"""
        self.title('Расчет прибыли')
        self.geometry('300x270+400+300')
        self.resizable(False, False)

        response = self.calculate()
        text = self.description(response[0])

        lbl_search = tk.Label(self, text=f'Осталось: {response[0]} BYN', font=('Times', '16'), bg='#BAEFEB')
        lbl_search.place(x=50, y=20)

        lbl_search = tk.Label(self, text=f'Заработано: {response[1]} BYN', font=('Times', '13'))
        lbl_search.place(x=65, y=60)

        lbl_search = tk.Label(self, text=f'Потрачено: {response[2]} BYN', font=('Times', '13'))
        lbl_search.place(x=65, y=90)

        btb_graph = tk.Button(self, text='Гистограмма', font=('Times', '14'), command=self.matplotlib)
        btb_graph.place(x=90, y=130)

        lbl_search = tk.Label(self, text=text, font=('Times', '13'), wraplength=270)
        lbl_search.place(x=20, y=180)

        self.grab_set()
        self.focus_get()

    def calculate(self):
        """Расчет финансов"""
        self.database.cursor.execute("""SELECT costs, price FROM control""")
        response = self.database.cursor.fetchall()
        profit = round(sum([price for costs, price in response]), 2)
        income = round(sum([price for costs, price in response if costs == 'Доход']), 2)
        expenditure = round(sum([price for costs, price in response if costs == 'Расход']), 2)
        return [profit, income, expenditure]

    def description(self, response):
        """Дополнительная информация при расчете"""
        self.database.cursor.execute("""SELECT * FROM control""")
        mark = bool(self.database.cursor.fetchall())
        if not mark:
            text = 'Нет Записей'
        elif response < 0:
            text = 'Ваш доход ушел за границу нуля, вам срочно нужен дополнительный заработок!'
        elif not mark:
            text = 'Нет Записей'
        elif response == 0:
            text = 'От зарплаты до зарплаты ?'
        elif 0 < response < 300:
            text = 'Пока что все под контролем, так держать!'
        else:
            text = f'Все под контролем, можно сходить на шопинг. Примерно допустимая сумма затрат {response - 300} BYN!'
        return text

    def matplotlib(self):
        x = [1, 2, 3, 4]
        y = [5, 2, 0.5, 1]

        plt.plot(x, y)
        plt.show()


if __name__ == '__main__':
    window = tk.Tk()
    database = DataBase()
    validate = ValidateData()
    app = Main(window)
    app.pack()
    window.title('Cost control')
    window.geometry('800x430+300+200')
    window.resizable(False, False)
    tk.Label(text='Version 1.1').pack()
    app.mainloop()
