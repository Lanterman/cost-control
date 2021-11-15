import tkinter as tk
from datetime import datetime
from tkinter import ttk
import sqlite3


class Main(tk.Frame):
    def __init__(self, window):
        super().__init__(window)
        self.init_main()
        self.database = database
        self.view_records()

    def init_main(self):
        toolbar = tk.Frame(bg='#d7d8e0', bd=5)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        self.add_img = tk.PhotoImage(file='img/add.png')
        btn_open_dialog = tk.Button(master=toolbar, text='Добавить позицию', command=self.open_dialog, bg='#d7d8e0',
                                    bd=0, compound=tk.TOP, image=self.add_img)
        btn_open_dialog.pack(side=tk.LEFT)

        self.update_img = tk.PhotoImage(file='img/update.png')
        btn_edit_dialog = tk.Button(master=toolbar, text='Редактировать', bg='#d7d8e0', bd=0, image=self.update_img,
                                    compound=tk.TOP, command=self.open_update)
        btn_edit_dialog.pack(side=tk.LEFT)

        self.delete_img = tk.PhotoImage(file='img/delete.png')
        btn_delete_dialog = tk.Button(master=toolbar, text='Удалить', bg='#d7d8e0', bd=0, image=self.delete_img,
                                      compound=tk.TOP, command=self.delete_records)
        btn_delete_dialog.pack(side=tk.LEFT)

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

        self.tree.pack()

    def records(self, description, costs, price):
        self.database.insert_data(description, costs, price)
        self.view_records()

    def update_records(self, description, costs, price):
        self.database.cursor.execute("""UPDATE control SET description=?, costs=?, price=?, date=? WHERE ID=?""",
                                     (description, costs, price, str(datetime.now())[:19],
                                      self.tree.set(self.tree.selection(), '#1')))
        self.database.connection.commit()
        self.view_records()

    def delete_records(self):
        for selection_item in self.tree.selection():
            self.database.cursor.execute("""DELETE FROM control WHERE id=?""", (self.tree.set(selection_item, '#1'),))
            self.database.connection.commit()
            self.view_records()

    def view_records(self):
        self.database.cursor.execute("""SELECT * FROM control""")
        [self.tree.delete(i) for i in self.tree.get_children()]
        [self.tree.insert('', 'end', values=row) for row in self.database.cursor.fetchall()]

    def open_dialog(self):
        Child()

    def open_update(self):
        Update()


class Child(tk.Toplevel):
    def __init__(self):
        super().__init__(window)
        self.init_child()
        self.view = app

    def add(self):
        self.view.records(self.entry_description.get(), self.combobox.get(), self.entry_price.get())
        self.destroy()

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

        self.combobox = ttk.Combobox(self, values=[u'Доход', u'Расход'])
        self.combobox.current(0)
        self.combobox.place(x=200, y=70)

        self.btn_save_and_continue = ttk.Button(self, text='Сохранить и продолжить')
        self.btn_save_and_continue.place(x=57, y=155)
        self.btn_save_and_continue.bind('<Button-1>', lambda event: self.view.records(self.entry_description.get(),
                                                                                      self.combobox.get(),
                                                                                      self.entry_price.get(),
                                                                                      ))
        self.btn_add = ttk.Button(self, text='Добавить', command=self.add)
        self.btn_add.place(x=210, y=155)
        btn_cancel = ttk.Button(self, text='Отмена', command=self.destroy)
        btn_cancel.place(x=290, y=155)

        self.grab_set()
        self.focus_get()


class Update(Child):
    def __init__(self):
        super().__init__()
        self.init_edit()

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


class DataBase:
    def __init__(self):
        self.connection = sqlite3.connect("control.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS control (
            id integer primary key,
            description text,
            costs text,
            price real,
            date text)
            """
        )
        self.connection.commit()

    def insert_data(self, description, costs, price):
        self.cursor.execute(
            """INSERT INTO control (description, costs, price, date) VALUES (?, ?, ?, ?)""",
            (description, costs, price, str(datetime.now())[:19])
        )
        self.connection.commit()


if __name__ == '__main__':
    window = tk.Tk()
    database = DataBase()
    app = Main(window)
    app.pack()
    window.title('Cost control')
    window.geometry('650x450+300+200')
    window.resizable(False, False)
    app.mainloop()
