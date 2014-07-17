from decimal import Decimal
from datetime import datetime, timedelta
try:
    from functools import singledispatch
except ImportError:
    from singledispatch import singledispatch

from ..converters import *


@singledispatch
def value_to_query(converter, command, name, value, filters, tz):
    pass # Do nothing (keep filters as is)


@value_to_query.register(StrConverter)
def _(converter, command, name, value, filters, tz):
    def contains(name, value, filters):
        if value:
            filters[name] = {'$regex': value, '$options': '-i'} # TODO -i breaks index support

    def starts_with(name, value, filters):
        if value:
            filters[name] = {'$regex': '^' + value, '$options': '-i'} # TODO -i breaks index support

    def equals(name, value, filters):
        filters[name] = value

    def not_equals(name, value, filters):
        filters[name] = {'$ne': value}

    def empty(name, value, filters):
        if value == 'yes':
            filters[name] = None
        elif value == 'no':
            filters[name] = {'$ne': None}

    locals()[command](name, value, filters)


@value_to_query.register(IntConverter)
@value_to_query.register(FloatConverter)
@value_to_query.register(DecimalConverter)
def _(converter, command, name, value, filters, tz):
    def equals(name, value, filters):
        filters[name] = value

    def not_equals(name, value, filters):
        filters[name] = {'$ne': value}

    def between(name, value, filters):
        if (value['min'] or value['min'] == 0) and (value['max'] or value['max'] == 0):
            filters[name] = {'$gte': value['min'], '$lte': value['max']}
        elif (value['min'] or value['min'] == 0):
            filters[name] = {'$gte': value['min']}
        elif (value['max'] or value['max'] == 0):
            filters[name] = {'$lte': value['max']}
        if 'unit' in value and value['unit']:
            filters[name + '_unit'] = value['unit']

    def empty(name, value, filters):
        if value == 'yes':
            filters[name] = None
        elif value == 'no':
            filters[name] = {'$ne': None}

    locals()[command](name, value, filters)


@value_to_query.register(DateTimeConverter)
def _(converter, command, name, value, filters, tz):
    # Treat datetime as datetime
    def equals(name, value, filters):
        if value:
            samesec = datetime(value.year, value.month, value.day, value.hour, value.minute, value.second, tzinfo=tz)
            nextsec = samesec + timedelta(seconds=1)
            filters[name] = {'$gte': samesec, '$lt': nextsec}

    def not_equals(name, value, filters):
        if value:
            samesec = datetime(value.year, value.month, value.day, value.hour, value.minute, value.second, tzinfo=tz)
            nextsec = samesec + timedelta(seconds=1)
            filters.setdefault('$or', []).extend(
                [{name: {'$lt': samesec}}, {name: {'$gte': nextsec}}]
            )

    def empty(name, value, filters):
        if value == 'yes':
            filters[name] = None
        elif value == 'no':
            filters[name] = {'$ne': None}

    def between(name, value, filters):
            if value['min'] and value['max']:
                filters[name] = {'$gte': value['min'], '$lte': value['max']}
            elif value['min']:
                filters[name] = {'$gte': value['min']}
            elif value['max']:
                filters[name] = {'$lte': value['max']}

    locals()[command](name, value, filters)


@value_to_query.register(DateConverter)
def _(converter, command, name, value, filters, tz):
    # Treat datetime as date
    def equals(name, value, filters):
        if value:
            sameday = datetime(value.year, value.month, value.day, tzinfo=tz)
            nextday = sameday + timedelta(hours=24)
            filters[name] =  {'$gte': sameday, '$lt': nextday}

    def not_equals(name, value, filters):
        if value:
            sameday = datetime(value.year, value.month, value.day, tzinfo=tz)
            nextday = sameday + timedelta(hours=24)
            filters.setdefault('$or', []).extend(
                [{name: {'$lt': sameday}}, {name: {'$gte': nextday}}]
            )

    def between(name, value, filters):
        if value['min'] and value['max']:
            minday = datetime(value['min'].year, value['min'].month, value['min'].day, tzinfo=tz)
            maxday = datetime(value['max'].year, value['max'].month, value['max'].day, tzinfo=tz)
            maxday = maxday + timedelta(days=1)
            filters[name] = {'$gte': minday, '$lt': maxday}
        elif value['min']:
            minday = datetime(value['min'].year, value['min'].month, value['min'].day, tzinfo=tz)
            filters[name] = {'$gte': minday}
        elif value['max']:
            maxday = datetime(value['max'].year, value['max'].month, value['max'].day, tzinfo=tz)
            maxday = maxday + timedelta(days=1)
            filters[name] = {'$lt': maxday}

    def empty(name, value, filters):
            if value == 'yes':
                filters[name] = None
            elif value == 'no':
                filters[name] = {'$ne': None}

    locals()[command](name, value, filters)


def get_filters(filterform, tz=None):
    filters = {}
    for name, form_field in filterform:
        if hasattr(form_field, 'prototypes'):
            if 'command' in form_field.prototypes:
                command = form_field.value['command']
                if command:
                    value_to_query(
                        form_field.meta['converter'], command, name, form_field.value[command], filters, tz
                    )
            elif 'min' in form_field.prototypes and 'max' in form_field.prototypes:
                value_to_query(
                    form_field.meta['converter'], 'between', name, form_field.value, filters, tz
                )
        elif form_field.meta.get('converter'):
            value_to_query(
                form_field.meta.get('converter'), 'equals', name, form_field.value, filters, tz
            )
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
