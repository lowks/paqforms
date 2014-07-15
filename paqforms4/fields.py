"""
.fields can be created ONLY in feed (not in __init__):
    FieldField will contain different number of nested fields
    depending on input.

Следует различать внутренее представление данных в полях формы и данные, которые приходят из формы.
Внутреннее представление полей обычного и булевского ввода совпадает с тем, что используется в повседневном
python-коде. Например, для булевских полей это True / False, для полей дат — `datetime` объект,
для полей ввода текста — юникод. В полях множественного ввода данные приводятся к юникоду,
даже если поле будет содержать исключительно числа.

Поля обычного ввода реализуют интерфейс
    .parse(data)
    .value
    .format()

Поля булевского ввода реализуют интерфейс
    .parse(data)
    .value

Поля с выборкой из вариантов реализуют интерфейс
    .parse(data)
    .value

Стартовые значения полей должны задаваться в их внутреннем представлении.

To override field with reordering, redeclare class:
    class NewForm(forms.Form):
        existent_field = SomeField()

To override field without reordering, set attribute to class (or object):
    NewForm = type('NewForm', (OldForm,), {})
    NewForm.existent_field = SomeField()

Field removal is impossible
"""
import os.path as op
import inspect
import sys
import importlib
import weakref
import copy
import datetime
import gettext
import babel.core
import babel.support; nt = babel.support.NullTranslations(); _ = lambda _: _

from markupsafe import Markup
from collections import OrderedDict, Sequence
from .converters import *
from .validators import *
from .helpers import *
from .i18n import get_translations
from .bootstrap.widgets import *


# METACLASSES ==================================================================
class OrderedClass(type):
    @classmethod
    def __prepare__(metacls, clsname, bases):
        return OrderedDict()


class DeclarativeMeta(OrderedClass):
    def __init__(cls, clsname, bases, attrs):
        # Collect prototypes, set names, delete corresponding attributes from `cls`
        prototypes = OrderedDict()

        for base in bases:
            if hasattr(base, 'prototypes'):
                prototypes.update(base.prototypes)

        for name, attr in attrs.items():
            if isinstance(attr, (Field, FieldField, FormField)):
                prototypes[name] = attr
                if attr.name is None:
                    attr.name = name
                delattr(cls, name)

        cls.prototypes = prototypes


    def __iter__(cls):
        return iter(cls.prototypes.items())


    def __setattr__(cls, name, value):
        if isinstance(value, Prototype):
            value.name = name
            cls.prototypes[name] = value
        else:
            OrderedClass.__setattr__(cls, name, value)


# FIELDS =======================================================================
class Prototype(metaclass=OrderedClass):
    def __init__(self, name):
        self.name = name
        self.master = None


    def __repr__(self):
        basename = op.basename(inspect.getfile(self.__class__)).split('.')[0]
        return '<{}.{}: fullname={!r}>'.format(basename, self.__class__.__name__, self.fullname)


    def __delattr__(self, name):
        try:
            object.__delattr__(self, name)
        except AttributeError:
            pass


    def __call__(self, attrs={}, **context):
        return self.widget(self, attrs, **context)


    def bind(self, master, index=None):
        self.master = weakref.ref(master)
        self.index = index
        return self


    @property
    def locale(self):
        return self.master().locale if self.master else 'en'


    @property
    def translations(self):
        return self.master().translations if self.master else nt


    @property
    def fullname(self):
        if self.master and self.master().fullname:
            if self.name:
                if self.index is None:
                    return self.master().fullname + '.' + self.name
                else:
                    return self.master().fullname + '-{!s}'.format(self.index) + '.' + self.name
            else:
                if self.index is None:
                    return self.master().fullname
                else:
                    return self.master().fullname + '-{!s}'.format(self.index)
        else:
            return self.name


    def alerts(self, **attrs):
        return self.widget.alerts(self, **attrs)


