from tags.metatags import MetaTitle, MetaDescription, MetaKeywords
from tags.models import Model

class SimpleModel(Model):
    title = MetaTitle(strict=False)
    description = MetaDescription(strict=False)
    keywords = MetaKeywords(strict=False)
    title2 = MetaTitle(strict=False, name='title2')



def test_model():
    obj = SimpleModel(title='QWERTY111', description='ASDSAD', keywords='keywords', title2='TITLE@')
    print(obj.title.as_dict())
    print('+'*99, obj.validate())
    print(obj.as_dict())

    print('==='*99)

    obj1 = SimpleModel(title='23', description='34', keywords='23', title2='34@')

    print('*' * 99, obj1.validate())
    print(obj1.as_dict())

    print('===' * 99)

    print('*' * 99, obj.validate())
    print(obj.as_dict())

