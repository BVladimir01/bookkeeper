from dataclasses import dataclass


@dataclass
class Budget:
    """
    Бюджет, по выбранной категории на выбранный срок
    """
    amount: int
    category: int
    time_period: str = 'month'
    pk: int = 0

    _time_period_options = {'day', 'week', 'month', 'year'}

    def __post_init__(self):
        if not self.time_period in self._time_period_options:
            raise ValueError(f'Unsopported time period. Choose from {self._time_period_options}')
