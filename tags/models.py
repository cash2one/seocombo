from __future__ import unicode_literals, absolute_import
from _thread import get_ident

import operator
import inspect
import itertools

from collections import OrderedDict
from copy import deepcopy
from types import FunctionType

import functools
from tags.fields import BaseField

string_type = str
iteritems = operator.methodcaller('items')

def metaclass(metaclass):
    def make_class(cls):
        attrs = cls.__dict__.copy()
        del attrs['__dict__']
        del attrs['__weakref__']
        return metaclass(cls.__name__, cls.__bases__, attrs)
    return make_class

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


class ModelOptions(object):
    """
    This class is a container for all model configuration options. Its
    primary purpose is to create an independent instance of a model's
    options for every class.
    """

    def __init__(self, klass, namespace=None, roles=None, export_level=10,
                 serialize_when_none=None, export_order=False):
        """
        :param klass:
            The class which this options instance belongs to.
        :param namespace:
            A namespace identifier that can be used with persistence layers.
        :param roles:
            Allows to specify certain subsets of the model's fields for
            serialization.
        :param serialize_when_none:
            When ``False``, serialization skips fields that are None.
            Default: ``True``
        :param export_order:
            Specifies whether to maintain the original field order when exporting
            the model. This entails returning an ``OrderedDictionary`` instead of
            a regular dictionary.
            Default: ``False``
        """
        self.klass = klass
        self.namespace = namespace
        self.roles = roles or {}
        self.export_level = export_level
        if serialize_when_none is True:
            self.export_level = 10
        elif serialize_when_none is False:
            self.export_level = 1
        self.export_order = export_order


class ModelMeta(type):
    """
    Metaclass for Models.
    """

    def __new__(mcs, name, bases, attrs):
        """
        This metaclass adds four attributes to host classes: mcs._fields,
        mcs._serializables, mcs._validator_functions, and mcs._options.

        This function creates those attributes like this:

        ``mcs._fields`` is list of fields that are Schematics types
        ``mcs._serializables`` is a list of ``Serializable`` objects
        ``mcs._validator_functions`` are class-level validation functions
        ``mcs._options`` is the end result of parsing the ``Options`` class
        """

        # Structures used to accumulate meta info
        fields = OrderedDict()
        serializables = {}
        validator_functions = {}  # Model level

        # Accumulate metas info from parent classes
        for base in reversed(bases):
            if hasattr(base, '_fields'):
                fields.update(deepcopy(base._fields))
            if hasattr(base, '_serializables'):
                serializables.update(deepcopy(base._serializables))
            if hasattr(base, '_validator_functions'):
                validator_functions.update(base._validator_functions)

        # Parse this class's attributes into meta structures
        for key, value in iteritems(attrs):
            if key.startswith('validate_') and isinstance(value, (FunctionType, classmethod)):
                validator_functions[key[9:]] = prepare_validator(value, 4)
            if isinstance(value, BaseField):
                fields[key] = value

        # Parse meta options
        options = mcs._read_options(name, bases, attrs)

        # Convert list of types into fields for new klass
        #fields.sort(key=lambda i: i[1]._position_hint)
        for key, field in iteritems(fields):
            attrs[key] = FieldDescriptor(key)
        for key, serializable in iteritems(serializables):
            attrs[key] = serializable

        # Ready meta data to be klass attributes
        attrs['_fields'] = fields
        attrs['_field_list'] = list(fields.items())
        attrs['_serializables'] = serializables
        attrs['_validator_functions'] = validator_functions
        attrs['_options'] = options

        klass = type.__new__(mcs, name, bases, attrs)
        #klass = str_compat(klass)

        # Register class on ancestor models
        klass._subclasses = []
        for base in klass.__mro__[1:]:
            if isinstance(base, ModelMeta):
                base._subclasses.append(klass)

        # Finalize fields
        # for field_name, field in fields.items():
        #     field._setup(field_name, klass)
        # for field_name, field in serializables.items():
        #     field._setup(field_name, klass)

        # klass._valid_input_keys = (
        #     set(itertools.chain(*(field.get_input_keys() for field in fields.values())))
        #   | set(serializables))

        return klass

    @classmethod
    def _read_options(mcs, name, bases, attrs):
        """
        Parses `ModelOptions` instance into the options value attached to
        `Model` instances.
        """
        options_members = {}

        for base in reversed(bases):
            if hasattr(base, "_options"):
                for key, value in inspect.getmembers(base._options):
                    if not key.startswith("_") and not key == "klass":
                        options_members[key] = value

        options_class = attrs.get('__optionsclass__', ModelOptions)
        if 'Options' in attrs:
            for key, value in inspect.getmembers(attrs['Options']):
                if not key.startswith("_"):
                    if key == "roles":
                        roles = options_members.get("roles", {}).copy()
                        roles.update(value)

                        options_members["roles"] = roles
                    else:
                        options_members[key] = value

        return options_class(mcs, **options_members)

    @property
    def fields(cls):
        return cls._fields


@metaclass(ModelMeta)
class Model(object):
    """

    """

    def __init__(self, raw_data=None, init=True, **kwargs):

        self._initial = raw_data or {}

        kwargs.setdefault('init_values', init)
        kwargs.setdefault('apply_defaults', init)

    def __iter__(self):
        return (k for k in self._fields if k in self._data)

    def keys(self):
        return list(iter(self))

    def items(self):
        return [(k, self._data[k]) for k in self]

    def values(self):
        return [self._data[k] for k in self]

    def get(self, key, default=None):
        return getattr(self, key, default)

    def __getitem__(self, name):
        if name in self._fields or name in self._serializables:
            return getattr(self, name)
        else:
            raise UnknownFieldError(self, name)

    def __setitem__(self, name, value):
        if name in self._fields:
            return setattr(self, name, value)
        else:
            raise UnknownFieldError(self, name)

    def __delitem__(self, name):
        if name in self._fields:
            return delattr(self, name)
        else:
            raise UnknownFieldError(self, name)

    def __contains__(self, name):
        return name in self._data \
            or name in self._serializables and getattr(self, name, Undefined) is not Undefined

    def __len__(self):
        return len(self._data)

    def __eq__(self, other, memo=set()):
        if self is other:
            return True
        if type(self) is not type(other):
            return NotImplemented
        key = (id(self), id(other), get_ident())
        if key in memo:
            return True
        else:
            memo.add(key)
        try:
            return self._data == other._data
        finally:
            memo.remove(key)

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        model = self.__class__.__name__
        return '<%s instance>' % model
