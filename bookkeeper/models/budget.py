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
        if not self.time_period in self._time_period_options:
            raise ValueError(f'Unsopported time period. Choose from {self._time_period_options}')
