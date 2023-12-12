import unittest

from katara.katara_service.models.db_factory import DBType, DBFactory
from katara.katara_service.models.db_base import BaseDB


class TestControllerBase(unittest.TestCase):

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
        super().tearDown()
