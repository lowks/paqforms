import decimal
import datetime
import babel.support; nt = babel.support.NullTranslations()

from collections import OrderedDict
from werkzeug.datastructures import MultiDict
from unittest.mock import Mock
from nose.tools import assert_raises

from paqforms4.converters import *
from paqforms4.helpers import *
from paqforms4.validators import *
from paqforms4.fields import *




"""
class Test_FilterStrField:
    def test_ok(self):
        form = FilterStrField(data={'contains': 'something'})
        assert form.value == {
            'contains': 'something',
            'starts_with': None,
            'equals': None,
            'not_equals': None,
            'empty': True,
        }
        assert form.ok
        assert not form.messages['error']

    def test_bad(self):
        form = FilterStrField(data={'empty': 'cracked-by-ufo'})
        assert not hasattr(form, 'value')
        assert not form.ok
        assert form.messages['error']

    def test_required(self):
        form = FilterStrField()
        assert form.value == {
            'contains': None,
            'starts_with': None,
            'equals': None,
            'not_equals': None,
            'empty': True,
        }
        assert not form.ok
        assert not form.messages['error']

class _Test_FilterIntField:
    def test_ok(self):
        form = FilterIntField(data={'equals': 42})
        assert form.value == {
            'equals': 42,
            'between': {'max': None, 'min': None},
            'empty': True,
        }
        assert form.ok
        assert not form.messages['error']

    def test_bad(self):
        form = FilterIntField(data={'empty': 'cracked-by-ufo'})
        assert not hasattr(form, 'value')
        assert not form.ok
        assert form.messages['error']

    def test_required(self):
        form = FilterIntField()
        assert form.value == {
            'equals': None,
            'between': {'max': None, 'min': None},
            'empty': True,
        }
        assert not form.ok
        assert not form.messages['error']

class _Test_FloatFilterField:
    def test_ok(self):
        form = FloatFilterField(data={'equals': 42.0})
        assert form.value == {
            'equals': 42.0,
            'between': {'max': None, 'min': None},
            'empty': True,
        }
        assert form.ok
        assert not form.messages['error']

    def test_bad(self):
        form = FloatFilterField(data={'empty': 'cracked-by-ufo'})
        assert not hasattr(form, 'value')
        assert not form.ok
        assert form.messages['error']

    def test_required(self):
        form = FloatFilterField()
        assert form.value == {
            'equals': None,
            'between': {'max': None, 'min': None},
            'empty': True,
        }
        assert not form.ok
        assert not form.messages['error']

class _Test_DecimalFilterField:
    def test_ok(self):
        form = DecimalFilterField(data={'equals': decimal.Decimal(42.0)})
        assert form.value == {
            'equals': decimal.Decimal(42.0),
            'between': {'max': None, 'min': None},
            'empty': True,
        }
        assert form.ok
        assert not form.messages['error']

    def test_bad(self):
        form = DecimalFilterField(data={'empty': 'cracked-by-ufo'})
        assert not hasattr(form, 'value')
        assert not form.ok
        assert form.messages['error']

    def test_required(self):
        form = DecimalFilterField()
        assert form.value == {
            'equals': None,
            'between': {'max': None, 'min': None},
            'empty': True,
        }
        assert not form.ok
        assert not form.messages['error']

class _Test_DateFilterField:
    def test_ok(self):
        form = DateFilterField(data={'between': {'min': '1999-01-01'}})
        assert form.value == {
            'equals': None,
            'between': {'min': datetime.date(1999, 1, 1), 'max': None},
            'empty': True,
        }
        assert form.ok
        assert not form.messages['error']

    def test_bad(self):
        pass # TODO

    def test_required(self):
        pass # TODO

class _Test_DateTimeFilterField:
    def test_ok(self):
        form = DateTimeFilterField(data={'between': {'max': '1999-01-01'}})
        assert form.value == {
            'equals': None,
            'between': {'min': None, 'max': datetime.datetime(1999, 1, 1)},
            'empty': True,
        }
        assert form.ok
        assert not form.messages['error']

    def test_bad(self):
        pass # TODO

    def test_required(self):
        pass # TODO

class LoginForm(Form):
    username = FieldStr(validators=[LengthValidator(min=1)])
    password = FieldStr(validators=[LengthValidator(min=4)])


class Test_Form:
    def test_create_demo_valid(self):
        model = {'role': 'admin'}
        data = {'username': 'root', 'password': 'root'}
        form = LoginForm(model=model, data=data)
        assert form.ok
        model = form.value
        assert model == {
            'role': 'admin',
            'username': 'root',
            'password': 'root',
        }

    def test_create_demo_invalid(self):
        model = {}
        data = {'username': '', 'password': 'root'}
        form = LoginForm(model=model, data=data)
        assert not form.ok

    def test_edit_password_demo_valid(self):
        model = {
            'role': 'admin',
            'username': 'root',
            'password': 'root',
        }
        data = {'password': 'root of all evil'}
        form = LoginForm(model=model, data=data)
        assert form.ok
        model = form.value
        assert model == {
            'role': 'admin',
            'username': 'root',
            'password': 'root of all evil',
        }

    def test_edit_password_demo_invalid(self):
        model = {
            'role': 'admin',
            'username': 'root',
            'password': 'root of all evil',
        }
        data = {'password': ''}
        form = LoginForm(model=model, data=data)
        assert not form.ok
"""