from .fields import BaseCharField


class MetaTitle(BaseCharField):
    _html_template = '<title>{value}</title>'

    def __init__(self, value, html_template: str = None, strict: bool = False,
                 required: bool = True, **kwargs):
        if html_template:
            self._html_template = html_template
        super().__init__(name='title', max_length=80, min_length=50,
                         value=value, strict=strict, required=required,
                         html_template=self._html_template, **kwargs)


class MetaDescription(BaseCharField):
    _html_template = '<meta name="description" content="{value}"/>'

    def __init__(self, value, html_template: str = None, strict: bool = False,
                 required: bool = True, **kwargs):
        if html_template:
            self._html_template = html_template
        super().__init__(name='description', max_length=250, min_length=150,
                         value=value, strict=strict, required=required,
                         html_template=self._html_template, **kwargs)


class MetaKeywords(BaseCharField):
    _html_template = '<meta name="keywords" content="{value}"/>'

    def __init__(self, value, html_template: str = None, strict: bool = False,
                 required: bool = False, **kwargs):
        if html_template:
            self._html_template = html_template
        super().__init__(name='keywords', max_length=150, min_length=50,
                         value=value, strict=strict, required=required,
                         html_template=self._html_template, **kwargs)
