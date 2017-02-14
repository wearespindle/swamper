import collections
import inspect

import six


NON_FIELD_ERRORS = None


class BaseJanitor(object):

    def __init__(self, fields, data, error_class=ValueError, skip_verify=False):
        self.fields = fields
        self.data = data
        self.instances = {}
        self.build_instances()

        self.skip_verify = skip_verify
        if not self.skip_verify:
            self._verify_args()

        self._errors = None
        self.error_class = error_class

    def _verify_args(self):
        # Verify fields type.
        if (not isinstance(self.fields, collections.Iterable) or
                isinstance(self.fields, collections.Mapping) or
                isinstance(self.fields, six.string_types)):
            raise TypeError("'fields' must be a 1-dimensional iterable (list, tuple, ..)")

        # Verify field types.
        for field in self.fields:
            if not isinstance(field, six.string_types):
                raise TypeError("'fields' must only contain field names")

        # Verify data type.
        if not isinstance(self.data, collections.Mapping):
            raise TypeError("'data' must be a 2-dimensional iterable (dict, ..)")

        # Verify instances type.
        if not isinstance(self.instances, collections.Mapping):
            raise TypeError("'instances' must be a 2-dimensional iterable (dict, ..)")

    def build_instances(self):
        """
        Build self.instances.
        """
        pass

    def clean_instances(self):
        """
        Clean self.instances.
        """
        pass

    def handle_error(self, field, error):
        if not isinstance(error, self.error_class):
            error = self.error_class(error)

        return [str(error)]

    @property
    def errors(self):
        if self._errors is None:
            self.full_clean()
        return self._errors

    def is_clean(self):
        """
        Returns True if the form has no errors.
        """
        return not self.errors

    def add_error(self, field, message):
        error_list = self.handle_error(field, message)

        if field not in self.errors:
            if field != NON_FIELD_ERRORS and field not in self.fields:
                raise ValueError("No field named '{}'".format(field))
            else:
                self._errors[field] = []

        self._errors[field].extend(error_list)
        if field in self.cleaned_data:
            del self.cleaned_data[field]

    def full_clean(self):
        self._errors = {}
        self.cleaned_data = {}

        try:
            self.clean_instances()
        except self.error_class as e:
            self.add_error(NON_FIELD_ERRORS, e)
        else:
            self._clean_fields()
            self._clean_all()

    def _clean_fields(self):
        for field in self.fields:
            value = self.data.get(field)
            self.cleaned_data[field] = value

            try:
                if hasattr(self, 'clean_%s' % field):
                    value = getattr(self, 'clean_%s' % field)(value)
                    self.cleaned_data[field] = value
            except self.error_class as e:
                self.add_error(field, e)

    def _clean_all(self):
        try:
            cleaned_data = self.clean()
        except self.error_class as e:
            self.add_error(NON_FIELD_ERRORS, e)
        else:
            if cleaned_data is not None:
                self.cleaned_data = cleaned_data

    def clean(self):
        return self.cleaned_data

    def setattr(self, instance, field, value):
        if field in self.cleaned_data:
            setattr(instance, field, self.cleaned_data[field])

    def get_or_update(self, object_or_class, fields):
        if not self.skip_verify:
            # Verify fields type.
            if not (isinstance(fields, collections.Iterable) and
                    not isinstance(fields, collections.Mapping) and
                    not isinstance(fields, six.string_types)):
                raise TypeError("'fields' must be 1 dimensional iterable (list, tuple, ..)")

            # Verify field types.
            for field in fields:
                if not isinstance(field, six.string_types):
                    raise TypeError("'fields' must only contain field names")

            # Verify if all instances type were pre-defined.
            if self.instances and object_or_class not in self.instances:
                raise TypeError("'object_or_class' must be in 'instances'")

        if inspect.isclass(object_or_class):
            instance = self.instances.get(object_or_class, object_or_class())
        else:
            instance = object_or_class

        for field in fields:
            self.setattr(instance, field, self.cleaned_data[field])

        return instance
