from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Protocol, Any, Dict, List


class Model(Protocol):
    """
    Model should contain pk attribute
    """
    pk: int


T = TypeVar('T', bound=Model)


class AbstractRepository(ABC, Generic[T]):

    @abstractmethod
    def add(self, obj:T) -> int:
        """
        Добавить объект в репозиторий. вернуть id
        объекта, записать id в атрибут pk
        """

    @abstractmethod
    def get(self, pk:int) -> T | None:
        """
        Получить объект по id
        """

    @abstractmethod
    def update(self, obj:T) -> None:
        """
        Обновить данные об объекте
        """

    @abstractmethod
    def delete(self, pk: int) -> None:
        """
        Удалить запись
        """

    @abstractmethod
    def get_all(self, where: Dict[str, Any] | None = None) -> List[T]:
        """
        Получить все записи по некоторому условия where - условие в виде
        словаря {'название поля': значение} если условие не задано, вернуть все записи
        """
