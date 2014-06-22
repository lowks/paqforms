import re

from unittest.mock import Mock
from nose.tools import assert_raises

from paqforms4.validators import *


class Test_RepeatValidator:
    def test_call(self):
        validator = RepeatValidator('password')
        master_field = Mock()
        password_field = Mock()
        repassword_field = Mock()
        master_field.fields = {
            'password': password_field,
            'repassword': repassword_field,
        }
        password_field.master = master_field
        repassword_field.master = master_field

        password_field.value = 'admin'
        repassword_field.value = 'admin'
        validator(repassword_field)

        password_field.value = 'admin'
        repassword_field.value = 'root'
        assert_raises(ValidationError, validator, repassword_field)


class Test_LengthValidator:
    def test_call_no_args(self):
        """
        Behavior of strings and lists is identical
        'xyz' <=> ['x', 'y', 'z']
        """
        validator = LengthValidator()
        field = Mock()

        field.value = ''
        validator(field)

        field.value = 'x'
        validator(field)

    def test_call_min(self):
        validator = LengthValidator(min=1)
        field = Mock()

        field.value = ''
        assert_raises(ValidationError, validator, field)

        field.value = 'x'
        validator(field)

        field.value = 'xy'
        validator(field)

    def test_call_max(self):
        validator = LengthValidator(max=1)
        field = Mock()

        field.value = ''
        validator(field)

        field.value = 'x'
        validator(field)

        field.value = 'xy'
        assert_raises(ValidationError, validator, field)

    def _test_call_min_and_max(self):
        validator = LengthValidator(min=1, max=2)
        assert_raises(ValidationError, validator, '')
        validator('x')
        validator('xy')
        assert_raises(ValidationError, validator, 'xyz')

    def _test_call_min_and_max_invalid(self):
        validator = LengthValidator(min=2, max=1)
        assert_raises(ValidationError, validator, '')
        assert_raises(ValidationError, validator, 'x')
        assert_raises(ValidationError, validator, 'xy')
        assert_raises(ValidationError, validator, 'xyz')

    def _test_call_exact(self):
        validator = LengthValidator(exact=2)
        assert_raises(ValidationError, validator, '')
        assert_raises(ValidationError, validator, 'x')
        validator('xy')
        assert_raises(ValidationError, validator, 'xyz')

    def _test_call_min_and_max_as_exact(self):
        validator = LengthValidator(min=2, max=2)
        assert_raises(ValidationError, validator, '')
        assert_raises(ValidationError, validator, 'x')
        validator('xy')
        assert_raises(ValidationError, validator, 'xyz')

class _Test_ValueValidator:
    def test_call_no_args(self):
        validator = ValueValidator()
        validator(0)
        validator(1)
        validator(2)
        validator(3)

    def test_call_min(self):
        validator = ValueValidator(min=1)
        assert_raises(ValidationError, validator, 0)
        validator(1)
        validator(2)
        validator(3)

    def test_call_max(self):
        validator = ValueValidator(max=2)
        validator(0)
        validator(1)
        validator(2)
        assert_raises(ValidationError, validator, 3)

    def test_call_min_and_max(self):
        validator = ValueValidator(min=1, max=2)
        assert_raises(ValidationError, validator, 0)
        validator(1)
        validator(2)
        assert_raises(ValidationError, validator, 3)

    def test_call_min_and_max_invalid(self):
        validator = ValueValidator(min=2, max=1)
        assert_raises(ValidationError, validator, 0)
        assert_raises(ValidationError, validator, 1)
        assert_raises(ValidationError, validator, 2)
        assert_raises(ValidationError, validator, 3)

    def test_call_exact(self):
        validator = ValueValidator(exact=2)
        assert_raises(ValidationError, validator, 0)
        assert_raises(ValidationError, validator, 1)
        validator(2)
        assert_raises(ValidationError, validator, 3)

    def test_call_min_and_max_as_exact(self):
        validator = ValueValidator(min=2, max=2)
        assert_raises(ValidationError, validator, 0)
        assert_raises(ValidationError, validator, 1)
        validator(2)
        assert_raises(ValidationError, validator, 3)

class _Test_RegexValidator:
    def test_compiled_regex_fails(self):
        # compiled regex can not be deepcopied
        assert_raises(TypeError, lambda: RegexValidator(re.compile(r'^\d+$')))

    def test_call(self):
        validator = RegexValidator(r'^\d+$')
        assert_raises(ValidationError, validator, r'')
        validator(r'123')
        assert_raises(ValidationError, validator, r'abc')
        assert_raises(ValidationError, validator, r'123-abc')
        validator = RegexValidator(r'^.$')
        assert_raises(ValidationError, validator, r'')
        validator(r'1')
        validator(r'a')
        assert_raises(ValidationError, validator, r'12')
        assert_raises(ValidationError, validator, r'ab')

class _Test_EmailValidator:
    def test_call(self):
        validator = EmailValidator()
        validator(r'test@domain')
        validator(r'test@domain.com')
        validator(r'test-with-dash@domain.com')
        validator(r'test+with+plus@domain.com')
        validator(r'test_with_underscore@domain.com')
        validator(r'test.with.dot@domain.com')
        validator(r'test-with@very.long.domain.name')
        assert_raises(ValidationError, validator, r'test#with#hash@domain.com')
        assert_raises(ValidationError, validator, r'test/with/slash@domain.com')
        assert_raises(ValidationError, validator, r'test with space@domain.com')
        assert_raises(ValidationError, validator ,r'test @ with @ multi @ @domain.com')

class _Test_OneOfValidator:
    def test_call(self):
        validator = OneOfValidator(['spb', 'msk'])
        validator('msk')
        validator('spb')
        assert_raises(ValidationError, validator, 'xyz')
        assert_raises(Exception, validator, ['msk'])
        assert_raises(Exception, validator, {'msk'})
        assert_raises(Exception, validator, ('msk',))













'''
class _Test_OneOfModelsValidator:
    def test_call(self):
        validator = OneOfModelsValidator([{'id': 1}, {'id': 2}])
        validator({'id': 1})
        validator({'id': 2})
        assert_raises(ValidationError, validator, {'id': 3})
        assert_raises(Exception, validator, ['id'])
        assert_raises(Exception, validator, {'id'})
        assert_raises(Exception, validator, ('id',))

class _Test_ValidatorValidator:
    def test_call(self):
        validator = ValidatorValidator(LengthValidator(exact=1))
        validator(['a', 'b', 'c'])
        validator([['x'], ['x'], ['x']])
        assert_raises(ValidationError, validator, ['a', 'b', 'cc'])
        assert_raises(ValidationError, validator, ['a', '', 'c'])
        assert_raises(ValidationError, validator, [['x'], ['x'], ['x', 'x']])
        assert_raises(ValidationError, validator, [['x'], [], ['x']])
'''