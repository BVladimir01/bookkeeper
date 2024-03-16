import sys
sys.path.append('D:\\физтех\\proga\\bookkeeper_project')

from bookkeeper.repository.sqlite_repository import SQLiteRepository
import pytest
from dataclasses import dataclass


@pytest.fixture
def custom_class():
    @dataclass
    class Custom():
        pk: int = 0
        attr_name: str = 'name'
        val_name : int = 10
    
    return Custom


@pytest.fixture
def repo(custom_class):
    return SQLiteRepository('D:\\физтех\\proga\\bookkeeper_project\\tests\\test_db.db', custom_class)


def test_crud(custom_class, repo):
    obj = custom_class()
    pk = repo.add(obj)
    assert obj.pk == pk
    assert repo.get(pk) == obj
    obj2 = custom_class(attr_name='name2')
    obj2.pk = pk
    repo.update(obj2)
    assert repo.get(pk) == obj2
    a = repo.delete(pk)
    assert repo.get(pk) == None


def test_cannot_add_with_pk(repo, custom_class):
    obj = custom_class()
    obj.pk = 1
    with pytest.raises(ValueError):
        repo.add(obj)


def test_cannot_add_without_pk(repo):
    with pytest.raises(ValueError):
        repo.add(0)


def test_cannot_delete_unexistent(repo):
    with pytest.raises(KeyError):
        repo.delete(10000)


def test_cannot_update_without_pk(repo, custom_class):
    obj = custom_class()
    obj.pk = 0
    with pytest.raises(ValueError):
        repo.update(obj)


def test_get_all(repo, custom_class):
    objects = [custom_class() for i in range(5)]
    for o in objects:
        repo.add(o)
    assert repo.get_all() == objects


def test_get_all_with_condition(repo, custom_class):
    objects = []
    for i in range(5):
        o = custom_class()
        o.attr_name = str(i)
        o.val_name = 'test'
        repo.add(o)
        objects.append(o)
    assert repo.get_all({'attr_name': '0'}) == [objects[0]]
    assert repo.get_all({'val_name': 'test'}) == objects
