from datetime import datetime, timedelta
from mongoengine import StringField, BooleanField, IntField, FloatField, DecimalField

from ..converters import *
from ..pymongo.helpers import value_to_query


def get_filters(filterform, model_class, tz=None):
    filters = {}
    model_fields = model_class._fields
    for name, field in filterform:
        if field.__class__.__name__.startswith('Filter'):
            command = field.value['command']
            if command:
                value = field.value[command]
                # crappy logic before PaqForms5
                if len(field.shared.get('converters', [])) == 1:
                    value_to_query(field.shared.get('converters')[0], command, name, value, filters)
        elif field.__class__.__name__.startswith('Between'):
            # crappy logic before PaqForms5
            if len(field.shared.get('converters', [])) == 1:
                value_to_query(field.shared.get('converters')[0], 'between', name, field.value, filters)
        elif model_fields.get(name) and isinstance(model_fields[name], (StringField, BooleanField, IntField, FloatField, DecimalField)):
            if len(field.converters) == 1:
                value_to_query(field.converters[0], 'equals', name, field.value, filters)
    return filters


def get_sorts(sortform):
    sorts = []
    for name, field in sortform:
        if field.value:
            if isinstance(field.value, str):
                value = field.value.lower()
                if value == 'asc':
                    sorts.append('+' + name)
                elif value == 'desc':
                    sorts.append('-' + name)
                else:
                    raise ValueError('Invalid value {!r} for field {!r}'.format(value, field))
            else:
                raise TypeError('Invalid value type {!r} for field {!r}'.format(type(field.value), field))
    return sorts
