from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Protocol, Any, Dict, List
from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import QEvent, QObject, Qt, QSize, Signal

class AbstractRepository(ABC):
    expense_table: object
    budget_table: object

    @abstractmethod
    def init_ui(self) -> None:
        """
        Initiates all widget, fills data
        """