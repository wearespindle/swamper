from pytest import raises
import six

from swamper.base import BaseSwamper


def test_build_or_update_get():
    """
    Test building an object instance with attributes that were cleaned by the
    swamper.
    """
    data = {'name': 'swamper'}
    fields = ['name']

    class Object(object):
        name = ''

    class Swamper(BaseSwamper):
        def build_instances(self):
            self.instances = {}

    swamper = Swamper(fields, data)
    assert swamper.errors == {}

    obj = swamper.build_or_update(Object, [])

    assert obj.name == ''
    assert isinstance(obj, Object)


def test_build_or_update_update():
    """
    Test updating an object instance with attributes that were cleaned by the
    swamper.
    """
    data = {'name': 'swamper'}
    fields = ['name']

    class Object(object):
        name = ''

    class Swamper(BaseSwamper):
        def build_instances(self):
            obj = Object()
            self.instances = {}
            self.instances[Object] = obj

    swamper = Swamper(fields, data)
    assert swamper.errors == {}

    obj = Object()
    obj = swamper.build_or_update(obj, fields)
    assert obj.name == 'swamper'


def test_build_or_update_update_with_field_mapping():
    """
    Test updating an object instance with attributes that were cleaned by the
    swamper using different names for data fields.
    """
    data = {'name': 'swamper'}
    fields = ['first_name']

    class Object(object):
        first_name = ''

    class Swamper(BaseSwamper):
        instance_to_data_fields = {'first_name': 'name'}

        def build_instances(self):
            obj = Object()
            self.instances = {}
            self.instances[Object] = obj

    swamper = Swamper(fields, data)
    assert swamper.errors == {}

    obj = Object()
    obj = swamper.build_or_update(obj, fields)
    assert obj.first_name == 'swamper'


def test_build_or_update_fail():
    """
    Test build_or_update will fail when there are errors messages defined.
    """
    data = {'name': 4567}
    fields = ['name']

    baseswamper = BaseSwamper(fields, data)
    assert baseswamper.is_clean() is True

    class Swamper(BaseSwamper):
        def clean_name(self, value, is_blank):
            """
            Raise an exception to validate this error is added for this field
            and removed from cleaned data.
            """
            if not isinstance(value, six.string_types):
                raise self.error_class('Name must be a string')

            return value

    swamper = Swamper(fields, data)
    assert swamper.is_clean() is False

    with raises(ValueError):
        swamper.build_or_update(object, fields)
