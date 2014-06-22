import re
import requests


# HELPERS
def xgetid(model):
    if isinstance(model, dict):
        if '_id' in model:
            return model['_id']
        else:
            return model['id']
    else:
        if 'get_pk' in model:
            pk = model.get_pk()
            return getattr(model, pk)
        else:
            return model.id


# EXCEPTIONS
class ValidationError(Exception):
    pass


# VALIDATORS
class LengthValidator:
    """
    Validates the length of a string or list field.
    """
    def __init__(self, min=None, max=None, exact=None, min_message=None, max_message=None, minmax_message=None, exact_message=None):
        """
        :param min: minimum length. If not provided, minimum length will not be checked.
        :param max: maximum length. If not provided, maximum length will not be checked.
        :param exact: exact length. If not provided, maximum length will not be checked.
        :param min_message: message for "lesser than min" ValidationError
        :param max_message: message for "bigger than max" ValidationError
        :param minmax_message: message for "not between min and max" ValidationError
        :param exact_message: message for "not equal to exact" ValidationError

        Setting :param min equal to :param max is the same as setting :param exact
        """
        self.min = min
        self.max = max
        self.exact = exact
        if self.min == self.max and self.min is not None:
            self.exact = self.min
            self.min = None
            self.max = None
        self.min_message = min_message
        self.max_message = max_message
        self.minmax_message = minmax_message
        self.exact_message = exact_message


    def __call__(self, value, field):
        if self.exact is not None:
            if len(value) != self.exact:
                message_tpl = self.exact_message or field.translations.gettext('Length <> {exact}')
                message = message_tpl.format(exact=str(self.exact))
                raise ValidationError(message)
        elif self.min is not None and self.max is not None:
            if len(value) < self.min or len(value) > self.max:
                message_tpl = self.minmax_message or field.translations.gettext('Length is not between [{min}:{max}]')
                message = message_tpl.format(min=self.min, max=self.max)
                raise ValidationError(message)
        elif self.min is not None:
            if len(value) < self.min:
                message_tpl = self.min_message or field.translations.gettext('Length < {min}')
                message = message_tpl.format(min=self.min)
                raise ValidationError(message)
        elif self.max is not None:
            if len(value) > self.max:
                message_tpl = self.max_message or field.translations.gettext('Length > {max}')
                message = message_tpl.format(max=self.max)
                raise ValidationError(message)


class ValueValidator:
    """
    Validates the value of an integer or float field.
    """
    def __init__(self, min=None, max=None, exact=None, min_message=None, max_message=None, minmax_message=None, exact_message=None):
        """
        :param min: minimum value. If not provided, minimum value will not be checked.
        :param max: maximum value. If not provided, maximum value will not be checked.
        :param exact: exact value. If not provided, maximum value will not be checked.
        :param min_message: message for "lesser than min" ValidationError
        :param max_message: message for "bigger than max" ValidationError
        :param minmax_message: message for "not between min and max" ValidationError
        :param exact_message: message for "not equal to exact" ValidationError

        Setting :param min equal to :param max is the same as setting :param exact
        """
        self.min = min
        self.max = max
        self.exact = exact
        if self.min == self.max and self.min is not None:
            self.exact = self.min
            self.min = None
            self.max = None
        self.min_message = min_message
        self.max_message = max_message
        self.minmax_message = minmax_message
        self.exact_message = exact_message


    def __call__(self, value, field):
        if self.exact is not None:
            if value != self.exact:
                message_tpl = self.exact_message or field.translations.gettext('Value <> {exact}')
                message = message_tpl.format(exact=self.exact)
                raise ValidationError(message)
        elif self.min is not None and self.max is not None:
            if value < self.min or value > self.max:
                message_tpl = self.minmax_message or field.translations.gettext('Value is not between [{min}:{max}]')
                message = message_tpl.format(min=self.min, max=self.max)
                raise ValidationError(message)
        elif self.min is not None:
            if value < self.min:
                message_tpl = self.min_message or field.translations.gettext('Value < {min}')
                message = message_tpl.format(min=self.min)
                raise ValidationError(message)
        elif self.max is not None:
            if value > self.max:
                message_tpl = self.max_message or field.translations.gettext('Value > {max}')
                message = message_tpl.format(max=self.max)
                raise ValidationError(message)


class OneOfValidator:
    def __init__(self, options, message=None):
        self.options = options # cannot use sets here
        self.message = message


    def __call__(self, value, field):
        if value not in self.options:
            message = self.message or field.translations.gettext('Invalid value')
            raise ValidationError(message)


class RegexValidator:
    def __init__(self, regex, flags=0, message=None):
        if not isinstance(regex, str):
            raise TypeError("`regex` must be 'str'")
        self.regex = regex
        self.flags = flags
        self.message = message


    def __call__(self, value, field):
        if not re.search(self.regex, value, self.flags):
            message = self.message or field.translations.gettext('Invalid input')
            raise ValidationError(message)


class EmailValidator(RegexValidator):
    def __init__(self, message=None):
        RegexValidator.__init__(self, r'^[-\w+.]+@[-\w+.]+$', re.IGNORECASE, message)


    def __call__(self, value, field):
        try:
            RegexValidator.__call__(self, value, field)
        except ValidationError:
            if self.message:
                raise
            else:
                message = field.translations.gettext('Invalid email')
                raise ValidationError(message)


class URLValidator(RegexValidator):
    def __init__(self, message=None):
        RegexValidator.__init__(self,
            r'^[a-z]+://([^/:]+\.[a-z]{2,10}|([0-9]{1,3}\.){3}[0-9]{1,3})(:[0-9]+)?(/.*)?$',
            re.IGNORECASE,
            message
        )


    def __call__(self, value, field):
        try:
            RegexValidator.__call__(self, value, field)
        except ValidationError:
            if self.message:
                raise
            else:
                message = field.translations.gettext('Invalid URL')
                raise ValidationError(message)


class RepeatValidator:
    def __init__(self, fieldname, message=None):
        self.fieldname = fieldname
        self.message = message


    def __call__(self, value, field):
        try:
            otherfield = field.master().fields[self.fieldname]
        except KeyError:
            message_tpl = field.translations.gettext("Invalid field name {fieldname}")
            message = message_tpl.format(fieldname=self.fieldname)
            raise RuntimeError(message)
        if value != otherfield.value:
            message_tpl = self.message or field.translations.gettext('Must be equal to {othercaption}')
            message = message_tpl.format(thiscaption=field.widget.caption, othercaption=otherfield.widget.caption)
            raise ValidationError(message)


class CallbackValidator:
    def __init__(self, callback, message=None):
        """
        :param callback: func(value, field) => bool
        """
        self.callback = callback
        self.message = message


    def __call__(self, value, field):
        result = self.callback(value, field)
        if not result:
            raise ValidationError(self.message)


class MapValidator:
    def __init__(self, validator, message=None):
        self.validator = validator
        self.message = message


    def __call__(self, value, field):
        try:
            [self.validator(v, field) for v in value]
        except ValidationError as e:
            message_start = self.message or field.translations.gettext('One of the objects has the following error')
            message = '{}: {}'.format(message_start, str(e))
            raise ValidationError(message)


__all__ = (
    # EXCEPTIONS
    'ValidationError',

    # VALIDATORS
    'LengthValidator', 'ValueValidator', 'OneOfValidator',
    'RegexValidator', 'EmailValidator', 'URLValidator',
    'RepeatValidator', 'CallbackValidator', 'MapValidator',
)