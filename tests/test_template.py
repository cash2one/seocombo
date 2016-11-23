from templates.simple import SimpleTemplate


def test_simple_template():
    templates = [
        'My doggy name is {name} with color {color}',
        'Name of my doggy is {name}',
        'Color of my doggy is {color}'
    ]
    keys = {'name':'Druzhok', 'color':'red'}
    template = SimpleTemplate(templates=templates, keys=keys)
    assert isinstance(template.create(), str)
    assert (template.create(index=0) == 'My doggy name is Druzhok with color red')
    assert (template.create(index=1) == 'Name of my doggy is Druzhok')
    assert (template.create(index=2) == 'Color of my doggy is red')
    try:
        template.create(index=3)
    except IndexError:
        assert True
    try:
        SimpleTemplate(templates=templates, keys=())
    except TypeError:
        assert True
    try:
        SimpleTemplate(templates={}, keys={})
    except TypeError:
        assert True

    assert isinstance(template.create_all(), list)
    assert len(template.create_all()) == 3