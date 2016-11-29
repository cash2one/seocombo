from tags.models import Model
from tags import fields

class SimpleModel(Model):
    name = fields.BaseCharField(name='name')


def test_model():
    obj = SimpleModel(name='qwerty')
    print(obj.name.as_dict)
    print(obj._fields)