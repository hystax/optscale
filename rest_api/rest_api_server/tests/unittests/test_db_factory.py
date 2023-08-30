import unittest

from rest_api.rest_api_server.models.db_factory import DBType, DBFactory
from tools.optscale_exceptions.common_exc import InvalidModelTypeException
from rest_api.rest_api_server.models.db_base import BaseDB


class DBFactoryTest(unittest.TestCase):
    def test_wrong_type(self):
        with self.assertRaises(InvalidModelTypeException):
            DBFactory('wrong_type').db()

    def test_get_db(self):
        for db_type, db_class in DBFactory.DBS.items():
            self.assertTrue(isinstance(DBFactory(db_type).db, db_class))

    def test_multiton(self):
        db_type = DBType.Test
        db1 = DBFactory(db_type).db
        db2 = DBFactory(db_type).db
        self.assertEqual(db1, db2)

    def test_base_db(self):
        base = BaseDB()
        with self.assertRaises(NotImplementedError):
            res = base.engine


if __name__ == '__main__':
    unittest.main(verbosity=2)
