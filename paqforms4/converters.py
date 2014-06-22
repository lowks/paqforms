import re
import decimal
import collections
import datetime
import dateutil.parser
import babel.numbers
import babel.dates


class StrConverter:
    def __init__(self, none_value=None):
        self.none_value = none_value


    def parse(self, data, locale='en'):
        if isinstance(data, str):
            data = data.strip()
            if data:
                return data
            else:
                return None
        elif data is None:
            return self.none_value() if callable(self.none_value) else self.none_value
        else:
            raise TypeError


    def format(self, value, locale='en'):
        data = '' if value is None else value
        return data


class StrLowerConverter(StrConverter):
    def parse(self, data, locale='en'):
        value = StrConverter.parse(self, data, locale)
        if isinstance(value, str):
            return value.lower()
        else:
            return value


class StrReverseConverter(StrConverter):
    def parse(self, data, locale='en'):
        value = StrConverter.parse(self, data, locale)
        if isinstance(value, str):
            return value[::-1]
        else:
            return value


    def format(self, value, locale='en'):
        if value is None:
            return ''
        else:
            return value[::-1]


class StrUpperConverter(StrConverter):
    def parse(self, data, locale='en'):
        value = StrConverter.parse(self, data, locale)
        if isinstance(value, str):
            return value.upper()


class BoolConverter:
    def __init__(self, none_value=None):
        self.none_value = none_value


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
                return None
        elif data is None:
            return self.none_value() if callable(self.none_value) else self.none_value
        else:
            raise TypeError


    def format(self, value, locale='en'):
        data = '' if value is None else str(int(value))
        return data


class IntConverter:
    def __init__(self, none_value=None):
        self.none_value = none_value


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
            return self.none_value() if callable(self.none_value) else self.none_value
        else:
            raise TypeError


    def format(self, value, locale='en'):
        data = '' if value is None else babel.numbers.format_number(value, locale=locale)
        return data


class FloatConverter:
    def __init__(self, none_value=None):
        self.none_value = none_value


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
            return self.none_value() if callable(self.none_value) else self.none_value
        else:
            raise TypeError


    def format(self, value, locale='en'):
        data = '' if value is None else babel.numbers.format_decimal(value, locale=locale)
        return data


class DecimalConverter:
    def __init__(self, none_value=None):
        self.none_value = none_value


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
            return self.none_value() if callable(self.none_value) else self.none_value
        else:
            raise TypeError


    def format(self, value, locale='en'):
        data = '' if value is None else babel.numbers.format_decimal(value, locale=locale)
        return data


class DateConverter:
    def __init__(self, none_value=None, coerce_to_date=False):
        self.none_value = none_value
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
            return self.none_value() if callable(self.none_value) else self.none_value
        else:
            raise TypeError


    def format(self, value, locale='en'):
        #data = '' if value is None else babel.dates.format_date(value, locale=locale)
        data = '' if value is None else value.strftime('%Y-%m-%d')
        return data


class DateTimeConverter:
    def __init__(self, none_value=None):
        self.none_value = none_value


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
            return self.none_value() if callable(self.none_value) else self.none_value
        else:
            raise TypeError


    def format(self, value, locale='en'):
        #data = '' if value is None else babel.dates.format_datetime(value, locale=locale)
        data = '' if value is None else value.strftime('%Y-%m-%d %H:%M:%S')
        return data


class CutNonNumConverter:
    def __init__(self, none_value=None):
        self.none_value = none_value


    def parse(self, data, locale='en'):
        if isinstance(data, str):
            if data:
                return re.subn(r'[^\d]', '', data, re.U)[0]
            else:
                return None
        elif data is None:
            return self.none_value() if callable(self.none_value) else self.none_value
        else:
            raise TypeError


    def format(self, value, locale='en'):
        data = '' if value is None else value
        return data


class SplitConverter:
    def __init__(self, none_value=lambda: [], delimiter='\n'):
        self.none_value = none_value
        self.delimiter = delimiter


    def parse(self, data, locale='en'):
        if isinstance(data, str):
            data = data.strip()
            if data:
                return data.split(self.delimiter)
            else:
                return []
        elif data is None:
            return self.none_value() if callable(self.none_value) else self.none_value
        else:
            raise TypeError


    def format(self, value, locale='en'):
        data = '' if value is None else self.delimiter.join(value)
        return data


class FilterConverter:
    def __init__(self, func=None, none_value=lambda: []):
        self.func = func
        self.none_value = none_value


    def parse(self, data, locale='en'):
        if data is None:
            return self.none_value() if callable(self.none_value) else self.none_value
        elif isinstance(data, (list, tuple)):
            result = list(filter(self.func, data))
        else:
            raise TypeError
        return result


    def format(self, value, locale='en'):
        return value


class FilterValueConverter:
    def __init__(self, func=None, none_value=lambda: []):
        self.func = func
        self.none_value = none_value


    def parse(self, data, locale='en'):
        if data is None:
            return self.none_value() if callable(self.none_value) else self.none_value
        elif isinstance(data, dict):
            if self.func:
                result = {key: value for (key, value) in data.items() if self.func(value)}
            else:
                result = {key: value for (key, value) in data.items() if value is not None}
        else:
            raise TypeError
        return result


    def format(self, value, locale='en'):
        return value


class MapConverter:
    def __init__(self, converter=None, none_value=lambda: []):
        self.converter = converter
        self.none_value = none_value


    def parse(self, data, locale='en'):
        if data is None:
            return self.none_value() if callable(self.none_value) else self.none_value
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
    'StrConverter', 'StrLowerConverter', 'StrUpperConverter', 'StrReverseConverter',
    'BoolConverter', 'IntConverter', 'FloatConverter',
    'DecimalConverter', 'DateConverter', 'DateTimeConverter', 'CutNonNumConverter',
    'SplitConverter', 'FilterConverter', 'FilterValueConverter', 'MapConverter',
)
