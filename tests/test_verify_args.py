from collections import namedtuple

from pytest import raises, fail

from janitor.base import BaseJanitor as Janitor


def test_types_for_field_list_ok():
    """
    Test objects you can use to provide field names.
    """
    data = {'name': 'janitor'}
    for fields in (
        ['name'],
        ('name',),
        set(['name']),
        namedtuple('tuple', 'fields')(fields='name'),
    ):
        try:
            janitor = Janitor(fields, data)
        except TypeError as e:
            fail(str(e))

        assert 'name' in janitor.fields


def test_types_for_field_list_fail():
    """
    Test objects you cannot use to provide field names.
    """
    data = {'name': 'janitor'}
    for fields in (
        {'field': 'name'},
        [('name',)],
        'name',
    ):
        with raises(TypeError):
            Janitor(fields, data)


def test_types_for_data_ok():
    """
    Test objects you can use to provide data.
    """
    fields = ['name']
    for data in (
        {'name': 'janitor'},
        namedtuple('tuple', 'name')(name='janitor')._asdict(),
    ):
        try:
            janitor = Janitor(fields, data)
        except TypeError as e:
            fail(str(e))

        assert janitor.data['name'] == 'janitor'


def test_types_for_data_fail():
    """
    Test objects you cannot use to provide data.
    """
    fields = ['name']
    for data in (
        ('janitor',),
        namedtuple('tuple', 'name')(name='janitor'),
    ):
        with raises(TypeError):
            Janitor(fields, data)


def test_types_for_instances_ok():
    """
    Test objects you can use to provide data.
    """
    fields = ['name']
    data = {'name': 'janitor'}
    for instances in (
        # Since everything is an object, 'type(obj): obj' will work with these.
        [4, 5.0, '6', u'7'],
    ):
        try:
            Janitor(fields, data, instances)
        except TypeError as e:
            fail(str(e))


def test_types_for_instances_fail():
    """
    Test objects you cannot use to provide data.
    """
    fields = ['name']
    data = {'name': 'janitor'}
    for instances in (
        {'int': 4,
         'float': 5.0,
         'basestring': '6',
         'unicode': u'7'},
    ):
        with raises(TypeError):
            Janitor(fields, data, instances)


def test_fix_me_an_object_types_for_field_list_fail():
    """
    Test objects you cannot use to provide field names for `fix_me_an`.
    """
    data = {'name': 'janitor'}
    fields = ['name']

    class Object(object):
        name = ''

    instances = [Object()]

    janitor = Janitor(fields, data, instances=instances)
    assert janitor.errors == {}

    for fields in (
        {'field': 'name'},
        [('name',)],
        'name',
    ):
        with raises(TypeError):
            janitor.fix_me_an(Object, fields)


def test_fix_me_an_object_types_for_object_fail():
    """
    Test types you cannot use to provide object class for `fix_me_an`.
    """
    data = {'name': 'janitor'}
    fields = ['name']

    class Object(object):
        name = ''

    class AnotherObject(object):
        name = ''

    instances = [Object()]

    janitor = Janitor(fields, data, instances=instances)
    assert janitor.errors == {}

    with raises(TypeError):
        janitor.fix_me_an(AnotherObject, fields)
