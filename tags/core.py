import json
import warnings
import inspect


class BaseTag(object):
    def __init__(self, name: str, max_length: int = 0, min_length: int = 0,
                 value: str = None, strict=False, required=False,
                 html_template=None, **kwargs):
        """
        :param name:
        :param max_length:
        :param min_length:
        :param value:
        :param strict:
        :param required:
        :param kwargs:

        strict - flag to validate value by max_length and min_length if it's set
        max_length - maximum char length of value
        min_length - minimum char length of value
        """
        self.name = name
        self.max_length = max_length
        self.min_length = min_length
        self.strict = strict
        self.required = required
        self.value = value
        self.html_template = html_template
        # Make validation
        self.validate()

    def __str__(self):
        return self.value

    def validate(self):
        # overwrite this method if you wanna add an a custom validation
        return

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, n):
        if not n:
            raise AttributeError('name is required!')
        self._name = n

    @property
    def max_length(self):
        return self._max_length

    @max_length.setter
    def max_length(self, m):
        try:
            self._max_length = int(m)
        except ValueError:
            raise ValueError('max_length must be int!')

    @property
    def min_length(self):
        return self._min_length

    @min_length.setter
    def min_length(self, m):
        try:
            self._min_length = int(m)
        except ValueError:
            raise ValueError('min_length must be int!')

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        if not v and self.required:
            raise ValueError('{name} is required'.format(name=self.name))
        v = str(v)
        v_len = len(v)
        if not self.max_length >= v_len >= self.min_length:
            message = '''
            {name} value length must be
            gte {min} and lte {max}, current: {cur}
            ''' .format(
                name=self.name,
                min=self.min_length,
                max=self.max_length,
                cur=v_len
            )
            if self.strict:
                raise ValueError(message)
            else:
                warnings.warn(message)
        self._value = v

    @property
    def html_template(self):
        return self._html_tempate

    @html_template.setter
    def html_template(self, h):
        if h:
            try:
                self._html_tempate = h.format(value=self.value)
            except KeyError:
                raise KeyError("""
                your html_template should contain the key name.
                For example: '<title>{value}</title>'""")
        else:
            self._html_tempate = ''

    @property
    def as_dict(self):
        return {self.name: self.value}

    @property
    def as_json(self):
        return json.dumps(self.as_dict)

    @property
    def as_html(self):
        return self.html_template

class BaseBundle(object):

    name = None
    fields = ()

    def as_html(self):
        return ''.join([s.as_html for s in self.fields])
