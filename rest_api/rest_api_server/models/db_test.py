from sqlalchemy import create_engine

from rest_api.rest_api_server.models.db_base import BaseDB
from sqlalchemy.pool import StaticPool


class TestDB(BaseDB):
    def _get_engine(self):
        return create_engine('sqlite://',
                             poolclass=StaticPool,
                             connect_args={'check_same_thread': False})

    def create_schema(self):
        self.create_all()
