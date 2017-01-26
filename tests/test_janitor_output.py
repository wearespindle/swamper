from janitor.base import BaseJanitor as Janitor


def test_fix_me_an_object():
    """
    Test building an object instance with attributes that were cleaned by the
    janitor.
    """
    data = {'name': 'janitor'}
    fields = ['name']

    class Object(object):
        name = ''

    instances = [Object()]

    janitor = Janitor(fields, data, instances=instances)
    assert janitor.errors == {}

    obj = janitor.fix_me_an(Object, ['name'])

    assert obj.name == 'janitor'