class Field(Prototype, metaclass=OrderedClass):
    autorender = True

    def __init__(self, widget, default=None, required=False, converters=[], validators=[], name=None):
        self.widget = Widget(widget) if isinstance(widget, str) else widget
        self.default = default
        self.required = required

        try:
            self.converters = list(iter(converters))
        except TypeError:
            self.converters = [converters]
        try:
            self.validators = list(iter(validators))
        except TypeError:
            self.validators = [validators]

        Prototype.__init__(self, name)


    def clone(self):
        clone = copy.copy(self)
        del clone.value
        return clone


    @property
    def caption(self):
        return self.widget.caption


    @property
    def has_error(self):
        return 'error' in self.messages


    @property
    def has_warning(self):
        return 'warning' in self.messages


    @property
    def has_info(self):
        return 'info' in self.messages


    @property
    def has_success(self):
        return 'success' in self.messages


    # HIGH-LEVEL API
    def feed(self, value, data=None, submit=False):
        """value or data => self.value"""
        self.feed_value = value
        self.feed_data = data
        self.feed_submit = submit
        self.value = self.default
        if submit or (data or data == 0):
            try:
                self.value = self.parse_data(data)
                if self.value is None or self.value == []:
                    if (callable(self.required) and self.required()) or (not callable(self.required) and self.required):
                        raise ValidationError(self.translations.gettext('Fill the field'))
                else:
                    self.validate_value(self.value)
            except ValidationError as e:
                self.messages = {'error': [e.args[0]]}
            else:
                self.messages = {}
        else:
            self.value = self.default if value is None else value
            self.messages = {}
        return self


    def format(self):
        if self.has_error: # REVERTED apr .22 (need to return feed_data as .value now equals to default on errors)
            return self.feed_data
        else:
            return self.format_value(self.value)


    # LOW-LEVEL API
    def parse_data(self, data):
        """data => value"""
        try:
            if self.converters:
                for converter in self.converters:
                    data = converter.parse(data, self.locale)
            return data
        except (TypeError, ValueError):
            raise ValidationError(self.translations.gettext('Invalid value'))


    def format_value(self, value):
        """value => data"""
        if self.converters:
            for converter in reversed(self.converters):
                value = converter.format(value, self.locale)
        return value


    def validate_value(self, value):
        for validator in self.validators:
            validator(self.value, self)


class FieldField(Prototype, metaclass=OrderedClass): # TODO add validators! (need to check length!)
    def __init__(self, widget, prototype, default=[], required=False, converters=[], validators=[], name=None):
        self.widget = FieldFieldWidget(widget) if isinstance(widget, str) else widget
        if isinstance(prototype, Prototype):
            self.prototype = prototype
        else:
            raise ValueError('invalid `prototype` argument')
        self.default = default # TODO not in use yet
        self.required = required

        try:
            self.converters = list(iter(converters))
        except TypeError:
            self.converters = [converters]
        try:
            self.validators = list(iter(validators))
        except TypeError:
            self.validators = [validators]

        self.fields = []
        Prototype.__init__(self, name)


    def clone(self):
        clone = copy.copy(self)
        del clone.fields
        del clone.value
        return clone


    @property
    def caption(self):
        return self.widget.caption


    @property
    def has_error(self):
        return 'error' in self.messages or any(field.has_error for field in self.fields)


    @property
    def has_warning(self):
        return 'warning' in self.messages or any(field.has_warning for field in self.fields)


    @property
    def has_info(self):
        return 'info' in self.messages or any(field.has_info for field in self.fields)


    @property
    def has_success(self):
        return 'success' in self.messages or any(field.has_success for field in self.fields)


    # HIGH-LEVEL API
    def feed(self, value, data=[], submit=False):
        """
        value or data => self.value
        :arg:`data` replaces value
        """
        self.feed_value = value
        self.feed_data = data
        self.feed_submit = submit
        self.fields = []
        if submit or data:
            for (i, d) in enumerate(data or [], start=1):
                field = self.prototype.clone().bind(self, i)
                field.feed(None, d, submit)
                self.fields.append(field)
        else:
            if value is not None:
                for (i, v) in enumerate(value or [], start=1):
                    field = self.prototype.clone().bind(self, i)
                    field.feed(v, None, submit)
                    self.fields.append(field)
        if value is None:
            self.value = self.default
        else:
            self.value = value
        self.value = [field.value for field in self.fields]
        try:
            self.value = self.convert_value(self.value)
            if not self.value:
                if (callable(self.required) and self.required()) or (not callable(self.required) and self.required):
                    raise ValidationError(self.translations.gettext('Fill the field'))
            else:
                self.validate_value(self.value)
        except ValidationError as e:
            self.messages = {'error': [e.args[0]]}
        else:
            self.messages = {}
        for i, field in enumerate(self.fields):
            self.messages[i] = field.messages
        return self


    # LOW-LEVEL API
    def convert_value(self, value):
        """value => converters(value) => value"""
        try:
            if self.converters:
                for converter in self.converters:
                    value = converter.parse(value, self.locale)
            return value
        except (TypeError, ValueError):
            raise ValidationError(self.translations.gettext('Invalid value'))


    def validate_value(self, value):
        for validator in self.validators:
            validator(self.value, self)


