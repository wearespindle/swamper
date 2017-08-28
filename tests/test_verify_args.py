from collections import namedtuple

from pytest import raises, fail

from swamper.base import BaseSwamper


def test_types_for_field_list_ok():
    """
    Test objects you can use to provide field names.
    """
    data = {'name': 'swamper'}
    for fields in (
        ['name'],
        ('name',),
        set(['name']),
        namedtuple('tuple', 'fields')(fields='name'),
    ):
        try:
            swamper = BaseSwamper(fields, data)
        except TypeError as e:
            fail(str(e))

        assert 'name' in swamper.fields


def test_types_for_field_list_fail():
    """
    Test objects you cannot use to provide field names.
    """
    data = {'name': 'swamper'}
    for fields in (
        {'field': 'name'},
        [('name',)],
        'name',
    ):
        with raises(TypeError):
            BaseSwamper(fields, data)


def test_types_for_data_ok():
    """
    Test objects you can use to provide data.
    """
    fields = ['name']
    for data in (
        {'name': 'swamper'},
        namedtuple('tuple', 'name')(name='swamper')._asdict(),
    ):
        try:
            swamper = BaseSwamper(fields, data)
        except TypeError as e:
            fail(str(e))

        assert swamper.raw_data['name'] == 'swamper'


def test_types_for_data_fail():
    """
    Test objects you cannot use to provide data.
    """
    fields = ['name']
    for data in (
        ('swamper',),
        namedtuple('tuple', 'name')(name='swamper'),
    ):
        with raises(TypeError):
            BaseSwamper(fields, data)


def test_types_for_instances_ok():
    """
    Test objects you can use to provide data.
    """
    class Swamper(BaseSwamper):
        def build_instances(self):
            self.instances = {
                int: 4,
                float: 5.0,
                bytes: b'6',
            }

    fields = ['name']
    data = {'name': 'swamper'}
    try:
        Swamper(fields, data).is_clean()
    except TypeError as e:
        fail(str(e))


def test_types_for_instances_fail():
    """
    Test objects you cannot use to provide data.
    """
    class Swamper(BaseSwamper):
        def build_instances(self):
            self.instances = (4, 5.0, '6')

    fields = ['name']
    data = {'name': 'swamper'}
    with raises(TypeError):
        Swamper(fields, data).is_clean()


def test_types_for_instance_to_data_fields_ok():
    """
    Test objects you can use to map field names.
    """
    class Swamper(BaseSwamper):
        instance_to_data_fields = {'first_name': 'name'}

    fields = ['first_name']
    data = {'name': 'swamper'}
    try:
        Swamper(fields, data)
    except TypeError as e:
        fail(str(e))


def test_types_for_instance_to_data_fields_fail():
    """
    Test objects you cannot use to map field names.
    """
    class Swamper(BaseSwamper):
        instance_to_data_fields = [('first_name', 'name')]

    fields = ['first_name']
    data = {'name': 'swamper'}
    with raises(TypeError):
        Swamper(fields, data)


def test_build_or_update_object_types_for_field_list_fail():
    """
    Test objects you cannot use to provide field names for `build_or_update`.
    """
    data = {'name': 'swamper'}
    fields = ['name']

    class Object(object):
        name = ''

    class Swamper(BaseSwamper):
        def build_instances(self):
            self.instances = {}
            self.instances[Object] = Object()

    swamper = Swamper(fields, data)
    assert swamper.errors == {}

    for fields in (
        {'field': 'name'},
        [('name',)],
        'name',
    ):
        with raises(TypeError):
            swamper.build_or_update(Object, fields)


def test_build_or_update_object_types_for_object_fail():
    """
    Test types you cannot use to provide object class for `build_or_update`.
    """
    data = {'name': 'swamper'}
    fields = ['name']

    class Object(object):
        name = ''

    class AnotherObject(object):
        name = ''

    class Swamper(BaseSwamper):
        def build_instances(self):
            self.instances = {}
            self.instances[Object] = Object()

    swamper = Swamper(fields, data)
    assert swamper.errors == {}

    with raises(TypeError):
        swamper.build_or_update(AnotherObject, fields)
