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
def make_field(field, field_class, **kwargs):
    if field is not False:
        if isinstance(field, dict):
            widget = kwargs.pop('widget', '') or field.pop('widget', '')
            field = field_class(widget, **dict(kwargs, **field))
        elif field is None:
            widget = kwargs.pop('widget', '')
            field = field_class(widget, **kwargs)
        else:
            for key, value in kwargs.items():
                if getattr(field, key, None) is None:
                    setattr(field, key, value)
    return field


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
        self.widget = make_widget(widget, Widget)
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
        self.widget = make_widget(widget, FieldFieldWidget)
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
        self.widget = make_widget(widget, FormFieldWidget)
        if hasattr(prototypes, 'prototypes'):
            self.prototypes = prototypes.prototypes
        elif isinstance(prototypes, Sequence):
            self.prototypes = OrderedDict([(prototype.name, prototype) for prototype in prototypes])
        else:
            self.prototypes = prototypes
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
        widget = make_widget(widget, SelectWidget)
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
        widget = make_widget(widget, MultiCheckboxWidget)
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


class BetweenField(FormField):
    def __init__(self,
        widget,
        min_field,
        max_field,
        unit_field = False,
        shared = {},
        name = None,
    ):
        widget = make_widget(widget, BetweenWidget)
        FormField.__init__(self, widget, [], name=name)
        self.lazy_prototypes = OrderedDict([
            ('min', min_field),
            ('max', max_field),
            ('unit', unit_field),
        ])
        self.shared = shared


    def bind(self, master, index=None):
        FormField.bind(self, master, index)
        min_field = make_field(
            field = self.lazy_prototypes['min'],
            field_class = Field,
            widget = TextWidget(''),
            name = 'min',
            **self.shared
        )
        max_field = make_field(
            field = self.lazy_prototypes['max'],
            field_class = Field,
            widget = TextWidget(''),
            name = 'max',
            **self.shared
        )
        unit_field = make_field(
            field = self.lazy_prototypes['unit'],
            field_class = ChoiceField,
            choices = [],
            name = 'unit',
        )
        prototypes = list(filter(None,
            [min_field, max_field, unit_field]
        ))
        self.prototypes = OrderedDict([(prototype.name, prototype) for prototype in prototypes])
        return self


class FilterTextField(FormField):
    commands = ('starts_with', 'contains', 'equals', 'not_equals', 'empty')


    def __init__(self,
        widget,
        command_field = None,
        starts_with_field = None,
        contains_field = None,
        equals_field = None,
        not_equals_field = None,
        empty_field = None,
        shared = dict(converters=[StrConverter()]),
        name = None
    ):
        widget = make_widget(widget, FilterTextWidget)
        FormField.__init__(self, widget, [], name=name)
        self.lazy_prototypes = OrderedDict([
            ('command', command_field),
            ('starts_with', starts_with_field),
            ('contains', contains_field),
            ('equals', equals_field),
            ('not_equals', not_equals_field),
            ('empty', empty_field),
        ])
        self.shared = shared


    def bind(self, master, index=None):
        FormField.bind(self, master, index)
        command_field = make_field(
            field = self.lazy_prototypes['command'],
            field_class = ChoiceField,
            widget = SelectWidget('', list(map(self.translations.gettext, self.commands))),
            choices = self.commands,
            default = 'contains',
            name = 'command',
        )
        starts_with_field = make_field(
            field = self.lazy_prototypes['starts_with'],
            field_class = Field,
            widget = TextWidget(''),
            name = 'starts_with',
            **self.shared
        )
        contains_field = make_field(
            field = self.lazy_prototypes['contains'],
            field_class = Field,
            widget = TextWidget(''),
            name = 'contains',
            **self.shared
        )
        equals_field = make_field(
            field = self.lazy_prototypes['equals'],
            field_class = Field,
            widget = TextWidget(''),
            name = 'equals',
            **self.shared
        )
        not_equals_field = make_field(
            field = self.lazy_prototypes['not_equals'],
            field_class = Field,
            widget = TextWidget(''),
            name = 'not_equals',
            **self.shared
        )
        empty_field = make_field(
            field = self.lazy_prototypes['empty'],
            field_class = ChoiceField,
            widget = SelectWidget(''),
            choices = ['*', 'yes', 'no'],
            default = '*',
            name = 'empty',
        )
        prototypes = list(filter(None,
            [command_field, starts_with_field, contains_field, equals_field, not_equals_field, empty_field]
        ))
        self.prototypes = OrderedDict([(prototype.name, prototype) for prototype in prototypes])
        return self


