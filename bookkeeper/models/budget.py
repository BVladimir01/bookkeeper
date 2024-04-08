"""
Module describes class of Budget model
"""


from dataclasses import dataclass


@dataclass
class Budget:
    """
    Бюджет, по выбранной категории на выбранный срок
    """

    pk: int = 0
    amount: int = 0
    time_period: str = 'Месяц'
    
    _time_period_options = {'День', 'Неделя', 'Месяц'}


    def __post_init__(self):
        """
        extra init procedures for dataclass
        corrects types of __init__ args
        """
        if not self.time_period in self._time_period_options:
            raise ValueError(f'Unsopported time period. Choose from {self._time_period_options}')
        for attr_name, attr_type in self.__annotations__.items():
            value = getattr(self, attr_name)
            if not isinstance(value, attr_type):
                setattr(self, attr_name, attr_type(value))
