import json
import warnings

from tags.exceptions import HtmlTemplateException


class BaseField(object):
    def __init__(self, name: str, value: str = None, strict=False,
                 required=False, html_template=None, **kwargs):
        """
        :param name:
        :param value:
        :param strict:
        :param required:
        :param html_template:
        :param kwargs:

        strict - flag to raise exception, not warning for basic validation
        """
        self.name = name
        self.strict = strict
        self.required = required
        self.value = value
        self.html_template = html_template
        self._modelfield=True

    def __str__(self):
        return self.value

    def validate(self):
        # overwrite this method if you wanna add an a custom validation
        return True

    def sanitize(self, data):
        return data

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, n):
        if not n:
            raise AttributeError('name is required!')
        self._name = n

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = v

    def as_dict(self):
        return {self.name: self.value}

    def as_json(self):
        return json.dumps(self.as_dict)

    def as_html(self):
        try:
            return self.html_template.format(value=self.value)
        except (KeyError, AttributeError):
            raise HtmlTemplateException(message="""your html_template should contain the key name.For example: '<title>{value}</title>'""")


class BaseCharField(BaseField):
    def __init__(self, name: str, value: str = None, strict=False,
                 min_length: int = 0, max_length: int = 255 * 1000,
                 required=False, html_template=None, **kwargs):

        self.min_length = min_length
        self.max_length = max_length

        super().__init__(name, value, strict, required, html_template, **kwargs)

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

    def validate(self):
        if not self.value and self.required:
            raise ValueError('{name} is required'.format(name=self.name))
        v = str(self.value)
        v_len = len(v)
        if not self.max_length >= v_len >= self.min_length:
            message = '''
            {name} value length must be
            gte {min} and lte {max}, current: {cur}
            '''.format(
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
        return True

class BaseIntField(BaseField):
    def __init__(self, name: str, value: str = None, strict=False,
                 min_value: int = 0, max_value: int = 255 * 1000,
                 required=False, html_template=None, **kwargs):

        self.min_value = min_value
        self.max_value = max_value

        super().__init__(name, value, strict, required, html_template, **kwargs)

    @property
    def max_value(self):
        return self._max_value

    @max_value.setter
    def max_value(self, m):
        try:
            self._max_value = int(m)
        except ValueError:
            raise ValueError('max_value must be int!')

    @property
    def min_value(self):
        return self._min_value

    @min_value.setter
    def min_value(self, m):
        try:
            self._min_value = int(m)
        except ValueError:
            raise ValueError('min_value must be int!')

    def validate(self):
        if not self.value and self.required:
            raise ValueError('{name} is required'.format(name=self.name))
        try:
            v = int(self.value)
        except ValueError:
            raise ValueError('min_value must be int!')
        if not self.max_value >= v >= self.min_value:
            message = '''
            {name} value must be
            gte {min} and lte {max}, current: {cur}
            '''.format(
                name=self.name,
                min=self.min_value,
                max=self.max_value,
                cur=v
            )
            if self.strict:
                raise ValueError(message)
            else:
                warnings.warn(message)
        self._value = v
        return True