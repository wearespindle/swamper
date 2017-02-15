import collections
import inspect

import six


NON_FIELD_ERRORS = None


class BaseJanitor(object):

    def __init__(self, fields, data, error_class=ValueError, skip_verify=False):
        """
        Build a janitor that clean given fields from data.

        Args:
            fields (list): list of field names to clean.
            data (dict): input to clean.
            error_class (Exception): class to catch from cleaning methods,
                these will end up as error messages.
            skip_verify (bool): toggle argument type checking (default=False).
        """
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
        """
        Validate types for variables that indicate what to clean.

        Raises:
            TypeError: when types not match for fields, data or instances.
        """
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
        """
        Turn an error (message) into an error (class).

        Args:
            field (str): name of the field to add the error for.
            error (str|self.error_class): cast error to this type if it isn't
                already.

        Returns:
            list: one or more error messages for said field.
        """
        if not isinstance(error, self.error_class):
            error = self.error_class(error)

        return [str(error)]

    @property
    def errors(self):
        """
        Build errors when never done so before.

        Returns:
            dict: Map of field to list of errors.
        """
        if self._errors is None:
            self.full_clean()
        return self._errors

    def is_clean(self):
        """
        Indicates if there were no errors cleaning input.

        Returns:
            bool: True if the form has no errors.
        """
        return not self.errors

    def add_error(self, field, message):
        """
        Add one or more error messages for a field. When adding an error for
        a field, this field is also removed from `cleaned_data`.

        Args:
            field (str): name of the field to add the error for.
            message (str|self.error_class): error message for given field.

        Raises:
            ValueError: if field was never specified when creating this janitor.
        """
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
        """
        Clean instances, fields and do a post clean where you have access to
        all cleaned input data so far. When an error is raised during cleaning
        of instances, don't continue.
        """
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
        """
        Run all clean methods for predefined fields, these methods are also
        called when the correspondig field isn't present in the input data.
        """
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
        """
        Run the global method to clean fields that depend on each other.
        """
        try:
            cleaned_data = self.clean()
        except self.error_class as e:
            self.add_error(NON_FIELD_ERRORS, e)
        else:
            if cleaned_data is not None:
                self.cleaned_data = cleaned_data

    def clean(self):
        """
        In this method you can clean fields that depend on each other.

        Returns:
            dict: the final cleaned data.
        """
        return self.cleaned_data

    def setattr(self, instance, field, value):
        """
        Assign value for field on instance.

        This is a separate method to make overriding easy. This method is used
        by `build_or_update`.

        Args:
            instance (object): any object to set the value for field on.
            field (str): name of the attribute to set from `cleaned_data`.
            value (object): any value you want to assign for field on the
                given instance.
        """
        if field in self.cleaned_data:
            setattr(instance, field, self.cleaned_data[field])

    def build_or_update(self, instance_or_class, fields):
        """
        Return an object with all fields assigned to it from the cleaned data.

        Args:
            instance_or_class (object|type): instance or type to build instance
                for to return with the field values assigned.
            fields (list): list of field names to assign for instance.

        Returns:
            object: instance with (updated) values for `fields`.
        """
        if not self.is_clean():
            raise ValueError('Cannot build or update because there are errors')

        if inspect.isclass(instance_or_class):
            klass = instance_or_class
            instance = self.instances.get(instance_or_class, instance_or_class())
        else:
            klass = type(instance_or_class)
            instance = instance_or_class

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
        if self.instances and klass not in self.instances:
            raise TypeError("'instance_or_class' must be in 'instances'")

        for field in fields:
            self.setattr(instance, field, self.cleaned_data[field])

        return instance
