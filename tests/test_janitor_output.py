from pytest import raises
import six

from janitor.base import BaseJanitor


def test_build_or_update_get():
    """
    Test building an object instance with attributes that were cleaned by the
    janitor.
    """
    data = {'name': 'janitor'}
    fields = ['name']

    class Object(object):
        name = ''

    class Janitor(BaseJanitor):
        def build_instances(self):
            pass

    janitor = Janitor(fields, data)
    assert janitor.errors == {}

    obj = janitor.build_or_update(Object, [])

    assert obj.name == ''
    assert isinstance(obj, Object)


def test_build_or_update_update():
    """
    Test updating an object instance with attributes that were cleaned by the
    janitor.
    """
    data = {'name': 'janitor'}
    fields = ['name']

    class Object(object):
        name = ''

    class Janitor(BaseJanitor):
        def build_instances(self):
            obj = Object()
            self.instances[Object] = obj

    janitor = Janitor(fields, data)
    assert janitor.errors == {}

    obj = Object()
    obj = janitor.build_or_update(obj, fields)
    assert obj.name == 'janitor'


def test_build_or_update_fail():
    """
    Test build_or_update will fail when there are errors messages defined.
    """
    data = {'name': 4567}
    fields = ['name']

    basejanitor = BaseJanitor(fields, data)
    assert basejanitor.is_clean() is True

    class Janitor(BaseJanitor):
        def clean_name(self, value, is_blank):
            """
            Raise an exception to validate this error is added for this field
            and removed from cleaned data.
            """
            if not isinstance(value, six.string_types):
                raise self.error_class('Name must be a string')

            return value

    janitor = Janitor(fields, data)
    assert janitor.is_clean() is False

    with raises(ValueError):
        janitor.build_or_update(object, fields)
