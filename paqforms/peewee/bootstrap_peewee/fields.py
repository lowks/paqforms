from paqforms.html import RenderableMixin
from paqforms.rest_peewee.fields import *
from paqforms.rest_peewee.fields import Choices


class QuerySelectField(QueryChoiceField, RenderableMixin):
    widget = SelectWidget()

    def __init__(self,
        caption,
        query,
        formatter = lambda model: unicode(model),
        default = None,
        required = False,
        validators = [],
    ):
        self.caption = caption
        QueryChoiceField.__init__(self,
            query,
            formatter,
            default,
            required,
            validators,
        )

class QueryMultiSelectField(QueryMultiChoiceField, RenderableMixin):
    widget = SelectWidget(multiple=True)

    def __init__(self,
        caption,
        query,
        formatter = lambda model: unicode(model),
        default = lambda: [],
        validators = [],
    ):
        self.caption = caption
        QueryMultiChoiceField.__init__(self,
            query,
            formatter,
            default,
            validators,
        )

class QueryMultiCheckboxField(QueryMultiSelectField):
    widget = MultiCheckboxWidget()


__all__ = [
    'QuerySelectField', 'QueryMultiSelectField', 'QueryMultiChoiceField',
]
