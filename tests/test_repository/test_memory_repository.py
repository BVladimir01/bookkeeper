import sys
sys.path.append('D:\\физтех\\proga\\bookkeeper_project')

from bookkeeper.repository.memory_repository import MemoryRepository
import pytest


@pytest.fixture
def custom_class():
    class Custom():
        pk = 0
    
    return Custom


@pytest.fixture
def repo():
    return MemoryRepository()


def test_crud(custom_class, repo):
    obj = custom_class()
    pk = repo.add(obj)
    assert obj.pk == pk
    assert repo.get(pk) == obj
    obj2 = custom_class()
    obj2.pk = pk
    repo.update(obj2)
    assert repo.get(pk) == obj2
    repo.delete(pk)
    assert repo.get(pk) == None