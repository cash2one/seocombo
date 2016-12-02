import json
from collections import OrderedDict
from itertools import chain


class MetaModel(type):
    def __new__(cls, name, bases, attrs):
        super_new = super(MetaModel, cls).__new__

        fields = {}
        for name in list(attrs.keys())[:]:
            if not name.startswith('_'):
                v = attrs[name]
                if hasattr(v, '_modelfield'):
                    field = attrs.pop(name)
                    fields[name] = field

        parents = [b for b in bases if isinstance(b, MetaModel)]
        if not parents:
            return super_new(cls, name, bases, attrs)

        module = attrs.pop('__module__')
        new_class = super_new(cls, name, bases, {'__module__': module})

        new_class.fields = fields
        for i in attrs:
            setattr(new_class, i, attrs[i])

        return new_class


class Model(object, metaclass=MetaModel):
    def __init__(self, label=None, **kwargs):
        self.label = label
        self.values = {}
        # self.fields = None

        # if self.fields is None:
        #     fields = OrderedDict()
        #     for name in dir(self):
        #         if not name.startswith('_'):
        #             unbound_field = getattr(self, name)
        #             if hasattr(unbound_field, '_modelfield'):
        #                 fields[name] = unbound_field
        #     self.fields = fields

        self.init_fields(**kwargs)

    def __getattr__(self, item):
        try:
            return getattr(self, item)
        except:
            return self.fields[item].__class__(self.values[item])

    def __setattr(self, key, value):
        field = self.fields.get(key, None)
        if field:
            self.values[key] = field.sanitize(value)

    def __getattr(self, item):
        if item in self.values:
            return self.values[item]

    def init_fields(self, **kwargs):
        print(kwargs, '//'*10)
        for k, v in kwargs.items():
            # setattr(self, k, v)
            self.__setattr(k, v)

    def validate(self):
        for f, v in self.fields.items():
            try:
                # v.validate()
                pass
            except ValueError as e:
                raise e

    def as_dict(self):
        # result = OrderedDict()
        # print('**' * 10, [(k,v.value) for k,v in self.fields.items()])
        # for f, v in self.fields.items():
        #     v.validate()
        #     result.update(v.as_dict())
        return self.values

    def as_json(self):
        return json.dumps(self.as_dict())

    def as_html(self, pretty=False):
        result = ''
        for f, v in self.fields.items():
            v.validate()
            result+=v.as_html()
            if pretty: result+='\n'
        return result