class FormField(Prototype, metaclass=OrderedClass):
    def __init__(self, widget, prototypes, default={}, converters=[], validators=[], name=None):
        self.widget = FormFieldWidget(widget) if isinstance(widget, str) else widget
        if hasattr(prototypes, 'prototypes'):
            self.prototypes = prototypes.prototypes
        elif isinstance(prototypes, Sequence):
            self.prototypes = OrderedDict([(p.name, p) for p in prototypes if p])
        else:
            self.prototypes = OrderedDict([(name, p) for name, p in prototypes.items() if p])
        self.default = default

        try:
            self.converters = list(iter(converters))
        except TypeError:
            self.converters = [converters]
        try:
            self.validators = list(iter(validators))
        except TypeError:
            self.validators = [validators]

        self.fields = OrderedDict()
        Prototype.__init__(self, name)


    def __iter__(self):
        return iter(self.fields.items())


    def clone(self):
        clone = copy.copy(self)
        del clone.fields
        del clone.value
        return clone


    @property
    def has_error(self):
        return 'error' in self.messages or any(field.has_error for field in self.fields.values())


    @property
    def has_warning(self):
        return 'warning' in self.messages or any(field.has_warning for field in self.fields.values())


    @property
    def has_info(self):
        return 'info' in self.messages or any(field.has_info for field in self.fields.values())


    @property
    def has_success(self):
        return 'success' in self.messages or any(field.has_success for field in self.fields.values())


    @property
    def ok(self):
        return not self.has_error and self.feed_submit


    @property
    def caption(self):
        if self.widget.caption:
            return self.widget.caption
        else:
            if self.fields:
                first_field = list(self.fields.values())[0]
                return first_field.widget.caption
            else:
                return ''


    @property
    def multipart(self):
        for prototype in self.prototypes.values():
            if hasattr(prototype, 'multipart') and prototype.multipart:
                return True
        return False


    @property
    def required(self):
        for prototype in self.prototypes.values():
            if hasattr(prototype, 'required') and prototype.required:
                return True
        return False


    @property
    def enctype(self):
        return Markup('enctype="multipart/form-data"') if self.multipart else ''


    # HIGH-LEVEL API
    def feed(self, value, data={}, submit=False):
        """
        value or data => self.value
        :arg:`data` overrides :arg:`value`
        """
        self.feed_value = value
        self.feed_data = data
        self.feed_submit = submit
        self.fields = OrderedDict()
        for prototype in self.prototypes.values():
            name = prototype.name
            field = prototype.clone().bind(self)
            self.fields[name] = (
                field.feed(
                    xgetattr(value, name),
                    xgetattr(data, name),
                    submit = submit
                )
            )
        if value is None:
            if callable(self.default):
                self.value = self.default()
            elif hasattr(self.default, 'copy'):
                self.value = self.default.copy()
            else:
                self.value = copy(self.default)
        else:
            self.value = value
        for field in self.fields.values():
            xsetattr(self.value, field.name, field.value) # TODO can push fields undefined in Model
        try:
            self.value = self.convert_value(self.value)
            if not self.value:
                if (callable(self.required) and self.required()) or (not callable(self.required) and self.required):
                    raise ValidationError(self.translations.gettext('Fill the field'))
            else:
                self.validate_value(self.value)
        except ValidationError as e:
            self.messages = {'error': [e.args[0]]}
        else:
            self.messages = {}
        for name, field in self.fields.items():
            self.messages[name] = field.messages # TODO can conflict with 'error' / 'warning' / ... etc. names
        return self


    # LOW-LEVEL API
    def convert_value(self, value):
        """value => converters(value) => value"""
        try:
            if self.converters:
                for converter in self.converters:
                    value = converter.parse(value, self.locale)
            return value
        except (TypeError, ValueError) as e:
            raise ValidationError(self.translations.gettext('Invalid value'))


    def validate_value(self, value):
        for validator in self.validators:
            validator(self.value, self)


