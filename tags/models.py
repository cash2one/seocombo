import json
from collections import OrderedDict



class Model(object):

    def __init__(self, label=None, **kwargs):
        self._fields = None
        self.label = label
        self.fields = OrderedDict()

        if self._fields is None:
            fields = OrderedDict()
            for name in dir(self):
                if not name.startswith('_'):
                    unbound_field = getattr(self, name)
                    if hasattr(unbound_field, '_modelfield'):
                        fields[name] = unbound_field
            self._fields = fields

        self.__init_fields__(**kwargs)

        self.__init_fields__(**kwargs)

    def __init_fields__(self, **kwargs):
        for k, v in kwargs.items():
            if self.fields.get(k, None):
                self.fields[k].__setattr__('value', v)

    @property
    def fields(self):
        return self._fields

    @fields.setter
    def fields(self, fields):
        pass

    def validate(self):
        for f, v in self.fields.items():
            try:
                v.validate()
            except ValueError as e:
                raise e


    def as_dict(self):
        result = OrderedDict()
        for f, v in self.fields.items():
            v.validate()
            result.update(v.as_dict())
        return result

    def as_json(self):
        return json.dumps(self.as_dict())

    def as_html(self, pretty=False):
        result = ''
        for f, v in self.fields.items():
            v.validate()
            result+=v.as_html()
            if pretty: result+='\n'
        return result


