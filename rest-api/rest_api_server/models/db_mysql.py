#!/usr/bin/env python3

from sqlalchemy import create_engine

from rest_api_server.models.db_base import BaseDB
from rest_api_server.models.migrator import Migrator


class MySQLDB(BaseDB):
    def _get_engine(self):
        return create_engine(
            'mysql+mysqlconnector://%s:%s@%s/%s?charset=utf8mb4' %
            self._config.rest_db_params(),
            pool_size=200,
            max_overflow=25,
            pool_pre_ping=True,
        )

    def create_schema(self):
        migrator = Migrator(self.engine)
        migrator.migrate_all()
