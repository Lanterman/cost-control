import unittest

from project.database import DataBase, CostControl as CoCo


class TestMain(unittest.TestCase):
    """Проверка функционала кнопок"""

    def setUp(self):
        """Предварительные данные"""
        self.db = DataBase()

        self.delete_db()

        self.db.insert_data('зарплата', 'продукты', 'Доход', 1000)
        self.db.insert_data('зашел в магазин', 'продукты', 'Расход', 1000)

    def delete_db(self):
        """Очистка базы данныз """
        self.db.connection.query(CoCo).delete()
        self.db.connection.commit()

    def test_clean_the_mark(self):
        """Проверка метода clean_the_mark()"""
        reports = self.db.connection.query(CoCo)
        self.assertEqual(len([*reports]), 2)

        [self.db.connection.delete(cost) for cost in reports]
        self.db.connection.commit()

        reports = self.db.connection.query(CoCo)
        self.assertNotEqual(len([*reports]), 2)

    def test_delete_records(self):
        """Проверка метода delete_records()"""
        reports = self.db.connection.query(CoCo.description, CoCo.category, CoCo.costs, CoCo.price)
        exp_data = [
            ('зарплата', '---------', 'Доход', 1000.0),
            ('зашел в магазин', 'продукты', 'Расход', 1000.0)
        ]

        self.assertTrue(reports)
        self.assertEqual([*reports], exp_data)

        for selection_item in reports:
            reports = self.db.connection.query(CoCo).filter_by(description=selection_item[0])
            self.db.connection.delete(reports[0])
        self.db.connection.commit()

        reports = self.db.connection.query(CoCo)
        self.assertNotEqual([*reports], exp_data)


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
        self.db.connection.query(CoCo).delete()
        self.db.connection.commit()

    def test_calculate(self):
        """Проверка расчет финансов"""
        reports = self.db.connection.query(CoCo.costs, CoCo.price)
        data = [('Доход', 1000.0), ('Расход', -1000.0)]
        profit = round(sum([price for costs, price in reports]), 2)
        income = round(sum([price for costs, price in reports if costs == 'Доход']), 2)
        expenditure = round(sum([price for costs, price in reports if costs == 'Расход']), 2)

        self.assertEqual([*reports], data)
        self.assertEqual(profit, 0.0)
        self.assertEqual(income, 1000.0)
        self.assertEqual(expenditure, -1000.0)

    def test_description(self):
        """Проверка дополнительной информация при расчете"""
        mark = self.db.connection.query(CoCo.costs, CoCo.price)
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
        self.assertEqual([*mark], data)
        self.assertEqual(response, 0.0)
        self.assertEqual(text, 'От зарплаты до зарплаты ?')

    def test_matplotlib(self):
        """Проверка расчета гистограммы"""
        reports = self.db.connection.query(CoCo.category, CoCo.price).filter(CoCo.costs == 'Расход')
        categories = {'продукты': 0, 'транспорт': 0, 'связь': 0, 'работа': 0, 'хобби': 0, 'дом': 0, 'копилка': 0,
                      'другое': 0}

        for category, price in reports:
            if category in categories:
                categories[category] += price
            else:
                categories['другое'] += price

        x = list(categories.keys())
        y = [-1 * categories[category] for category in categories]

        self.assertTrue(reports)
        self.assertEqual(len([*reports]), 1)
        self.assertEqual(categories['продукты'], -1000)
        self.assertEqual(categories['другое'], 0)
        self.assertEqual(x, ['продукты', 'транспорт', 'связь', 'работа', 'хобби', 'дом', 'копилка', 'другое'])
        self.assertEqual(y, [1000, 0, 0, 0, 0, 0, 0, 0])


if __name__ == '__main__':
    unittest.main()
