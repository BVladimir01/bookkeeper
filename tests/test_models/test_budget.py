import sys
sys.path.append('D:\\физтех\\proga\\bookkeeper_project')

from datetime import datetime
from bookkeeper.models.budget import Budget
from bookkeeper.repository.memory_repository import MemoryRepository
import pytest


@pytest.fixture
def repo():
    return MemoryRepository()


def test_create_with_full_args_list():
    b = Budget(amount=100,
                category=1,
                time_period='month')
    assert b.amount == 100
    assert b.category == 1
    assert b.time_period == 'month'


def test_create_brief():
    b = Budget(100, 1)
    assert b.amount == 100
    assert b.category == 1


def test_can_add_to_repo(repo):
    b = Budget(100, 1)
    pk = repo.add(b)
    assert b.pk == pk


def test_cannot_create_wrong_period():
    with pytest.raises(ValueError):
        b = Budget(100, 1, time_period='123')