class FilterRangeField(FormField):
    commands = ('equals', 'not_equals', 'between', 'empty')


    def __init__(self,
        widget,
        command_field = None,
        equals_field = None,
        not_equals_field = None,
        between_field = None,
        empty_field = None,
        shared = {},
        name = None,
    ):
        widget = make_widget(widget, FilterRangeWidget)
        FormField.__init__(self, widget, [], name=name)
        self.lazy_prototypes = OrderedDict([
            ('command', command_field),
            ('equals', equals_field),
            ('not_equals', not_equals_field),
            ('between', between_field),
            ('empty', empty_field),
        ])
        self.shared = shared


    def bind(self, master, index=None):
        FormField.bind(self, master, index)
        command_field = make_field(
            field = self.lazy_prototypes['command'],
            field_class = ChoiceField,
            widget = SelectWidget('', list(map(self.translations.gettext, self.commands))),
            choices = self.commands,
            default = 'equals',
            name = 'command'
        )
        equals_field = make_field(
            field = self.lazy_prototypes['equals'],
            field_class = Field,
            widget = TextWidget(''),
            name = 'equals',
            **self.shared
        )
        not_equals_field = make_field(
            field = self.lazy_prototypes['not_equals'],
            field_class = Field,
            widget = TextWidget(''),
            name = 'not_equals',
            **self.shared
        )
        between_field = make_field(
            field = self.lazy_prototypes['between'],
            field_class = BetweenField,
            widget = TextWidget(''),
            name = 'between',
            **self.shared
        )
        empty_field = make_field(
            field = self.lazy_prototypes['empty'],
            field_class = ChoiceField,
            widget = SelectWidget(''),
            choices = ['*', 'yes', 'no'],
            default = '*',
            name = 'empty',
        )
        prototypes = list(filter(None,
            [command_field, equals_field, not_equals_field, between_field, empty_field]
        ))
        self.prototypes = OrderedDict([(prototype.name, prototype) for prototype in prototypes])
        return self


# SHORTCUTS ====================================================================
def TextField(widget, default=None, required=False, converters=StrConverter(), validators=LengthValidator(max=255), name=None):
    widget = make_widget(widget, TextWidget)
    return Field(widget, default, required, converters, validators, name=name)


def CheckField(widget, default=None, required=False, validators=[], name=None):
    widget = make_widget(widget, CheckboxWidget)
    return Field(widget, default, required, converters=BoolConverter(none=False), validators=validators, name=name)


def DateField(widget, default=None, required=False, validators=[], name=None):
    widget = make_widget(widget, DateWidget)
    return Field(widget, converters=DateConverter(), default=default, required=required, validators=validators, name=name)


def DateTimeField(widget, default=None, required=False, validators=[], name=None):
    widget = make_widget(widget, DateTimeWidget)
    return Field(widget, converters=DateTimeConverter(), default=default, required=required, validators=validators, name=name)


def BetweenDateField(widget):
    return BetweenField(
        widget = widget,
        min_field = Field(TextWidget('', attrs={'data-role': 'datepicker'})),
        max_field = Field(TextWidget('', attrs={'data-role': 'datepicker'})),
        shared = dict(converters=[DateConverter()])
    )


def BetweenDateTimeField(widget):
    return BetweenField(
        widget = widget,
        min_field = Field(TextWidget('', attrs={'data-role': 'datetimepicker'}), converters=DateTimeConverter()),
        max_field = Field(TextWidget('', attrs={'data-role': 'datetimepicker'}), converters=DateTimeConverter()),
    )


def FilterDateField(widget):
    return FilterRangeField(
        widget,
        equals_field = DateField(''),
        not_equals_field = DateField(''),
        between_field = BetweenDateField(''),
        shared = dict(converters=[DateConverter()]),
    )


def FilterDateTimeField(widget):
    return FilterRangeField(
        widget,
        equals_field = DateTimeField(''),
        not_equals_field = DateTimeField(''),
        between_field = BetweenDateTimeField(''),
        shared = dict(converters=[DateTimeConverter()]),
    )


__all__ = (
    'make_field',

    # FIELDS
    'Field',
    'FieldField',
    'FormField',
    'BaseForm',
    'ChoiceField',
    'MultiChoiceField',
    'BetweenField',
    'FilterTextField',
    'FilterRangeField',

    # SHORTCUTS
    'TextField',
    'CheckField',
    'DateField',
    'DateTimeField',
    'BetweenDateField',
    'BetweenDateTimeField',
    'FilterDateField',
    'FilterDateTimeField'
)
