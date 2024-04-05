from inspect import get_annotations
from typing import Any, Dict, List
from repository.abstract_repository import AbstractRepository, T
import sqlite3

class SQLiteRepository(AbstractRepository[T]):

    def __init__(self, db_file: str, cls: type) -> None:
        self.cls = cls
        self.db_file = db_file
        self.table_name = cls.__name__.lower()
        self.fields = get_annotations(cls, eval_str=True)
        self.attr_names = [field for field, typ in self.fields.items()]
        passed_str = ',\n'.join([f'{field}' + ' TEXT' for field in self.attr_names if not field == 'pk'])

        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('PRAGMA foreign_keys = ON')
        cursor.execute(f"""CREATE TABLE IF NOT EXISTS {self.table_name} (
                       id INTEGER PRIMARY KEY,
                       {passed_str});""")
        conn.commit()
        conn.close()


    def add(self, obj: T) -> int:

        if getattr(obj, 'pk', None) != 0:
            raise ValueError('trying to add {} with filled pk attribute'.format(obj))
        
        names = self.attr_names[1:]
        p = ', '.join('?'*len(names))
        values = [str(getattr(obj, x)) for x in names]
        passed_str = ', '.join(names)

        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('PRAGMA foreign_keys = ON')
        print(f'INSERT into {self.table_name} ({passed_str}) VALUES ({p})')
        print(values)
        cursor.execute(f'INSERT into {self.table_name} ({passed_str}) VALUES ({p})', values)
        obj.pk = cursor.lastrowid
        conn.commit()
        conn.close()

        return obj.pk
    

    def delete(self, pk: int) -> T:
        copy = self.get(pk)
        if copy == None:
            raise KeyError('No such id')
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('PRAGMA foreign_keys = ON')
        cursor.execute(f'DELETE FROM {self.table_name} WHERE id = {pk}')
        conn.commit()
        conn.close()
        return copy


    def get_all(self, where: Dict[str, Any] | None = None) -> List[T]:
        res_list = []

        if not where:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('PRAGMA foreign_keys = ON')
            res = cursor.execute(f'SELECT * FROM {self.table_name}')
            args_list = res.fetchall()
            conn.commit()
            conn.close()
            if args_list:
                for args in args_list:
                    names_vals_dict = {attr_name: attr_val for attr_name, attr_val in zip(self.attr_names, args)}
                    res_list.append(self.cls(**names_vals_dict)) 
            return res_list
        
        conditions = where.items()
        cond_fields = []
        cond_vals = []
        for item in conditions:
            cond_fields.append(item[0])
            cond_vals.append(item[1])
        print(set(cond_fields))
        print(set(self.fields) | {'pk'})

        if not set(cond_fields) <= (set(self.fields) | {'pk'}):
            raise KeyError('no such column(s): ' + str(set(cond_fields) - set(self.fields) - {'pk'}))
        
        queries = ''
        for field in cond_fields:
            queries += f' and {field} = ?'
        queries = queries[5:]
        queries = queries.replace(' pk ', ' id ')

        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('PRAGMA foreign_keys = ON')
        print(f'SELECT * FROM {self.table_name} WHERE ' + queries)
        res = cursor.execute(f'SELECT * FROM {self.table_name} WHERE ' + queries, cond_vals)
        args_list = res.fetchall()
        conn.commit()
        conn.close()
        if args_list:
            for args in args_list:
                    names_vals_dict = {attr_name: attr_val for attr_name, attr_val in zip(self.attr_names, args)}
                    res_list.append(self.cls(**names_vals_dict))
        return res_list


    def get(self, pk: int) -> T | None:
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('PRAGMA foreign_keys = ON')
        res = cursor.execute(f'SELECT * FROM {self.table_name} WHERE id = {pk}')
        args = res.fetchone()
        conn.commit()
        conn.close()
        if args == None:
            return None
        names_vals_dict = {attr_name: attr_val for attr_name, attr_val in zip(self.attr_names, args)}
        copy = self.cls(**names_vals_dict)
        return copy


    def update(self, obj: T) -> None:
        if obj.pk == 0:
            raise ValueError('attempt to update object with unknown pk')
        id = obj.pk
        names = self.attr_names[1:]
        new_values = tuple((getattr(obj, attr_name) for attr_name in names))
        passed_str = ', '.join(f"{name} = '{value}'" for name, value in zip(names, new_values))

        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('PRAGMA foreign_keys = ON')
        print(f"""UPDATE {self.table_name} SET {passed_str} WHERE id = {id};""")
        print(new_values)
        res = cursor.execute(f"""UPDATE {self.table_name} SET {passed_str} WHERE id = {id};""")
        conn.commit()
        conn.close()
