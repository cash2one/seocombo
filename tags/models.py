from __future__ import unicode_literals, absolute_import

import operator
import inspect
import itertools

from collections import OrderedDict
from copy import deepcopy
from types import FunctionType

import functools

string_type = str
iteritems = operator.methodcaller('items')

def prepare_validator(func, argcount):
    if isinstance(func, classmethod):
        func = func.__get__(object).__func__
    if len(inspect.getargspec(func).args) < argcount:
        @functools.wraps(func)
        def newfunc(*args, **kwargs):
            if not kwargs or kwargs.pop('context', 0) is 0:
                args = args[:-1]
            return func(*args, **kwargs)
        return newfunc
    return func

class UndefinedType(object):

    _instance = None

    def __str__(self):
        return 'Undefined'

    def __repr__(self):
        return 'Undefined'

    def __eq__(self, other):
        return self is other

    def __ne__(self, other):
        return self is not other

    def __bool__(self):
        return False

    __nonzero__ = __bool__

    def __lt__(self, other):
        self._cmp_err(other, '<')

    def __gt__(self, other):
        self._cmp_err(other, '>')

    def __le__(self, other):
        self._cmp_err(other, '<=')

    def __ge__(self, other):
        self._cmp_err(other, '>=')

    def _cmp_err(self, other, op):
        raise TypeError("unorderable types: {0}() {1} {2}()".format(
                        self.__class__.__name__, op, other.__class__.__name__))

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        elif cls is not UndefinedType:
            raise TypeError("type 'UndefinedType' is not an acceptable base type")
        return cls._instance

    def __init__(self):
        pass

    def __setattr__(self, name, value):
        raise TypeError("'UndefinedType' object does not support attribute assignment")

class UndefinedValueError(AttributeError, KeyError):
    """Exception raised when accessing a field with an undefined value."""
    def __init__(self, model, name):
        msg = "'%s' instance has no value for field '%s'" % (model.__class__.__name__, name)
        super(UndefinedValueError, self).__init__(msg)

class FieldDescriptor(object):
    """
    ``FieldDescriptor`` instances serve as field accessors on models.
    """

    def __init__(self, name):
        """
        :param name:
            The field's name
        """
        self.name = name

    def __get__(self, instance, cls):
        """
        For a model instance, returns the field's current value.
        For a model class, returns the field's type object.
        """
        if instance is None:
            return cls._fields[self.name]
        else:
            Undefined = UndefinedType()
            value = instance._data.get(self.name, Undefined)
            if value is Undefined:
                raise UndefinedValueError(instance, self.name)
            else:
                return value

    def __set__(self, instance, value):
        """
        Sets the field's value.
        """
        field = instance._fields[self.name]
        value = field.pre_setattr(value)
        instance._data[self.name] = value

    def __delete__(self, instance):
        """
        Deletes the field's value.
        """
        del instance._data[self.name]

class ModelMeta(type):
    """
    Metaclass for Models.
    """

    def __new__(mcs, name, bases, attrs):
        """
        This metaclass adds two attributes to host classes:
        - mcs._fields,
        - mcs._validator_functions,

        This function creates those attributes like this:
        ``mcs._fields`` is list of fields that are Schematics types
        ``mcs._validator_functions`` are class-level validation functions
        """

        # Structures used to accumulate meta info
        fields = OrderedDict()
        validator_functions = {}  # Model level

        # Accumulate metas info from parent classes
        for base in reversed(bases):
            if hasattr(base, '_fields'):
                fields.update(deepcopy(base._fields))
            if hasattr(base, '_validator_functions'):
                validator_functions.update(base._validator_functions)

        # Parse this class's attributes into meta structures
        for key, value in iteritems(attrs):
            if key.startswith('validate_') and isinstance(value, (FunctionType, classmethod)):
                validator_functions[key[9:]] = prepare_validator(value, 4)

        # Convert list of types into fields for new klass
        fields.sort(key=lambda i: i[1]._position_hint)
        for key, field in iteritems(fields):
            attrs[key] = FieldDescriptor(key)

        # Ready meta data to be klass attributes
        attrs['_fields'] = fields
        attrs['_field_list'] = list(fields.items())
        attrs['_validator_functions'] = validator_functions

        klass = type.__new__(mcs, name, bases, attrs)

        # Register class on ancestor models
        klass._subclasses = []
        for base in klass.__mro__[1:]:
            if isinstance(base, ModelMeta):
                base._subclasses.append(klass)

        # Finalize fields
        for field_name, field in fields.items():
            field._setup(field_name, klass)

        klass._valid_input_keys = (
            set(itertools.chain(*(field.get_input_keys() for field in fields.values()))))

        return klass

    @property
    def fields(cls):
        return cls._fields