class BaseForm(FormField, metaclass=DeclarativeMeta):
    meta = {}


    def __init__(self,
        model,
        data = {},
        default = {},
        submit = None,
        locale = None,
        translations = nt,
        name = None,
    ):
        name = name or self.meta.get('name', None)
        FormField.__init__(self, FormWidget(''), self.prototypes, default, name=name)
        self._locale = babel.core.Locale.parse(locale or 'en')
        self._translations = get_translations(self._locale) if isinstance(translations, gettext.NullTranslations) else translations
        self.feed(model, data, submit)


    def feed(self, model, data={}, submit=False): # TODO need this method (kinda python bug) ??
        return FormField.feed(self, model, data, submit)


    @property
    def locale(self):
        return self._locale


    @property
    def translations(self):
        return self._translations


    @classmethod
    def deepcopy(cls):
        class CopyForm(cls):
            pass
        CopyForm.__name__ = cls.__name__
        CopyForm.prototypes = copy.deepcopy(cls.prototypes)
        return CopyForm


class ChoiceField(Field):
    def __init__(self,
        widget,
        choices = [],
        default = None,
        required = False,
        converters = [StrConverter()],
        validators = [],
        name = None
    ):
        widget = SelectWidget(widget) if isinstance(widget, str) else widget
        self.choices = choices
        Field.__init__(self, widget, default, required, converters, validators, name)


    # LOW-LEVEL API
    def validate_value(self, value):
        Field.validate_value(self, value)
        if self.choices:
            if value not in self.choices:
                raise ValidationError(
                    self.translations.gettext('Invalid value {!r} for defined `choices`').format(value)
                )


    def is_chosen(self, value): # TODO remove?
        # if self.has_error:
        #     return self.format_value(value) == self.feed_data
        # else:
        return value == self.value


    def bind(self, master, index=None):
        super().bind(master, index)
        if callable(self.choices):
            self.choices = self.choices()
        if hasattr(self.widget, 'options') and callable(self.widget.options):
            self.widget.options = self.widget.options()
        return self


class MultiChoiceField(Field):
    def __init__(self,
        widget,
        choices = [],
        default = [],
        required = False,
        converters = MapConverter(converter=StrConverter()),
        validators = [],
        name = None
    ):
        widget = MultiCheckboxWidget(widget) if isinstance(widget, str) else widget
        self.choices = choices
        Field.__init__(self, widget, default, required, converters, validators, name)


    # HIGH-LEVEL API
    def format(self):
        raise Exception('Undefined behavior. Use `format_value` instead!')


    # LOW-LEVEL API
    def validate_value(self, value):
        Field.validate_value(self, value)
        if self.choices:
            for v in value:
                if v not in self.choices:
                    raise ValidationError(
                        self.translations.gettext('Invalid value {!r} for defined `choices`').format(v)
                    )


    def is_chosen(self, value): # TODO remove?
        # if self.has_error:
        #     return self.format_value(value) in self.feed_data
        # else:
        return value in self.value


    def format_value(self, value):
        """value => data"""
        return Field.format_value(self, [value])[0]


    def bind(self, master, index=None):
        super().bind(master, index)
        if callable(self.choices):
            self.choices = self.choices()
        if hasattr(self.widget, 'options') and callable(self.widget.options):
            self.widget.options = self.widget.options()
        return self


