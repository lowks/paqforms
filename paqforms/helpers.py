from copy import copy
from collections import MutableMapping


def xhasattr(model, name):
    if isinstance(model, MutableMapping):
        return name in model
    else:
        return hasattr(model, name)


def xgetattr(model, name, default=None):
    if callable(default):
        default = default()
    if isinstance(model, MutableMapping):
        return model.get(name, default)
    else:
        return getattr(model, name, default)


def xsetattr(model, name, value):
    if isinstance(model, MutableMapping):
        model[name] = value
    else:
        setattr(model, name, value)


def variable_decode(d, dict_char='.', list_char='-'):
    """
    Decode the flat dictionary d into a nested structure.

    Patch by Ivan Kleshnin:
        1) Add "multi=True" to deal with "multicheckbox problem"
        2) Remove Python 2.4 support code

    (c) Ian Bicking
    """
    result = {}
    dicts_to_sort = set()
    known_lengths = {}
    for key, value in d.items(multi=True):
        keys = key.split(dict_char)
        new_keys = []
        was_repetition_count = False
        for k in keys:
            if k.endswith('--repetitions'):
                k = k[:-len('--repetitions')]
                new_keys.append(k)
                known_lengths[tuple(new_keys)] = int(value)
                was_repetition_count = True
                break
            elif list_char in k:
                k, index = k.split(list_char)
                new_keys.append(k)
                dicts_to_sort.add(tuple(new_keys))
                new_keys.append(int(index))
            else:
                new_keys.append(k)
        if was_repetition_count:
            continue

        place = result
        for i in range(len(new_keys)-1):
            try:
                if not isinstance(place[new_keys[i]], dict):
                    place[new_keys[i]] = {None: place[new_keys[i]]}
                place = place[new_keys[i]]
            except KeyError:
                place[new_keys[i]] = {}
                place = place[new_keys[i]]
        if new_keys[-1] in place:
            if isinstance(place[new_keys[-1]], dict):
                place[new_keys[-1]][None] = value
            elif isinstance(place[new_keys[-1]], list):
                if isinstance(value, list):
                    place[new_keys[-1]].extend(value)
                else:
                    place[new_keys[-1]].append(value)
            else:
                if isinstance(value, list):
                    place[new_keys[-1]] = [place[new_keys[-1]]]
                    place[new_keys[-1]].extend(value)
                else:
                    place[new_keys[-1]] = [place[new_keys[-1]], value]
        else:
            place[new_keys[-1]] = value

    to_sort_list = sorted(dicts_to_sort, key=len, reverse=True)
    for key in to_sort_list:
        to_sort = result
        source = None
        last_key = None
        for sub_key in key:
            source = to_sort
            last_key = sub_key
            to_sort = to_sort[sub_key]
        if None in to_sort:
            noneVals = [(0, x) for x in to_sort.pop(None)]
            noneVals.extend(to_sort.items())
            to_sort = noneVals
        else:
            to_sort = to_sort.items()
        list(to_sort).sort()
        to_sort = [v for k, v in to_sort]
        if key in known_lengths:
            if len(to_sort) < known_lengths[key]:
                to_sort.extend(['']*(known_lengths[key] - len(to_sort)))
        source[last_key] = to_sort

    return result


def variable_encode(d, prepend='', result=None, add_repetitions=True, dict_char='.', list_char='-'):
    """
    Encode a nested structure into a flat dictionary.

    (c) Ian Bicking
    """
    if result is None:
        result = {}
    if isinstance(d, dict):
        for key, value in d.items():
            if key is None:
                name = prepend
            elif not prepend:
                name = key
            else:
                name = "%s%s%s" % (prepend, dict_char, key)
            variable_encode(value, name, result, add_repetitions,
                            dict_char=dict_char, list_char=list_char)
    elif isinstance(d, list):
        for i, value in enumerate(d):
            variable_encode(value, "%s%s%i" % (prepend, list_char, i), result,
                add_repetitions, dict_char=dict_char, list_char=list_char)
        if add_repetitions:
            repName = ('%s--repetitions' % prepend
                if prepend else '__repetitions__')
            result[repName] = str(len(d))
    else:
        result[prepend] = d
    return result


def form_encode(data):
    data = variable_encode(data)
    for key, value in data.items():
        if value is None:
            data[key] = ''
        elif value is False:
            data[key] = '0'
        elif value is True:
            data[key] = '1'
        elif hasattr(value, 'id'):
            data[key] = value.id
        else:
            data[key] = str(value)
    return data


__all__ = (
    'xhasattr', 'xgetattr', 'xsetattr',
    'variable_decode', 'variable_encode', 'form_encode',
)
