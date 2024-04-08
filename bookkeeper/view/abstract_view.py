from abc import ABC, abstractmethod


class AbstractRepository(ABC):
    expense_table: object
    budget_table: object

    @abstractmethod
    def init_ui(self) -> None:
        """
        Initiates all widget, fills data
        """

    @abstractmethod
    def register_exp_add(self, handler) -> None:
        pass

    @abstractmethod
    def register_exp_delete(self, handler) -> None:
        pass

    @abstractmethod
    def register_exp_change(self, handler) -> None:
        pass

    @abstractmethod
    def register_exp_category_change(self, handler) -> None:
        pass

    @abstractmethod
    def register_budget_change(self, handler) -> None:
        pass

    @abstractmethod
    def register_update_categories(self, handler) -> None:
        pass

    @abstractmethod
    def register_category_change(self, handler) -> None:
        pass

    @abstractmethod
    def register_category_add(self, handler) -> None:
        pass

    @abstractmethod
    def register_category_delete(self, handler) -> None:
        pass
    
