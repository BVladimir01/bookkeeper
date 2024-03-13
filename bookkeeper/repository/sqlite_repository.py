from inspect import get_annotations
from typing import Any, Dict, List
from bookkeeper.repository.abstract_repository import AbstractRepository, T
import sqlite3


class SQLiteRepository(AbstractRepository[T]):
    def __init__(self, db_file: str, cls: type) -> None:
        self.db_file = db_file
        self.table_name = cls.__name__.lower()
        self.fields = get_annotations(cls, eval_str=True)
        self.fields.pop('pk')
    
    def add(self, obj: T) -> int:
        names = ', '.join(self.fields.keys)
        p = ', '.joint('?'*len(self.fields))
        values = [getattr(obj, x) for x in self.fields]
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('PRAGMA foreign_keys = ON')
        cursor.execute(f'INSERT into {self.table_name} ({names}) VALUES ({p})', values)
        obj.pk = cursor.lastrowid
        return obj.pk
    
    def delete(self, pk: int) -> None:
        pass

    def get_all(self, where: Dict[str, Any] | None = None) -> List[T]:
        pass

    def get(self, pk: int) -> T | None:
        pass

    def update(self, obj: T) -> None:
        pass