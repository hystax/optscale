import sqlite3
from datetime import datetime

from gemini.gemini_worker.duplicate_object_finder.aws.object_info import ObjectInfo
from gemini.gemini_worker.duplicate_object_finder.aws.stats import Stats


class SqliteCache:
    def __init__(self, filename: str, stats: Stats = None):
        self._connection = sqlite3.connect(filename)
        self._table_name = "object_info"
        self._stats = stats

        cursor = self._connection.cursor()
        create_table_query = f"CREATE TABLE '{self._table_name}' (tag TEXT, bucket TEXT, key TEXT, size integer);"
        cursor.execute(create_table_query)
        create_index_query = (
            f"CREATE INDEX {self._table_name}_idx ON {self._table_name}(tag);"
        )
        cursor.execute(create_index_query)
        self._connection.commit()

    def close(self):
        self._connection.close()

    def add(self, items: list[ObjectInfo]):
        if not items:
            return
        t = datetime.now()
        cursor = self._connection.cursor()
        val_list = [item.to_tuple() for item in items]

        query = f"INSERT INTO '{self._table_name}' (tag, bucket, key, size) VALUES (?, ?, ?, ?)"
        cursor.executemany(query, val_list)
        self._connection.commit()

        if self._stats:
            self._stats.timedelta_db += datetime.now() - t

    def get_duplicates(self) -> list[ObjectInfo]:
        cursor = self._connection.cursor()
        query = (
            f"SELECT * FROM '{self._table_name}' WHERE tag in "
            f"(SELECT tag FROM '{self._table_name}' GROUP BY tag HAVING COUNT(tag) > 1) "
            f"ORDER BY tag;")
        cursor.execute(query)
        res = [ObjectInfo.from_db_object(item) for item in cursor.fetchall()]
        return res
