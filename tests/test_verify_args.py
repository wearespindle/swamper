from collections import namedtuple

from pytest import raises, fail

from janitor.base import BaseJanitor


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
            janitor = BaseJanitor(fields, data)
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
            BaseJanitor(fields, data)


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
            janitor = BaseJanitor(fields, data)
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
            BaseJanitor(fields, data)


def test_types_for_instances_ok():
    """
    Test objects you can use to provide data.
    """
    class Janitor(BaseJanitor):
        def build_instances(self):
            self.instances = {
                int: 4,
                float: 5.0,
                bytes: b'6',
            }

    fields = ['name']
    data = {'name': 'janitor'}
    try:
        Janitor(fields, data)
    except TypeError as e:
        fail(str(e))


def test_types_for_instances_fail():
    """
    Test objects you cannot use to provide data.
    """
    class Janitor(BaseJanitor):
        def build_instances(self):
            self.instances = (4, 5.0, '6')

    fields = ['name']
    data = {'name': 'janitor'}
    with raises(TypeError):
        Janitor(fields, data)


def test_types_for_instance_to_data_fields_ok():
    """
    Test objects you can use to map field names.
    """
    class Janitor(BaseJanitor):
        instance_to_data_fields = {'first_name': 'name'}

    fields = ['first_name']
    data = {'name': 'janitor'}
    try:
        Janitor(fields, data)
    except TypeError as e:
        fail(str(e))


def test_types_for_instance_to_data_fields_fail():
    """
    Test objects you cannot use to map field names.
    """
    class Janitor(BaseJanitor):
        instance_to_data_fields = [('first_name', 'name')]

    fields = ['first_name']
    data = {'name': 'janitor'}
    with raises(TypeError):
        Janitor(fields, data)


def test_build_or_update_object_types_for_field_list_fail():
    """
    Test objects you cannot use to provide field names for `build_or_update`.
    """
    data = {'name': 'janitor'}
    fields = ['name']

    class Object(object):
        name = ''

    class Janitor(BaseJanitor):
        def build_instances(self):
            self.instances[Object] = Object()

    janitor = Janitor(fields, data)
    assert janitor.errors == {}

    for fields in (
        {'field': 'name'},
        [('name',)],
        'name',
    ):
        with raises(TypeError):
            janitor.build_or_update(Object, fields)


def test_build_or_update_object_types_for_object_fail():
    """
    Test types you cannot use to provide object class for `build_or_update`.
    """
    data = {'name': 'janitor'}
    fields = ['name']

    class Object(object):
        name = ''

    class AnotherObject(object):
        name = ''

    class Janitor(BaseJanitor):
        def build_instances(self):
            self.instances[Object] = Object()

    janitor = Janitor(fields, data)
    assert janitor.errors == {}

    with raises(TypeError):
        janitor.build_or_update(AnotherObject, fields)
