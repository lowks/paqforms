import re
import decimal
import collections
import datetime
import dateutil.parser
import babel.numbers
import babel.dates


class StrConverter:
    def __init__(self, parse_handler=None):
        self.parse_handler = parse_handler


    def parse(self, data, locale='en'):
        if isinstance(data, str):
            data = data.strip()
            if data:
                if self.parse_handler:
                    data = self.parse_handler(data)
                return data
            else:
                return None
        elif data is None:
            return None
        else:
            raise TypeError


    def format(self, value, locale='en'):
        data = '' if value is None else value
        return data


class BoolConverter:
    def __init__(self, none=None):
        self.none = none


    def parse(self, data, locale='en'):
        if isinstance(data, bool):
            return data
        elif isinstance(data, int):
            if data in {0, 1}:
                return bool(data)
            else:
                raise ValueError
        elif isinstance(data, str):
            if data:
                if (data in {'0', '1'}):
                    return bool(int(data))
                else:
                    raise ValueError
            else:
                return self.none
        elif data is None:
            return self.none
        else:
            raise TypeError


    def format(self, value, locale='en'):
        data = '' if value is None else str(int(value))
        return data


class IntConverter:
    def parse(self, data, locale='en'):
        if type(data) == int:
            return data
        elif type(data) == float:
            return int(round(data))
        elif type(data) == str:
            if data:
                data = data.strip().replace(" ", "\u00A0") # non-breaking-space (for correct number parsing)
                try:
                    return babel.numbers.parse_number(data, locale=locale)
                except Exception:
                    raise ValueError
            else:
                return None
        elif data is None:
            return None
        else:
            raise TypeError


    def format(self, value, locale='en'):
        data = '' if value is None else babel.numbers.format_number(value, locale=locale)
        return data


class FloatConverter:
    def parse(self, data, locale='en'):
        if isinstance(data, float):
            return data
        elif isinstance(data, int):
            return float(data)
        elif isinstance(data, str):
            if data:
                data = data.strip().replace(" ", "\u00A0") # non-breaking-space (for correct number parsing)
                try:
                    return float(babel.numbers.parse_decimal(data, locale=locale))
                except Exception:
                    raise ValueError
            else:
                return None
        elif data is None:
            return None
        else:
            raise TypeError


    def format(self, value, locale='en'):
        data = '' if value is None else babel.numbers.format_decimal(value, locale=locale)
        return data


class DecimalConverter:
    def parse(self, data, locale='en'):
        if isinstance(data, decimal.Decimal):
            return data
        elif isinstance(data, float):
            return decimal.Decimal(data)
        elif isinstance(data, int):
            return decimal.Decimal(data)
        elif isinstance(data, str):
            if data:
                data = data.strip().replace(" ", "\u00A0") # non-breaking-space (for correct number parsing)
                try:
                    return babel.numbers.parse_decimal(data, locale=locale)
                except Exception:
                    raise ValueError
            else:
                return None
        elif data is None:
            return None
        else:
            raise TypeError


    def format(self, value, locale='en'):
        data = '' if value is None else babel.numbers.format_decimal(value, locale=locale)
        return data


class DateConverter:
    def __init__(self, coerce_to_date=False):
        self.coerce_to_date = coerce_to_date


    def parse(self, data, locale='en'):
        if isinstance(data, datetime.datetime):
            return data.date()
        elif isinstance(data, datetime.date):
            return data
        elif isinstance(data, str):
            if data:
                #try: *** Babel not ready yet :( ***
                #    return babel.dates.parse_date(data, locale=locale)
                #except Exception:
                try:
                    value = dateutil.parser.parse(data)
                    return value.date() if self.coerce_to_date else value
                except Exception:
                    raise ValueError
            else:
                return None
        elif data is None:
            return None
        else:
            raise TypeError


    def format(self, value, locale='en'):
        #data = '' if value is None else babel.dates.format_date(value, locale=locale)
        data = '' if value is None else value.strftime('%Y-%m-%d')
        return data


class DateTimeConverter:
    def parse(self, data, locale='en'):
        if isinstance(data, datetime.datetime):
            return data
        elif isinstance(data, datetime.date):
            return datetime.datetime.combine(data, datetime.time())
        elif isinstance(data, str):
            if data:
                #try: *** Babel not ready yet :( ***
                #    if ',' in data:
                #        date_data, time_data = data.split(',')
                #        return datetime.datetime.combine(
                #            babel.dates.parse_date(date_data, locale=locale),
                #            babel.dates.parse_time(time_data, locale=locale)
                #        )
                #    else:
                #        return datetime.datetime.combine(
                #            babel.dates.parse_date(data, locale=locale),
                #            datetime.time()
                #        )
                #except Exception:
                try:
                    return dateutil.parser.parse(data)
                except Exception:
                    raise ValueError
            else:
                return None
        elif data is None:
            return None
        else:
            raise TypeError


    def format(self, value, locale='en'):
        #data = '' if value is None else babel.dates.format_datetime(value, locale=locale)
        data = '' if value is None else value.strftime('%Y-%m-%d %H:%M:%S')
        return data


class CutNonNumConverter:
    def parse(self, data, locale='en'):
        if isinstance(data, str):
            if data:
                return re.subn(r'[^\d]', '', data, re.U)[0]
            else:
                return None
        elif data is None:
            return None
        else:
            raise TypeError


    def format(self, value, locale='en'):
        data = '' if value is None else value
        return data


class SplitConverter:
    def __init__(self, delimiter='\n'):
        self.delimiter = delimiter


    def parse(self, data, locale='en'):
        if isinstance(data, str):
            data = data.strip()
            if data:
                return data.split(self.delimiter)
            else:
                return []
        elif data is None:
            return []
        else:
            raise TypeError


    def format(self, value, locale='en'):
        data = '' if value is None else self.delimiter.join(value)
        return data


class FilterConverter:
    def __init__(self, func=None):
        self.func = func


    def parse(self, data, locale='en'):
        if data is None:
            return []
        elif isinstance(data, (list, tuple)):
            result = list(filter(self.func, data))
            return result
        else:
            raise TypeError


    def format(self, value, locale='en'):
        return value


class FilterValueConverter:
    def __init__(self, func=None, nondata_keys=[]):
        self.func = func
        self.nondata_keys = nondata_keys


    def parse(self, data, locale='en'):
        if data is None:
            return []
        elif isinstance(data, dict):
            if self.func:
                result = {key: value for (key, value) in data.items() if self.func(value)}
            else:
                result = {key: value for (key, value) in data.items() if value is not None}
            if set(result) == set(self.nondata_keys):
                return {}
            else:
                return result
        else:
            raise TypeError


    def format(self, value, locale='en'):
        return value


class MapConverter:
    def __init__(self, converter=None):
        self.converter = converter


    def parse(self, data, locale='en'):
        if data is None:
            return []
        elif isinstance(data, (list, tuple)):
            if self.converter:
                result = [self.converter.parse(d, locale) for d in data]
            else:
                result = data
        else:
            raise TypeError
        return result


    def format(self, value, locale='en'):
        if value is None:
            return None
        else:
            if self.converter:
                data = [self.converter.format(v, locale) for v in value]
            else:
                data = value
            return data


__all__ = (
    'StrConverter', 'BoolConverter', 'IntConverter', 'FloatConverter',
    'DecimalConverter', 'DateConverter', 'DateTimeConverter', 'CutNonNumConverter',
    'SplitConverter', 'FilterConverter', 'FilterValueConverter', 'MapConverter',
)
