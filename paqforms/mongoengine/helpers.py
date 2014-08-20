from ..pymongo import get_filters


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
