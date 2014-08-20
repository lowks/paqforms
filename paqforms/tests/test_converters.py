import datetime
import decimal
from nose.tools import assert_raises

from paqforms.converters import *


class _Test_StrConverter:
    """
    Parser only strips the spaces
    Formatter does essentially nothing
    """
    def __init__(self):
        self.converter = StrConverter()


    def test_parse_accepts(self):
        assert self.converter.parse(' ') is None
        assert self.converter.parse(' xyz ') == 'xyz'
        assert self.converter.parse(1) == '1'
        assert self.converter.parse(1.0) == '1.0'
        assert self.converter.parse([]) == '[]'
        assert self.converter.parse({}) == '{}'
        assert self.converter.parse(None) is None


    def test_format(self):
        assert self.converter.format('') == ''
        assert self.converter.format(' ') == ' '
        assert self.converter.format('xyz') == 'xyz'
        assert self.converter.format(' xyz ') == ' xyz '


class _Test_BoolConverter:
    def __init__(self):
        self.converter = BoolConverter()


    def test_parse_accepts(self):
        assert self.converter.parse(True) == True
        assert self.converter.parse(False) == False
        assert self.converter.parse('1') == True
        assert self.converter.parse('0') == False
        assert self.converter.parse(1) == True
        assert self.converter.parse(0) == False
        assert self.converter.parse(None) is None


    def test_parse_rejects(self):
        assert_raises(TypeError, self.converter.parse, 1.0)
        assert_raises(ValueError, self.converter.parse, 2)
        assert_raises(TypeError, self.converter.parse, [])
        assert_raises(TypeError, self.converter.parse, {})


class _Test_IntConverter:
    def __init__(self):
        self.converter = IntConverter()


    def test_parse_accepts(self):
        assert self.converter.parse(0) == 0
        assert self.converter.parse(-1) == -1
        assert self.converter.parse(1) == 1
        assert self.converter.parse(1.4) == 1
        assert self.converter.parse(1.5) == 2
        assert self.converter.parse('0', 'en') == 0
        assert self.converter.parse('0', 'ru') == 0
        assert self.converter.parse('1000', 'en') == 1000
        assert self.converter.parse('1000', 'ru') == 1000
        assert self.converter.parse('-1000', 'en') == -1000
        assert self.converter.parse('-1000', 'ru') == -1000
        assert self.converter.parse('1,000', 'en') == 1000
        assert self.converter.parse('1 000', 'ru') == 1000 # nobr space
        assert self.converter.parse('1 000', 'ru') == 1000 # space
        assert self.converter.parse('-1,000', 'en') == -1000
        assert self.converter.parse('-1 000', 'ru') == -1000
        assert self.converter.parse(None, 'ru') is None


    def test_parse_rejects(self):
        assert_raises(ValueError, self.converter.parse, '1d')
        assert_raises(TypeError, self.converter.parse, [])
        assert_raises(TypeError, self.converter.parse, {})


    def test_format(self):
        assert self.converter.format(0, 'en') == '0'
        assert self.converter.format(0, 'ru') == '0'
        assert self.converter.format(1000, 'en') == '1,000'
        assert self.converter.format(1000, 'ru') == '1 000'
        assert self.converter.format(-1000, 'en') == '-1,000'
        assert self.converter.format(-1000, 'ru') == '-1 000'


class _Test_FloatConverter:
    def __init__(self):
        self.converter = FloatConverter()


    def test_parse_accepts(self):
        assert self.converter.parse(0.1) == 0.1
        assert self.converter.parse(-1.1) == -1.1
        assert self.converter.parse(1.1) == 1.1
        assert self.converter.parse('0', 'en') == 0.0
        assert self.converter.parse('0', 'ru') == 0.0
        assert self.converter.parse('1000.02', 'en') == 1000.02
        assert self.converter.parse('1000.02', 'ru') == 1000.02
        assert self.converter.parse('-1000.02', 'en') == -1000.02
        assert self.converter.parse('-1000.02', 'ru') == -1000.02
        assert self.converter.parse('1,000.02', 'en') == 1000.02
        assert self.converter.parse('1 000.02', 'ru') == 1000.02 # nobr space
        assert self.converter.parse('1 000.02', 'ru') == 1000.02 # space
        assert self.converter.parse('-1,000.02', 'en') == -1000.02
        assert self.converter.parse('-1 000.02', 'ru') == -1000.02
        assert self.converter.parse(None, 'ru') is None


    def test_parse_rejects(self):
        assert_raises(ValueError, self.converter.parse, '1.0d')
        assert_raises(TypeError, self.converter.parse, [])
        assert_raises(TypeError, self.converter.parse, {})


    def test_format(self):
        assert self.converter.format(0.0, 'en') == '0'
        assert self.converter.format(0.0, 'ru') == '0'
        assert self.converter.format(1000.02, 'en') == '1,000.02'
        assert self.converter.format(1000.02, 'ru') == '1 000,02'
        assert self.converter.format(-1000.02, 'en') == '-1,000.02'
        assert self.converter.format(-1000.02, 'ru') == '-1 000,02'


