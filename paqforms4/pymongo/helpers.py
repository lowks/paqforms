from datetime import datetime, timedelta
from ..converters import *


def get_filters(filterform, tz=None):
    filters = {}
    for name, field in filterform:
        if 'Filter' in field.__class__.__name__: # support usual fields in FilterForm`s
            if field.value.get('command'):
                command = field.value.pop('command')
                value = field.value[command]
            else:
                command = getattr(field, 'command', '')
                value = getattr(field, 'value', None)

            if command == 'contains':
                if value:
                    filters[name] = {'$regex': value, '$options': '-i'}
            elif command == 'starts_with':
                if value:
                    filters[name] = {'$regex': '^' + value, '$options': '-i'}
            elif command == 'equals':
                if value:
                    if isinstance(field.converter, DateConverter):
                        sameday = datetime(value.year, value.month, value.day, tzinfo=tz)
                        nextday = sameday + timedelta(hours=24)
                        filters[name] = {'$gte': sameday, '$lt': nextday}
                    elif isinstance(field.converter, DateTimeConverter):
                        samesec = datetime(value.year, value.month, value.day, value.hour, value.minute, value.second, tzinfo=tz)
                        nextsec = samesec + timedelta(seconds=1)
                        filters[name] = {'$gte': samesec, '$lt': nextsec}
                    else:
                        filters[name] = value
            elif command == 'not_equals':
                if value:
                    if isinstance(field.converter, DateConverter):
                        sameday = datetime(value.year, value.month, value.day, tzinfo=tz)
                        nextday = sameday + timedelta(hours=24)
                        filters.setdefault('$or', []).extend(
                            [{name: {'$lt': sameday}}, {name: {'$gte': nextday}}]
                        )
                    elif isinstance(field.converter, DateTimeConverter):
                        samesec = datetime(value.year, value.month, value.day, value.hour, value.minute, value.second, tzinfo=tz)
                        nextsec = samesec + timedelta(seconds=1)
                        filters.setdefault('$or', []).extend(
                            [{name: {'$lt': samesec}}, {name: {'$gte': nextsec}}]
                        )
                    else:
                        filters[name] = {'$ne': value}
            elif command == 'empty':
                if value: # checked (True)
                    filters[name] = {'$ne': None}
                else:     # unchecked (False)
                    filters[name] = None
            elif command == 'between':
                if isinstance(field.fields['min'].converter, DateConverter):
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
                elif isinstance(field.fields['min'].converter, DateTimeConverter):
                    if value['min'] and value['max']:
                        filters[name] = {'$gte': value['min'], '$lte': value['max']}
                    elif value['min']:
                        filters[name] = {'$gte': value['min']}
                    elif value['max']:
                        filters[name] = {'$lte': value['max']}
                else:
                    if (value['min'] or value['min'] == 0) and (value['max'] or value['max'] == 0):
                        filters[name] = {'$gte': value['min'], '$lte': value['max']}
                    elif (value['min'] or value['min'] == 0):
                        filters[name] = {'$gte': value['min']}
                    elif (value['max'] or value['max'] == 0):
                        filters[name] = {'$lte': value['max']}
        elif hasattr(field, 'converter') and isinstance(field.converter, BoolConverter):
            value = field.value
            if value is not None:
                filters[name] = value
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