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
        for attr_name, attr_type in self.__annotations__.items():
            value = getattr(self, attr_name)
            if type(value) != attr_type:
                setattr(self, attr_name, attr_type(value))


if __name__ == '__main__':
    test_obj = Budget(pk='1', amount='100', time_period='Месяц')
    print(test_obj)