class _Test_DecimalConverter:
    def __init__(self):
        self.converter = DecimalConverter()


    def test_parse_accepts(self):
        assert self.converter.parse(decimal.Decimal('0.1')) == decimal.Decimal('0.1')
        assert self.converter.parse(decimal.Decimal('-1.1')) == decimal.Decimal('-1.1')
        assert self.converter.parse(decimal.Decimal('1.1')) == decimal.Decimal('1.1')
        assert self.converter.parse(125) == decimal.Decimal(125)
        assert self.converter.parse(125.5) == decimal.Decimal(125.5)
        assert self.converter.parse('0', 'en') == decimal.Decimal(0)
        assert self.converter.parse('0', 'ru') == decimal.Decimal(0)
        assert self.converter.parse('1000.02', 'en') == decimal.Decimal('1000.02')
        assert self.converter.parse('1000.02', 'ru') == decimal.Decimal('1000.02')
        assert self.converter.parse('-1000.02', 'en') == decimal.Decimal('-1000.02')
        assert self.converter.parse('-1000.02', 'ru') == decimal.Decimal('-1000.02')
        assert self.converter.parse('1,000.02', 'en') == decimal.Decimal('1000.02')
        assert self.converter.parse('1 000.02', 'ru') == decimal.Decimal('1000.02') # nobr space
        assert self.converter.parse('1 000.02', 'ru') == decimal.Decimal('1000.02') # space
        assert self.converter.parse('-1,000.02', 'en') == decimal.Decimal('-1000.02')
        assert self.converter.parse('-1 000.02', 'ru') == decimal.Decimal('-1000.02')
        assert self.converter.parse(None, 'ru') is None


    def test_parse_rejects(self):
        assert_raises(ValueError, self.converter.parse, '125d')
        assert_raises(TypeError, self.converter.parse, [])
        assert_raises(TypeError, self.converter.parse, {})


    def test_format(self):
        assert self.converter.format(decimal.Decimal(0), 'en') == '0'
        assert self.converter.format(decimal.Decimal(0), 'ru') == '0'
        assert self.converter.format(decimal.Decimal('1000.02'), 'en') == '1,000.02'
        assert self.converter.format(decimal.Decimal('1000.02'), 'ru') == '1 000,02'
        assert self.converter.format(decimal.Decimal('-1000.02'), 'en') == '-1,000.02'
        assert self.converter.format(decimal.Decimal('-1000.02'), 'ru') == '-1 000,02'


class _Test_DateConverter:
    def __init__(self):
        self.converter = DateConverter(coerce_to_date=True)


    def test_parse_accepts(self):
        assert self.converter.parse(datetime.datetime.now().date()) == datetime.datetime.now().date()
        assert self.converter.parse(datetime.datetime.now()) == datetime.datetime.now().date()
        assert self.converter.parse('2013-05-01', 'en') == datetime.date(2013, 5, 1)
        assert self.converter.parse('2013-05-01', 'ru') == datetime.date(2013, 5, 1)
        #assert self.converter.parse('05/01/2013', 'en') == datetime.datetime(2013, 5, 1).date()
        #assert self.converter.parse('01-05-2013', 'ru') == datetime.datetime(2013, 5, 1).date()
        assert self.converter.parse(None, 'ru') is None


    def test_parse_rejects(self):
        assert_raises(ValueError, self.converter.parse, '2013-05-zz')
        assert_raises(ValueError, self.converter.parse, '01-zz-2013', 'ru')
        assert_raises(TypeError, self.converter.parse, 1)
        assert_raises(TypeError, self.converter.parse, 1.0)
        assert_raises(TypeError, self.converter.parse, [])
        assert_raises(TypeError, self.converter.parse, {})


    def test_format(self):
        #assert self.converter.format(datetime.date(2013, 5, 1), 'en') == 'May 1, 2013'
        #assert self.converter.format(datetime.date(2013, 5, 1), 'ru') == '01 мая 2013 г.'
        assert self.converter.format(datetime.date(2013, 5, 1), 'en') == '2013-05-01'
        assert self.converter.format(datetime.date(2013, 5, 1), 'ru') == '2013-05-01'


