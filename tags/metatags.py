from .fields import BaseCharField


class MetaTitle(BaseCharField):
    _html_template = '<title>{value}</title>'
    _name = 'title'
    _min_length = 50
    _max_length = 80


    def __init__(self, value=None, html_template: str = None, strict: bool = False,
                 required: bool = True, name=None, **kwargs):
        if html_template:
            self._html_template = html_template
        if name:
            self._name = name
        super().__init__(name=self._name, min_length=self._min_length, max_length=self._max_length,
                         value=value, strict=strict, required=required,
                         html_template=self._html_template, **kwargs)


class MetaDescription(BaseCharField):
    _html_template = '<meta name="description" content="{value}"/>'

    def __init__(self, value=None, html_template: str = None, strict: bool = False,
                 required: bool = True, **kwargs):
        if html_template:
            self._html_template = html_template
        super().__init__(name='description', max_length=250, min_length=150,
                         value=value, strict=strict, required=required,
                         html_template=self._html_template, **kwargs)


class MetaKeywords(BaseCharField):
    _html_template = '<meta name="keywords" content="{value}"/>'

    def __init__(self, value=None, html_template: str = None, strict: bool = False,
                 required: bool = False, **kwargs):
        if html_template:
            self._html_template = html_template
        super().__init__(name='keywords', max_length=150, min_length=50,
                         value=value, strict=strict, required=required,
                         html_template=self._html_template, **kwargs)
