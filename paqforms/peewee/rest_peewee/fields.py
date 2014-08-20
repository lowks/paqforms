#encoding: utf8
import peewee

from paqforms.converters import MapConverter
from paqforms.validators import RequiredValidator
from paqforms.rest_peewee.converters import ModelConverter
from paqforms.rest.fields import ChoiceField, MultiChoiceField


class Choices(object):
    def __init__(self, query, formatter):
        self.query = query
        self.formatter = formatter

    def __iter__(self):
        self.query._dirty = True
        yield (None, u'')
        for model in self.query:
            yield model, self.formatter(model)

class QueryChoiceField(ChoiceField):
    def __init__(self,
        query,
        formatter = lambda model: unicode(model),
        default = None,
        required = False,
        validators = [RequiredValidator()],
        name = None,
        autovalidate = True
    ):
        ChoiceField.__init__(self,
            Choices(query, formatter), ModelConverter(query), default, required, validators, name, autovalidate
        )

class QueryMultiChoiceField(MultiChoiceField):
    def __init__(self,
        query,
        formatter = lambda model: unicode(model),
        default = lambda: [],
        validators = [],
        name = None,
        autovalidate = True
    ):
        MultiChoiceField.__init__(self,
            Choices(query, formatter), MapConverter(ModelConverter(query)), default, validators, name, autovalidate
        )


__all__ = [
    'QueryChoiceField', 'QueryMultiChoiceField',
]
