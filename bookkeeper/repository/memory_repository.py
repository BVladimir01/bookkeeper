from itertools import count
from typing import Any
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Protocol, Any, Dict, List

from bookkeeper.repository.abstract_repository import AbstractRepository, T


class MemoryRepository(AbstractRepository[T]):
    """
    Работает в оперативной памяти. Хранит в словаре
    """
    def __init__(self) -> None:
        self._container : Dict[int, T]

        self._container = {}
        self._counter = count(1)

    def add(self, obj: T) -> int:
        #зачем именно гет, если обж из типа Т, можно просто обратиться
        if getattr(obj, 'pk', None) != 0:
            raise ValueError('trying to add {} with filled pk attribute'.format(obj))
        pk = next(self._counter)
        self._container[pk] = obj
        #Почему присваиваем пк если он и так типа Т
        obj.pk = pk
        return pk

    def get(self, pk: int) -> T | None:
        return self._container.get(pk)

    def update(self, obj: T) -> None:
        if obj.pk == 0:
            raise ValueError('attempt to update object with unknown pk')
        self._container[obj.pk] = obj

    def delete(self, pk: int) -> None:
        return self._container.pop(pk)
    
    def get_all(self, where: Dict[str, Any] | None = None) -> List[T]:
        if where is None:
            return list(self._container.values())
        return [obj for obj in self._container.values()
                if all(getattr(obj, attr) == value)
                for attr, value in where.items()]