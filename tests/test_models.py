from tags.metatags import MetaTitle, MetaDescription, MetaKeywords
from tags.models import Model

class SimpleModel(Model):
    title = MetaTitle(strict=False)
    description = MetaDescription(strict=False)
    keywords = MetaKeywords(strict=False)



def test_model():
    obj = SimpleModel(title='QWERTY111', description='ASDSAD', keywords='keywords')
    obj.description = 'DESCRIPTION'
    obj.keywords = 'LET'
    print('*'*99, obj.validate())
    print(obj.title.as_dict())
    print(obj.description.as_html())
    print(obj.as_dict())
    print(obj.as_json())
    print(obj.as_html(pretty=True))