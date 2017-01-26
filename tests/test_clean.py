import six

from janitor.base import BaseJanitor


def test_clean_field_ok_return_value():
    """
    Test field clean methods are called and its output is used to replace the
    value for field in cleaned data and if nothing is return the value is
    also replacing with None ('nothing').
    """
    data = {'name': 'janitor'}
    fields = ['name']

    basejanitor = BaseJanitor(fields, data)
    assert basejanitor.errors == {}
    assert basejanitor.cleaned_data['name'] == 'janitor'

    class Janitor(BaseJanitor):
        def clean_name(self, value):
            """
            Deliberately change the value for this field for the purpose of
            testing that this method has been called.
            """
            return [value]

    janitor = Janitor(fields, data)
    assert janitor.errors == {}
    assert janitor.cleaned_data['name'] == ['janitor']

    class Janitor(BaseJanitor):
        def clean_name(self, value):
            """
            Modifying cleaned_data instead of returning does not work.
            """
            self.cleaned_data['name'] = 'rotinaj'

    janitor = Janitor(fields, data)
    assert janitor.errors == {}
    assert janitor.cleaned_data['name'] is None


def test_clean_field_raise_error():
    """
    Test raising an error inside a field's clean method will remove it from
    cleaned data and add an error message for this field.
    """
    data = {'name': 4567}
    fields = ['name']

    basejanitor = BaseJanitor(fields, data)
    assert basejanitor.errors == {}

    class Janitor(BaseJanitor):
        def clean_name(self, value):
            """
            Raise an exception to validate this error is added for this field
            and removed from cleaned data.
            """
            if not isinstance(value, six.string_types):
                raise self.error_class('Name must be a string')

            return value

    janitor = Janitor(fields, data)
    assert janitor.errors == {
        'name': ['Name must be a string'],
    }
    assert 'name' not in janitor.cleaned_data


def test_clean_add_error():
    """
    Test adding an error for a field inside the global clean method will remove
    that field from cleaned data and add an error message for this field.
    """
    data = {'name': 4567}
    fields = ['name']

    basejanitor = BaseJanitor(fields, data)
    assert basejanitor.errors == {}

    class Janitor(BaseJanitor):
        def clean(self):
            """
            Add errors for a field can be done in the global clean.
            """
            name = self.cleaned_data['name']
            if not isinstance(name, six.string_types):
                self.add_error('name', 'Name must be a string')

            return self.cleaned_data

    janitor = Janitor(fields, data)
    assert janitor.errors == {
        'name': ['Name must be a string'],
    }
    assert 'name' not in janitor.cleaned_data


def test_clean_add_error_for_unknown_field():
    """
    Test adding an error for an unknown field inside the global clean method
    will trigger an exception.
    """
    data = {'name': 4567}
    fields = ['name']

    class Janitor(BaseJanitor):
        def clean(self):
            """
            Add errors for a field can be done in the global clean.
            """
            # name = self.cleaned_data['name']
            # if not isinstance(name, six.string_types):
            self.add_error('janitor', 'Name must be a string')

            return self.cleaned_data

    janitor = Janitor(fields, data)
    assert janitor.errors == {
        None: ["No field named 'janitor'"],
    }