# SHORTCUTS ====================================================================
def TextField(widget, default=None, required=False, converters=StrConverter(), validators=LengthValidator(max=255), name=None):
    widget = TextWidget(widget) if isinstance(widget, str) else widget
    return Field(widget, default, required, converters, validators, name=name)


def CheckField(widget, default=None, required=False, validators=[], name=None):
    widget = CheckboxWidget(widget) if isinstance(widget, str) else widget
    return Field(widget, default, required, converters=BoolConverter(none=False), validators=validators, name=name)


def DateField(widget, default=None, required=False, validators=[], name=None):
    widget = DateWidget(widget) if isinstance(widget, str) else widget
    return Field(widget, converters=DateConverter(), default=default, required=required, validators=validators, name=name)


def DateTimeField(widget, default=None, required=False, validators=[], name=None):
    widget = DateTimeWidget(widget) if isinstance(widget, str) else widget
    return Field(widget, converters=DateTimeConverter(), default=default, required=required, validators=validators, name=name)


def BetweenIntField(widget, min=0, max=None, unit_field=None, name=None):
    widget = BetweenWidget(widget) if isinstance(widget, str) else widget
    if unit_field:
        unit_field.name = 'unit'
    return FormField(
        widget = widget,
        prototypes = [
            Field('', [IntConverter()], validators=[ValueValidator(min=min, max=max)], name='min'),
            Field('', [IntConverter()], validators=[ValueValidator(min=min, max=max)], name='max'),
            unit_field
        ],
        name = name
    )


def BetweenFloatField(widget, min=0.0, max=None, unit_field=None, name=None):
    widget = BetweenWidget(widget) if isinstance(widget, str) else widget
    if unit_field:
        unit_field.name = 'unit'
    return FormField(
        widget = widget,
        prototypes = [
            Field('', [FloatConverter()], validators=[ValueValidator(min=min, max=max)], name='min'),
            Field('', [FloatConverter()], validators=[ValueValidator(min=min, max=max)], name='max'),
            unit_field
        ],
        name = name
    )


def BetweenDecimalField(widget, min=0, max=None, unit_field=None, name=None):
    widget = BetweenWidget(widget) if isinstance(widget, str) else widget
    if unit_field:
        unit_field.name = 'unit'
    return FormField(
        widget = widget,
        prototypes = [
            Field('', [DecimalConverter()], validators=[ValueValidator(min=min, max=max)], name='min'),
            Field('', [DecimalConverter()], validators=[ValueValidator(min=min, max=max)], name='max'),
            unit_field
        ],
        name = name
    )


def BetweenDateField(widget, name=None):
    widget = BetweenWidget(widget) if isinstance(widget, str) else widget
    return FormField(
        widget = widget,
        prototypes = [
            DateField('', name='min'),
            DateField('', name='max'),
        ],
        name = name
    )


def BetweenDateTimeField(widget, name=None):
    widget = BetweenWidget(widget) if isinstance(widget, str) else widget
    return FormField(
        widget = widget,
        prototypes = [
            DateTimeField('', name='min'),
            DateTimeField('', name='max'),
        ],
        name = name
    )


def FilterTextField(caption, name=None):
    return FormField(
        widget = FilterTextWidget(caption),
        prototypes = [
            ChoiceField(
                widget = SelectWidget(''),
                choices = ('starts_with', 'contains', 'equals', 'not_equals', 'empty'),
                default = 'starts_with',
                name = 'command'
            ),
            Field(TextWidget(''), converters=[StrConverter()], name='starts_with'),
            Field(TextWidget(''), converters=[StrConverter()], name='contains'),
            Field(TextWidget(''), converters=[StrConverter()], name='equals'),
            Field(TextWidget(''), converters=[StrConverter()], name='not_equals'),
            ChoiceField(SelectWidget(''), choices=('*', 'yes', 'no'), default='*', name='empty')
        ],
        name = name
    )


