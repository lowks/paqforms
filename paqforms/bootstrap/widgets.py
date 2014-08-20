import os.path as op; __dir__ = op.dirname(op.abspath(__file__))
import itertools
import html
import jinja2

from markupsafe import Markup

from ..html import *


class Widget:
    template = None # Can be overriden # HACK - nearly unused...
    alerts_template = 'alerts-inline.html'
    template_dirs = [op.join(__dir__, 'templates')]


    def __init__(self, caption, attrs={}, template=None, template_dirs=[], **context):
        self.caption = caption
        self.attrs = attrs.copy()
        self.context = context
        self.template = template or self.template
        self.template_dirs = template_dirs or self.template_dirs
        template_loader = jinja2.FileSystemLoader(self.template_dirs)
        self.template_env = jinja2.Environment(loader=template_loader, extensions=['jinja2.ext.do'])


    def __call__(self, field, attrs={}, **context):
        attrs = Attrs(self.attrs, attrs)

        # MAIN
        context = dict(self.context, **context)
        context.setdefault('field', field)
        context.setdefault('widget', self)

        # PYTHON COMMONS
        context['str'] = str
        context['any'] = any
        context['enumerate'] = enumerate
        context['isinstance'] = isinstance
        context['tuple'] = tuple

        # PAQFORMS
        context['_'] = field.translations.gettext
        context['Attr'] = Attr
        context['Attrs'] = Attrs

        if self.template:
            template = self.template_env.get_template('widgets/' + self.template)
        else:
            filenames = ['widgets/{}.html'.format(cls.__name__) for cls in self.__class__.mro()[:-2]]
            if filenames:
                template = self.template_env.select_template(filenames)
            else:
                raise Exception('Cannot render `Widget` class. Extend it or define `template` to use!')

        return Markup(
            template.render(
                attrs = attrs,
                context = context,
                **context
            )
        )


    def debug_repr(self):
        return html.escape(super().__repr__())


    def alerts(self, field):
        if any(field.messages.values()):
            template = self.template_env.get_template(op.join('helpers', self.alerts_template))
            return Markup(
                template.render(field=field, __=field.translations.gettext)
            )
        else:
            return ''


class FieldFieldWidget(Widget):
    def __call__(self, field, attrs={}, **context):
        attrs = Attrs(self.attrs, attrs)
        prototype = field.prototype.clone()
        prototype.name = field.name + '-0'
        prototype.bind(field.master(), 0).feed(None)
        context['prototype'] = prototype
        return Widget.__call__(self, field, attrs, **context)


class FieldsetWidget(Widget):
    def __init__(self, caption, compact=False, inline=False, attrs={}, template=None, template_dirs=[], **context):
        Widget.__init__(self, caption, attrs, template, template_dirs, **context)
        self.compact = compact
        self.inline = inline


    alerts_template = 'alerts-inline.html'


class FormFieldWidget(Widget):
    def __init__(self, caption, compact=False, inline=False, attrs={}, template=None, template_dirs=[], **context):
        Widget.__init__(self, caption, attrs, template, template_dirs, **context)
        self.compact = compact
        self.inline = inline


    alerts_template = 'alerts-inline.html'


class FormWidget(Widget):
    alerts_template = 'alerts-block.html'


    def __call__(self, form, attrs={}, **context):
        attrs = Attrs(self.attrs, attrs)
        return Markup('\n'.join(field(attrs=attrs, **context) for field in form.fields.values() if getattr(field, 'autorender', True)))


class HiddenWidget(Widget):
    type = 'hidden'
    template = 'InputWidget.html'


class InvisibleWidget(Widget):
    type = 'hidden'
    template = 'InvisibleWidget.html'


class TextWidget(Widget):
    type = 'text'
    template = 'InputWidget.html'


class PasswordWidget(Widget):
    type = 'password'
    template = 'InputWidget.html'


class CheckboxWidget(Widget):
    template = 'CheckboxWidget.html'


class DateWidget(TextWidget):
    """Requires: bootstrap-datepicker.js"""
    def __call__(self, field, attrs={}, **context):
        attrs = Attrs(attrs, {'data-role': 'datepicker'})
        return Widget.__call__(self, field, attrs, **context)


class DateTimeWidget(TextWidget):
    """Requires: bootstrap-datepicker.js"""
    def __call__(self, field, attrs={}, **context):
        attrs = Attrs(attrs, {'data-role': 'datetimepicker'})
        return Widget.__call__(self, field, attrs, **context)


class TextareaWidget(Widget):
    pass


class SelectWidget(Widget):
    def __init__(self, caption, options=[], get_option=None, multiple=False, attrs={}, template=None, template_dirs=[], **context):
        Widget.__init__(self, caption, attrs, template, template_dirs, **context)
        if options:
            self.options = options if callable(options) else (lambda: options)
        else:
            self.options = lambda: []
        if isinstance(get_option, str):
            self.get_option = lambda model: getattr(model, get_option) if model else ''
        else:
            self.get_option = get_option
        self.multiple = multiple


    def __call__(self, field, attrs={}, **context):
        context['zip_longest'] = itertools.zip_longest
        return Widget.__call__(self, field, attrs, **context)


class MultiCheckboxWidget(Widget):
    def __init__(self, caption, options=[], get_option=None, show_toggler=True, attrs={}, template=None, template_dirs=[], **context):
        Widget.__init__(self, caption, attrs, template, template_dirs, **context)
        if options:
            self.options = options if callable(options) else (lambda: options)
        else:
            self.options = lambda: []
        if isinstance(get_option, str):
            self.get_option = lambda model: getattr(model, get_option) if model else ''
        else:
            self.get_option = get_option
        self.show_toggler = show_toggler


    def __call__(self, field, attrs={}, **context):
        context['zip_longest'] = itertools.zip_longest
        return Widget.__call__(self, field, attrs, **context)


# FILTER WIDGETS
class FilterTextWidget(Widget):
    pass


class FilterRangeWidget(Widget):
    pass


__all__ = (
    'Widget',
    'FieldFieldWidget',
    'FormFieldWidget',
    'FieldsetWidget',
    'FormWidget',
    'HiddenWidget',
    'InvisibleWidget',
    'TextWidget',
    'PasswordWidget',
    'DateWidget',
    'DateTimeWidget',
    'TextareaWidget',
    'CheckboxWidget',
    'SelectWidget',
    'MultiCheckboxWidget',
    'FilterTextWidget',
    'FilterRangeWidget',
)

# TODO проработать эти input-small (???)
