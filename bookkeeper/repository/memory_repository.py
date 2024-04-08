"""
Describes memory type of repository. Implements abstract repository
"""


from itertools import count
from typing import Any, Dict, List
from repository.abstract_repository import AbstractRepository, T


class MemoryRepository(AbstractRepository[T]):
    """
    Работает в оперативной памяти. Хранит в словаре
    """

    def __init__(self) -> None:
        self._container : Dict[int, T]

        self._container = {}
        self._counter = count(1)


    def add(self, obj: T) -> int:
        """
        add obj to repo, return id of added object
        """
        if getattr(obj, 'pk', None) != 0:
            raise ValueError(f'trying to add {obj} with filled pk attribute')
        pk = next(self._counter)
        self._container[pk] = obj
        obj.pk = pk
        return pk


    def get(self, pk: int) -> T | None:
        """
        returns object with id=pk, else None
        """
        return self._container.get(pk)


    def update(self, obj: T) -> None:
        """
        Changes object with id=obj.pk to obj
        """
        if obj.pk == 0:
            raise ValueError('attempt to update object with unknown pk')
        self._container[obj.pk] = obj


    def delete(self, pk: int) -> T:
        """
        deletes object with id=pk and returns deleted object
        """
        return self._container.pop(pk)


    def get_all(self, where: Dict[str, Any] | None = None) -> List[T]:
        """
        returns list of instances with optional contidions of type
        dict{str of attribute: value of attribute}
        """
        if where is None:
            return list(self._container.values())
        res = []
        for obj in self._container.values():
            flag = 0
            for attr, value in where.items():
                if getattr(obj, attr) != value:
                    flag = 1
                    break
            if not flag:
                res.append(obj)
        return res
