import unittest

from database import DataBase


class Main(unittest.TestCase):
    """Проверка функционала кнопок"""

    def setUp(self):
        """Предварительные данные"""
        self.db = DataBase()

        self.delete_db()

        self.db.insert_data('зарплата', 'продукты', 'Доход', 1000)
        self.db.insert_data('зашел в магазин', 'продукты', 'Расход', 1000)

    def delete_db(self):
        """Очистка базы данныз """
        self.db.cursor.execute('''DELETE FROM control''')
        self.db.connection.commit()

    def test_clean_the_mark(self):
        """Проверка метода clean_the_mark()"""
        self.db.cursor.execute('''SELECT ID, description, category, costs, price FROM control''')
        data = self.db.cursor.fetchall()
        exp_data = [
            (1, 'зарплата', '---------', 'Доход', 1000.0),
            (2, 'зашел в магазин', 'продукты', 'Расход', 1000.0)
                    ]

        self.assertTrue(data)
        self.assertEqual(data, exp_data)

        self.delete_db()

        self.db.cursor.execute('''SELECT * FROM control''')
        self.assertFalse(self.db.cursor.fetchall())

    def test_delete_records(self):
        """Проверка метода delete_records()"""
        self.db.cursor.execute('''SELECT ID, description, category, costs, price FROM control''')
        data = self.db.cursor.fetchall()
        exp_data = [
            (1, 'зарплата', '---------', 'Доход', 1000.0),
            (2, 'зашел в магазин', 'продукты', 'Расход', 1000.0)
        ]

        self.assertTrue(data)
        self.assertEqual(data, exp_data)

        for selection_item in data:
            self.db.cursor.execute('''DELETE FROM control WHERE id=?''', (str(selection_item[0])))

        self.db.cursor.execute('''SELECT * FROM control''')
        self.assertFalse(self.db.cursor.fetchall())


class TestUpdate(unittest.TestCase):
    """Проверка функционала кнопок"""

    def test_update_records(self):
        """Проверка метода update_records()"""
        response = [1, 'зарплата', 'продукты', 'Доход', 1000.0]
        self.assertEqual(response[2], 'продукты')
        if response[3] == 'Доход':
            response[2] = '---------'
        self.assertEqual(response[2], '---------')


class TestCalculate(unittest.TestCase):
    """Проверка функционала кнопок"""

    def setUp(self):
        """Предварительные данные"""
        self.db = DataBase()

        self.delete_db()

        self.db.insert_data('зарплата', 'продукты', 'Доход', 1000)
        self.db.insert_data('зашел в магазин', 'продукты', 'Расход', -1000)

    def delete_db(self):
        """Очистка базы данныз """
        self.db.cursor.execute('''DELETE FROM control''')
        self.db.connection.commit()

    def test_calculate(self):
        """Проверка расчет финансов"""
        self.db.cursor.execute("""SELECT costs, price FROM control""")
        response = self.db.cursor.fetchall()
        data = [('Доход', 1000.0), ('Расход', -1000.0)]
        profit = round(sum([price for costs, price in response]), 2)
        income = round(sum([price for costs, price in response if costs == 'Доход']), 2)
        expenditure = round(sum([price for costs, price in response if costs == 'Расход']), 2)

        self.assertEqual(response, data)
        self.assertEqual(profit, 0.0)
        self.assertEqual(income, 1000.0)
        self.assertEqual(expenditure, -1000.0)

    def test_description(self):
        """Проверка дополнительной информация при расчете"""
        self.db.cursor.execute("""SELECT costs, price FROM control""")
        mark = self.db.cursor.fetchall()
        data = [('Доход', 1000.0), ('Расход', -1000.0)]
        response = round(sum([price for costs, price in mark]), 2)
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

        self.assertTrue(mark)
        self.assertEqual(mark, data)
        self.assertEqual(response, 0.0)
        self.assertEqual(text, 'От зарплаты до зарплаты ?')

    def test_matplotlib(self):
        """Проверка расчета гистограммы"""
        self.db.cursor.execute('''SELECT category, price FROM control WHERE costs="Расход"''')
        data = self.db.cursor.fetchall()
        cat = {'продукты': 0, 'транспорт': 0, 'связь': 0, 'работа': 0, 'хобби': 0, 'дом': 0, 'копилка': 0, 'другое': 0}

        for category, price in data:
            if category in cat:
                cat[category] += price
            else:
                cat['другое'] += price

        x = list(cat.keys())
        y = [-1 * cat[i] for i in cat]

        self.assertTrue(data)
        self.assertEqual(len(data), 1)
        self.assertEqual(cat['продукты'], -1000)
        self.assertEqual(cat['другое'], 0)
        self.assertEqual(x, ['продукты', 'транспорт', 'связь', 'работа', 'хобби', 'дом', 'копилка', 'другое'])
        self.assertEqual(y, [1000, 0, 0, 0, 0, 0, 0, 0])


if __name__ == '__main__':
    unittest.main()
