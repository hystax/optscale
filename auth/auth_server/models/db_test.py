from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from auth.auth_server.models.db_base import BaseDB


class TestDB(BaseDB):
    def _get_engine(self):
        return create_engine('sqlite://',
                             poolclass=StaticPool,
                             connect_args={'check_same_thread': False})

    def create_schema(self):
        self.create_all()
