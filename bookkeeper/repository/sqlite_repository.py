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
        types = ',\n'.join([f'{field}' for field, typ in self.fields.items()])

        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('PRAGMA foreign_keys = ON')
        cursor.execute(f"""CREATE TABLE IF NOT EXISTS {self.table_name} (
                       id INTEGER PRIMARY KEY,
                       {types});""")
        conn.commit()
        conn.close()


    def add(self, obj: T) -> int:

        if getattr(obj, 'pk', None) != 0:
            raise ValueError('trying to add {} with filled pk attribute'.format(obj))
        
        names = ', '.join(self.fields.keys())
        p = ', '.join('?'*len(self.fields))
        values = [getattr(obj, x) for x in self.fields]

        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('PRAGMA foreign_keys = ON')
        cursor.execute(f'INSERT into {self.table_name} ({names}) VALUES ({p})', values)
        obj.pk = cursor.lastrowid
        conn.commit()
        conn.close()

        return obj.pk
    

    def delete(self, pk: int) -> None:
        pass


    def get_all(self, where: Dict[str, Any] | None = None) -> List[T]:
        pass


    def get(self, pk: int) -> T | None:
        pass


    def update(self, obj: T) -> None:
        pass