class _Test_DateTimeConverter:
    def __init__(self):
        self.converter = DateTimeConverter()


    def test_parse_accepts(self):
        now = datetime.datetime.now()
        assert self.converter.parse(now) == now
        assert self.converter.parse(datetime.datetime.now().date()) == datetime.datetime.combine(datetime.datetime.now().date(), datetime.time())
        assert self.converter.parse('2013-05-01', 'en') == datetime.datetime(2013, 5, 1)
        assert self.converter.parse('2013-05-01', 'ru') == datetime.datetime(2013, 5, 1)
        #assert self.converter.parse('05/01/2013', 'en') == datetime.datetime(2013, 5, 1)
        #assert self.converter.parse('01-05-2013', 'ru') == datetime.datetime(2013, 5, 1)
        assert self.converter.parse(None, 'ru') is None


    def test_parse_rejects(self):
        assert_raises(ValueError, self.converter.parse, '2013-05-zz')
        assert_raises(ValueError, self.converter.parse, '01-zz-2013', 'ru')
        assert_raises(TypeError, self.converter.parse, 1)
        assert_raises(TypeError, self.converter.parse, 1.0)
        assert_raises(TypeError, self.converter.parse, [])
        assert_raises(TypeError, self.converter.parse, {})


    def test_format(self):
        #assert self.converter.format(datetime.datetime(2013, 5, 1), 'en') == 'May 1, 2013, 12:00:00 AM' # TODO: управление форматом?
        #assert self.converter.format(datetime.datetime(2013, 5, 1), 'ru') == '01 мая 2013 г., 0:00:00'  #
        assert self.converter.format(datetime.datetime(2013, 5, 1), 'en') == '2013-05-01 00:00:00'
        assert self.converter.format(datetime.datetime(2013, 5, 1), 'ru') == '2013-05-01 00:00:00'


class _Test_CutNonNumConverter:
    """
    Parser eliminates everything except digits
    Formatter does essentially nothing
    """
    def __init__(self):
        self.converter = CutNonNumConverter()


    def test_parse_accepts(self):
        assert self.converter.parse('380505573558', None) == '380505573558'
        assert self.converter.parse('+380505573558', None) == '380505573558'
        assert self.converter.parse('+38(050)5573558', None) == '380505573558'
        assert self.converter.parse('+38(050)557-3-558', None) == '380505573558'
        assert self.converter.parse('+38 (050) 557-3-558', None) == '380505573558'
        assert self.converter.parse(None) is None


    def test_parse_rejects(self):
        assert_raises(TypeError, self.converter.parse, 1)
        assert_raises(TypeError, self.converter.parse, 1.0)
        assert_raises(TypeError, self.converter.parse, [])
        assert_raises(TypeError, self.converter.parse, {})


    def test_format(self):
        assert self.converter.format('5573558', None) == '5573558'
        assert self.converter.format('505573558', None) == '505573558'
        assert self.converter.format('380505573558', None) == '380505573558'


class _Test_MapConverter:
    def test_parse_accepts(self):
        converter = MapConverter(converter=BoolConverter())
        assert converter.parse([]) == []
        assert converter.parse([True, False, True]) == [True, False, True]
        assert converter.parse(['1', '0', '1']) == [True, False, True]
        assert converter.parse([None]) == [None]

        converter = MapConverter(converter=IntConverter())
        assert converter.parse([]) == []
        assert converter.parse([1, 0, 1]) == [1, 0, 1]
        assert converter.parse(['1', '0', '1']) == [1, 0, 1]
        assert converter.parse([None]) == [None]


    def test_parse_rejects(self):
        converter = MapConverter(converter=BoolConverter())
        assert_raises(TypeError, converter.parse, [True, 0.0, 1.0])
        converter = MapConverter(converter=IntConverter())
        assert_raises(TypeError, converter.parse, [1, [], {}])


    def test_format(self):
        converter = MapConverter(converter=BoolConverter())
        assert converter.format([True, False, True]) == ['1', '0', '1']
        assert converter.format([True, False, True]) == ['1', '0', '1']
        converter = MapConverter(converter=IntConverter())
        assert converter.format([1, 0, 1]) == ['1', '0', '1']


class Test_Converters:
    def test_parse(self):
        data = 'JAC,Came,back'
        converters = [SplitConverter(delimiter=','), MapConverter(StrConverter(parse_handler=Str.lower)), MapConverter(StrConverter(parse_handler=lambda v: v[::-1]))]
        for converter in converters:
            data = converter.parse(data)
        assert data == ['JAC'.lower()[::-1], 'Came'.lower()[::-1], 'back'.lower()[::-1]]


    def test_format(self):
        value = ['jac'[::-1], 'came'[::-1], 'back'[::-1]]
        converters = [SplitConverter(delimiter=','), MapConverter(StrReverseConverter())]
        for converter in reversed(converters):
            value = converter.format(value)
        assert value == 'jac,came,back'