def FilterIntField(caption, name=None):
    return FormField(
        widget = FilterRangeWidget(caption),
        prototypes = [
            ChoiceField(
                widget = SelectWidget(''),
                choices = ('equals', 'not_equals', 'between', 'empty'),
                default = 'equals',
                name = 'command'
            ),
            Field(TextWidget(''), converters=[IntConverter()], name='equals'),
            Field(TextWidget(''), converters=[IntConverter()], name='not_equals'),
            BetweenIntField('', name='between'),
            ChoiceField(SelectWidget(''), choices=('*', 'yes', 'no'), default='*', name='empty')
        ],
        name = name
    )


def FilterFloatField(caption, name=None):
    return FormField(
        widget = FilterRangeWidget(caption),
        prototypes = [
            ChoiceField(
                widget = SelectWidget(''),
                choices = ('equals', 'not_equals', 'between', 'empty'),
                default = 'equals',
                name = 'command'
            ),
            Field(TextWidget(''), converters=[FloatConverter()], name='equals'),
            Field(TextWidget(''), converters=[FloatConverter()], name='not_equals'),
            BetweenFloatField('', name='between'),
            ChoiceField(SelectWidget(''), choices=('*', 'yes', 'no'), default='*', name='empty')
        ],
        name = name
    )


def FilterDecimalField(caption, name=None):
    return FormField(
        widget = FilterRangeWidget(caption),
        prototypes = [
            ChoiceField(
                widget = SelectWidget(''),
                choices = ('equals', 'not_equals', 'between', 'empty'),
                default = 'equals',
                name = 'command'
            ),
            Field(TextWidget(''), converters=[DecimalConverter()], name='equals'),
            Field(TextWidget(''), converters=[DecimalConverter()], name='not_equals'),
            BetweenDecimalField('', name='between'),
            ChoiceField(SelectWidget(''), choices=('*', 'yes', 'no'), default='*', name='empty')
        ],
        name = name
    )


def FilterDateField(caption, name=None):
    return FormField(
        widget = FilterRangeWidget(caption),
        prototypes = [
            ChoiceField(
                widget = SelectWidget(''),
                choices = ('equals', 'not_equals', 'between', 'empty'),
                default = 'equals',
                name = 'command'
            ),
            DateField('', name='equals'),
            DateField('', name='not_equals'),
            BetweenDateField('', name='between'),
            ChoiceField(SelectWidget(''), choices=('*', 'yes', 'no'), default='*', name='empty')
        ],
        name = name
    )


def FilterDateTimeField(widget, name=None):
    return FormField(
        widget = FilterRangeWidget(caption),
        prototypes = [
            ChoiceField(
                widget = SelectWidget(''),
                choices = ('equals', 'not_equals', 'between', 'empty'),
                default = 'equals',
                name = 'command'
            ),
            DateTimeField('', name='equals'),
            DateTimeField('', name='not_equals'),
            BetweenDateTimeField('', name='between'),
            ChoiceField(SelectWidget(''), choices=('*', 'yes', 'no'), default='*', name='empty')
        ],
        name = name
    )


__all__ = (
    # FIELDS
    'Field',
    'FieldField',
    'FormField',
    'BaseForm',
    'ChoiceField',
    'MultiChoiceField',
    'TextField',
    'CheckField',
    'DateField',
    'DateTimeField',
    'BetweenIntField',
    'BetweenFloatField',
    'BetweenDecimalField',
    'BetweenDateField',
    'BetweenDateTimeField',
    'FilterTextField',
    'FilterIntField',
    'FilterFloatField',
    'FilterDecimalField',
    'FilterDateField',
    'FilterDateTimeField',
)
