import unittest
from auth.auth_server.models.db_factory import DBType, DBFactory
from auth.auth_server.models.db_base import BaseDB


class TestModelBase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._db_session = None

    @property
    def db_session(self):
        db = DBFactory(DBType.TEST, None).db
        engine = db.engine
        if not self._db_session:
            self._db_session = BaseDB.session(engine)()
        return self._db_session

    def setUp(self):
        super().setUp()
        self.db = DBFactory(DBType.TEST, None).db
        self.db.create_all()

    def tearDown(self):
        DBFactory.clean_type(DBType.TEST)
        DBFactory.clean_type(DBType.TEST)
        super().tearDown()
