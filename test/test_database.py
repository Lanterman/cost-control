import unittest

from project.database import DataBase, ValidateData
from project.database import CostControl as CoCo


class TestDataBase(unittest.TestCase):
    """Тестирование базы данных"""
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

    def test_insert_data(self):
        """Проверка метода insert_data()"""
        response = self.db.connection.query(CoCo.description, CoCo.category, CoCo.costs, CoCo.price)
        obj_1, obj_2 = response[0], response[1]
        data_1 = ('зарплата', '---------', 'Доход', 1000.0)
        data_2 = ('зашел в магазин', 'продукты', 'Расход', 1000.0)

        self.assertEqual(obj_1, data_1)
        self.assertEqual(obj_2, data_2)


class TestValidateData(unittest.TestCase):
    """Проверка валидатора полей"""

    def test_validate_data(self):
        """Проверка метода validate_data()"""
        valid = ValidateData()
        check_1 = valid.validate_data('продукты', 'Расход', 10)
        check_2 = valid.validate_data('продукты1', 'Расход', 10)
        check_3 = valid.validate_data('продукты', 'Расход1', 10)

        self.assertTrue(check_1)
        self.assertIsNone(check_2)
        self.assertIsNone(check_3)

    def test_control_of_filling_the_price(self):
        """Проверка метода control_of_filling_the_price()"""
        data_1 = [
            {'id': 1, 'description': 'зарплата', 'category': '---------', 'costs': 'Доход', 'price': 1000.0},
            {'id': 2, 'description': 'зашел в магазин', 'category': 'продукты', 'costs': 'Расход', 'price': 1000.0}
        ]
        data_2 = []
        for data in data_1:
            if data['costs'] == 'Расход' and data['price'] > 0:
                data['price'] = round(float(-1 * data['price']))
            elif data['costs'] == 'Доход' and data['price'] < 0:
                data['price'] = round(float(-1 * data['price']))
            data_2 += [data]

        self.assertEqual(len(data_2), 2)
        self.assertEqual(data_2[1]['costs'], 'Расход')
        self.assertEqual(data_2[1]['price'], -1000.0)
        self.assertEqual(data_2[0]['costs'], 'Доход')
        self.assertEqual(data_2[0]['price'], 1000.0)


if __name__ == '__main__':
    unittest.main()
