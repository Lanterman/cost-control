import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox
import sqlite3

from database import DataBase


class Main(tk.Frame):
    def __init__(self, window):
        super().__init__(window)
        self.init_main()
        self.database = database
        self.view_records()

    def init_main(self):
        toolbar = tk.Frame(bg='#d7d8e0', bd=10)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # primary actions
        self.add_img = tk.PhotoImage(file='img/add.gif')
        btn_open_dialog = tk.Button(master=toolbar, text='Add', command=self.open_dialog, bg='#d7d8e0',
                                    bd=1, compound=tk.TOP, image=self.add_img, width=55, height=55)
        btn_open_dialog.pack(side=tk.LEFT)

        self.search_img = tk.PhotoImage(file='img/search.gif')
        btn_search = tk.Button(master=toolbar, text='Search', bg='#d7d8e0', bd=1, image=self.search_img,
                               compound=tk.TOP, command=self.open_search, width=55, height=55)
        btn_search.pack(side=tk.LEFT)

        self.refresh_img = tk.PhotoImage(file='img/refresh.gif')
        btn_refresh = tk.Button(master=toolbar, text='Refresh', bg='#d7d8e0', bd=1, image=self.refresh_img,
                                compound=tk.TOP, command=self.view_records, width=55, height=55)
        btn_refresh.pack(side=tk.LEFT)

        self.delete_all_img = tk.PhotoImage(file='img/delete.gif')
        btn_delete_all = tk.Button(master=toolbar, text='Clean', bg='#d7d8e0', bd=1, width=55, height=55,
                                   image=self.delete_all_img, compound=tk.TOP, command='')
        btn_delete_all.pack(side=tk.LEFT)

        # additional actions
        self.delete_img = tk.PhotoImage(file='img/delete.gif')
        btn_delete = tk.Button(master=toolbar, text='Delete', bg='#d7d8e0', bd=1, image=self.delete_img,
                               compound=tk.TOP, command=self.delete_records, width=55, height=55)
        btn_delete.pack(side=tk.RIGHT)

        self.update_img = tk.PhotoImage(file='img/update.gif')
        btn_edit_dialog = tk.Button(master=toolbar, text='Edit', bg='#d7d8e0', bd=1, image=self.update_img,
                                    compound=tk.TOP, command=self.open_update, width=55, height=55)
        btn_edit_dialog.pack(side=tk.RIGHT)

        self.calculate_img = tk.PhotoImage(file='img/dollar.gif')
        btn_delete = tk.Button(master=toolbar, text='Calculate', bg='#d7d8e0', bd=1, image=self.calculate_img,
                               compound=tk.TOP, command=self.delete_records, width=55, height=55)
        btn_delete.pack(side=tk.RIGHT)

        self.tree = ttk.Treeview(self, columns=('ID', 'description', 'costs', 'price', 'date'), height=15,
                                 show='headings')

        self.tree.column('ID', width=30, anchor=tk.CENTER)
        self.tree.column('description', width=240, anchor=tk.CENTER)
        self.tree.column('costs', width=120, anchor=tk.CENTER)
        self.tree.column('price', width=100, anchor=tk.CENTER)
        self.tree.column('date', width=150, anchor=tk.CENTER)

        self.tree.heading('ID', text='ID')
        self.tree.heading('description', text='Описание')
        self.tree.heading('costs', text='Действие')
        self.tree.heading('price', text='Сумма')
        self.tree.heading('date', text='дата')

        self.tree.pack(side=tk.LEFT)

        scroll = tk.Scrollbar(self, command=self.tree.yview)
        scroll.pack(side=tk.LEFT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scroll.set)

    def records(self, description, costs, price):
        if costs in ('Расход', 'Доход'):
            self.database.insert_data(description, costs, price)
            self.view_records()
        else:
            messagebox.showwarning("Ошибка заполнения!", f"Нет такого действия - '{costs}'!")
        try:
            float(price)
        except Exception:
            messagebox.showwarning("Ошибка заполнения!",
                                   f"Допустимы только числа(простые и десятичные) - '{price}'!\nP.S. Десятичные писать через точку! ")

    def update_records(self, description, costs, price):
        self.database.cursor.execute("""UPDATE control SET description=?, costs=?, price=?, date=? WHERE ID=?""",
                                     (description, costs, price, str(datetime.now())[:19],
                                      self.tree.set(self.tree.selection(), '#1')))
        self.database.connection.commit()
        self.view_records()

    def delete_records(self):
        if self.tree.selection():
            for selection_item in self.tree.selection():
                self.database.cursor.execute('''DELETE FROM control WHERE id=?''',
                                             (self.tree.set(selection_item, '#1'),))
        else:
            messagebox.showwarning("Ошибка", "Выберите запись(-и) для удаления!")
        self.database.connection.commit()
        self.view_records()

    def view_records(self):
        self.database.cursor.execute("""SELECT * FROM control""")
        [self.tree.delete(i) for i in self.tree.get_children()]
        [self.tree.insert('', 'end', values=row) for row in self.database.cursor.fetchall()]

    def search_records(self, description):
        description = ('%' + description + '%',)
        self.database.cursor.execute('''SELECT * FROM control WHERE description LIKE ?''', description)
        [self.tree.delete(i) for i in self.tree.get_children()]
        [self.tree.insert('', 'end', values=row) for  row in self.database.cursor.fetchall()]

    def open_dialog(self):
        Child()

    def open_update(self):
        Update()

    def open_search(self):
        Search()


