from random import randrange


class SimpleTemplate(object):
    def __init__(self, templates: list, keys: dict):
        """
        :param templates:
        :param keys:
        You can generate a random or a specific template from its list.
        Also, you can generate all of the templates in the list.
        """
        self.templates = templates
        self.keys = keys
        self.range = len(self.templates)

    @property
    def templates(self):
        return self._templates

    @templates.setter
    def templates(self, t):
        if not isinstance(t, (list, tuple)):
            raise TypeError("templates must be a list or tuple!")
        if not t:
            raise ValueError("templates can't be empty")
        self._templates = t

    @property
    def keys(self):
        return self._keys

    @keys.setter
    def keys(self, k):
        if not isinstance(k, dict):
            raise TypeError("keys must be a list or tuple!")
        self._keys = k

    def create(self, index: int = None):
        if index == None:
            index = randrange(self.range)
        if not 0 <= index < self.range:
            raise IndexError("element index must be in range!")
        _template = self.templates[index]
        try:
            return _template.format(**self.keys)
        except KeyError as e:
            raise KeyError("Set {key} in your keys to build template '{template}'".format(
                key=e, template=_template
            ))

    def create_all(self):
        return [self.create(index=i) for i, v in enumerate(self.templates)]
