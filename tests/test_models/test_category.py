import sys
sys.path.append('D:\\физтех\\proga\\bookkeeper_project')

from bookkeeper.models.category import Category
from bookkeeper.repository.memory_repository import MemoryRepository
import pytest


@pytest.fixture
def repo():
    return MemoryRepository()


def test_create_object():
    c = Category('name2')
    assert c.name == 'name2'
    assert c.parent == None
    assert c.pk == 0

    c = Category('name2', parent=2, pk=1)
    assert c.name == 'name2'
    assert c.parent == 2
    assert c.pk == 1


def test_reassign():
    c = Category('name2', parent=2, pk=1)
    c.parent = 1
    c.pk = 2
    assert c.parent == 1
    assert c.pk == 2


def test_eq():
    c1 = Category('name2', parent=2, pk=1)
    c2 = Category('name2', parent=2, pk=1)
    assert not c1 is c2
    assert c1 == c2


def test_get_parent(repo):
    c1 = Category(name='parent')
    pk = repo.add(c1)
    c2 = Category(name='name', parent=pk)
    repo.add(c2)
    print(repo.get_all())
    assert c2.get_parent(repo) == c1


def test_get_parent(repo):
    c1 = Category(name='parent')
    pk = repo.add(c1)
    c2 = Category(name='name', parent=pk)
    c3 = Category(name='name2', parent=pk)
    repo.add(c2)
    repo.add(c3)
    print(repo.get_all())
    assert c1.get_children(repo) == [c2, c3]