class Child(tk.Toplevel):
    def __init__(self):
        super().__init__(window)
        self.view = app
        self.init_child()

    def add_a_mark(self):
        self.view.records(self.entry_description.get(), self.combobox.get(), self.entry_price.get())

    def init_child(self):
        self.title('Добавить расходы/доходы')
        self.geometry('400x200+400+300')
        self.resizable(False, False)

        lbl_description = tk.Label(self, text='Описание')
        lbl_description.place(x=50, y=40)
        lbl_costs = tk.Label(self, text='Действие')
        lbl_costs.place(x=50, y=70)
        lbl_price = tk.Label(self, text='Сумма')
        lbl_price.place(x=50, y=100)

        self.entry_description = ttk.Entry(self)
        self.entry_description.place(x=200, y=40)

        self.entry_price = ttk.Entry(self)
        self.entry_price.place(x=200, y=100)

        self.combobox = ttk.Combobox(self, values=['Доход', 'Расход'])
        self.combobox.current(0)
        self.combobox.place(x=200, y=70)

        self.btn_save_and_continue = ttk.Button(self, text='Сохранить и продолжить', command=self.add_a_mark)
        self.btn_save_and_continue.place(x=57, y=155)

        self.btn_add = ttk.Button(self, text='Добавить')
        self.btn_add.place(x=210, y=155)
        self.btn_add.bind('<Button-1>', lambda event: self.add_a_mark())
        self.btn_add.bind('<Button-1>', lambda event: self.destroy(), add='+')

        btn_cancel = ttk.Button(self, text='Отмена', command=self.destroy)
        btn_cancel.place(x=290, y=155)

        self.grab_set()
        self.focus_get()


class Update(Child):
    def __init__(self):
        super().__init__()
        self.init_edit()
        self.database = database
        self.default_data()

    def update(self):
        self.view.update_records(self.entry_description.get(), self.combobox.get(), self.entry_price.get())
        self.destroy()

    def init_edit(self):
        self.title('Редактировать')
        btn_edit = ttk.Button(self, text='Редактировать', command=self.update)
        btn_edit.place(x=195, y=155)
        self.btn_save_and_continue.place(x=40, y=155)
        self.btn_save_and_continue.bind('<Button-1>',
                                        lambda event: self.view.update_records(self.entry_description.get(),
                                                                               self.combobox.get(),
                                                                               self.entry_price.get(),
                                                                               ))
        self.btn_add.destroy()

    def default_data(self):
        try:
            self.database.cursor.execute('''SELECT * FROM control WHERE id=?''',
                                         (self.view.tree.set(self.view.tree.selection()[0], '#1'),))
            row = self.database.cursor.fetchone()
            self.entry_description.insert(0, row[1])
            if row[2] != 'Доход':
                self.combobox.current(1)
            self.entry_price.insert(0, row[3])
        except IndexError:
            self.destroy()
            messagebox.showwarning("Ошибка", "Выберите запись для изменения!")


class Search(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.init_search()
        self.view = app

    def init_search(self):
        self.title('Поиск')
        self.geometry('300x100+400+300')
        self.resizable(False, False)

        lbl_search = tk.Label(self, text='Поиск')
        lbl_search.place(x=50, y=20)

        self.entry_search = ttk.Entry(self)
        self.entry_search.place(x=105, y=20, width=150)

        btn_cancel = ttk.Button(self, text='Закрыть', command=self.destroy)
        btn_cancel.place(x=185, y=50)

        btn_search = ttk.Button(self, text='Поиск')
        btn_search.place(x=105, y=50)
        btn_search.bind('<Button-1>', lambda event: self.view.search_records(self.entry_search.get()))
        btn_search.bind('<Button-1>', lambda event: self.destroy(), add='+')


if __name__ == '__main__':
    window = tk.Tk()
    database = DataBase()
    app = Main(window)
    app.pack()
    window.title('Cost control')
    window.geometry('665x430+300+200')
    window.resizable(False, False)
    tk.Label(text='Version 1.1').pack()
    app.mainloop()
