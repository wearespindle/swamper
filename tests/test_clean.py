import six

from swamper.base import BaseSwamper


def test_clean_field_ok_return_value():
    """
    Test field clean methods are called and its output is used to replace the
    value for field in cleaned data and if nothing is return the value is
    also replacing with None ('nothing').
    """
    data = {'name': 'swamper'}
    fields = ['name']

    baseswamper = BaseSwamper(fields, data)
    assert baseswamper.is_clean() is True
    assert baseswamper.cleaned_data['name'] == 'swamper'

    class Swamper(BaseSwamper):
        def clean_name(self, value, is_blank):
            """
            Deliberately change the value for this field for the purpose of
            testing that this method has been called.
            """
            return [value]

    swamper = Swamper(fields, data)
    assert swamper.is_clean() is True
    assert swamper.cleaned_data['name'] == ['swamper']

    class Swamper(BaseSwamper):
        def clean_name(self, value, is_blank):
            """
            Modifying cleaned_data instead of returning does not work.
            """
            self.cleaned_data['name'] = 'rotinaj'

    swamper = Swamper(fields, data)
    assert swamper.is_clean() is True
    assert swamper.cleaned_data['name'] is None


def test_clean_field_raise_error():
    """
    Test raising an error inside a field's clean method will remove it from
    cleaned data and add an error message for this field.
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
    assert swamper.errors == {
        'name': ['Name must be a string'],
    }
    assert 'name' not in swamper.cleaned_data


def test_clean_add_error():
    """
    Test adding an error for a field inside the global clean method will remove
    that field from cleaned data and add an error message for this field.
    """
    data = {'name': 4567}
    fields = ['name']

    baseswamper = BaseSwamper(fields, data)
    assert baseswamper.is_clean() is True

    class Swamper(BaseSwamper):
        def clean(self):
            """
            Add errors for a field can be done in the global clean.
            """
            name = self.cleaned_data['name']
            if not isinstance(name, six.string_types):
                self.add_error('name', 'Name must be a string')

            return self.cleaned_data

    swamper = Swamper(fields, data)
    assert swamper.is_clean() is False
    assert swamper.errors == {
        'name': ['Name must be a string'],
    }
    assert 'name' not in swamper.cleaned_data


def test_clean_add_error_for_unknown_field():
    """
    Test adding an error for an unknown field inside the global clean method
    will trigger an exception.
    """
    data = {'name': 4567}
    fields = ['name']

    class Swamper(BaseSwamper):
        def clean(self):
            """
            Add errors for a field can be done in the global clean.
            """
            # name = self.cleaned_data['name']
            # if not isinstance(name, six.string_types):
            self.add_error('swamper', 'Name must be a string')

            return self.cleaned_data

    swamper = Swamper(fields, data)
    assert swamper.is_clean() is False
    assert swamper.errors == {
        None: ["No field named 'swamper'"],
    }


def test_clean_is_blank():
    """
    Test value for is_blank for any field.
    """
    data = {
        'name': 'swamper',
        'name_1': None,
        'name_2': '',
        'name_3': [],
        'name_4': 0,
    }
    fields = ['name', 'name_1', 'name_2', 'name_3', 'name_4', 'name_5']

    class Swamper(BaseSwamper):
        def clean_name(self, value, is_blank):
            assert is_blank is False

        def clean_name_1(self, value, is_blank):
            assert is_blank is True

        def clean_name_2(self, value, is_blank):
            assert is_blank is True

        def clean_name_3(self, value, is_blank):
            assert is_blank is True

        def clean_name_4(self, value, is_blank):
            assert is_blank is False

        def clean_name_5(self, value, is_blank):
            assert is_blank is False

    swamper = Swamper(fields, data)
    swamper.is_clean()


def test_clean_instances():
    """
    Test adding an error for an unknown field inside the global clean method
    will trigger an exception.
    """
    class Object(object):
        def __init__(self, name):
            self.name = name

    objects = [Object('jane'), Object('john')]

    data = {'name': 'swamper'}
    fields = ['name']

    class Swamper(BaseSwamper):
        def build_instances(self):
            self.instances = {}
            self.instances[Object] = Object(self.data['name'])

        def clean_instances(self):
            instance = self.instances[Object]
            for obj in objects:
                if obj.name == instance.name:
                    # Match found, refers to an object.
                    return

            raise ValueError("No object with name 'swamper'")

    swamper = Swamper(fields, data)
    assert swamper.is_clean() is False
    assert swamper.errors == {
        None: ["No object with name 'swamper'"],
    }


def test_clean_data_contains_instance_value():
    """
    Test values from instances remain when not in data.
    """
    data = {'first_name': 'John'}
    fields = ['job_title', 'first_name']

    class Job(object):
        job_title = 'swamper'
        first_name = ''

    class Swamper(BaseSwamper):
        def build_instances(self):
            obj = Job()
            self.instances = {}
            self.instances[Job] = obj

        def clean_instances(self):
            """
            `clean` depends on having both job_title and first_name, so provide
            the data which isn't available from self.data by copying it from
            an instance to self.cleaned_data.
            """
            if self.instances:
                for model, instance in self.instances.items():
                    # Update cleaned_data with fields from instance that aren't
                    # part of the new data.
                    initial_fields = set(fields) - set(self.data.keys())
                    obj_data = {field: getattr(instance, field) for field in initial_fields}
                    self.cleaned_data.update(obj_data)

        def clean(self):
            if self.cleaned_data['job_title'] == 'swamper':
                if not self.cleaned_data['first_name'].startswith('J'):
                    raise ValueError('Only people with a first name that begin '
                                     'with the letter J can become swampers.')

            return self.cleaned_data

    swamper = Swamper(fields, data)
    assert swamper.errors == {}
    assert swamper.cleaned_data['job_title'] == 'swamper'
    assert swamper.cleaned_data['first_name'] == 'John'

    obj = Job()
    obj = swamper.build_or_update(obj, fields)
    assert obj.job_title == 'swamper'
    assert obj.first_name == 'John'
