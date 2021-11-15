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

    def open_dialog(self):
        Child()

    def records(self, description, costs, price):
        self.database.insert_data(description, costs, price)
        self.view_records()

    def view_records(self):
        self.database.cursor.execute("""SELECT * FROM control""")
        [self.tree.delete(i) for i in self.tree.get_children()]
        [self.tree.insert('', 'end', values=row) for row in self.database.cursor.fetchall()]


class Child(tk.Toplevel):
    def __init__(self):
        super().__init__(window)
        self.init_child()
        self.view = app

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

        btn_add = ttk.Button(self, text='Добавить')
        btn_add.place(x=210, y=155)
        btn_add.bind('<Button-1>', lambda event: self.view.records(self.entry_description.get(), self.combobox.get(),
                                                                   self.entry_price.get(),
                                                                   ))
        btn_cancel = ttk.Button(self, text='Отмена', command=self.destroy)
        btn_cancel.place(x=290, y=155)

        self.grab_set()
        self.focus_get()


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
