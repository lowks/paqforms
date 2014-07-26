import collections
import html
import re

from markupsafe import Markup


class Attr(collections.Sequence):
    """HTML attribute. Provides seamless concatenation and escaping"""
    def __init__(self, value, oneval=False):
        if value is None:
            self.value = ''
        elif value is False:
            self.value = '0'
        elif value is True:
            self.value = '1'
        else:
            self.value = str(value)
        self.oneval = oneval


    def __str__(self):
        chunks = filter(None, self.value.split(' '))
        value = ' '.join(chunks).strip()
        result = html.escape(value, True).replace('&#x27;', "'")
        return self.clean_oneval_str(result) if self.oneval else result


    def __add__(self, other):
        if isinstance(other, Attr):
            other = other.value
        self.value = '{} {}'.format(self.value, other)
        return self


    def __radd__(self, other):
        if isinstance(other, Attr):
            other = other.value
        self.value = '{} {}'.format(other, self.value)
        return self


    def __getitem__(self, item):
        return self.value.__getitem__(item)


    def __getattr__(self, item):
        return self.value.__getattr__(item)


    def __len__(self):
        return self.value.__len__()


    def clean_oneval_str(self, data):
        result = re.subn('\s+', '-', data)[0]
        return re.subn('[-]+', '-', result)[0]


class Attrs(dict):
    """HTML attributes collection
    Features:
        * raises ValueError for None & False (the way HTML works ^_^)
        * uses Attr objects as values
        * supports namespaces (grab via prefix)
        * drops attrs with '_' prefix at render
        * treats attrs with '_' suffix as ones without (e.g. class_ <=> class)
    """
    @classmethod
    def take_prefixed(cls, iterable, prefix):
        """
        Side effect: pop :arg`mapping` keys, starting with :arg`prefix`
        """
        attrs = {}
        for key in iterable.copy().keys():
            if key.startswith(prefix):
                attrs[key[len(prefix):]] = iterable.pop(key)
        return cls(attrs)


    def __init__(self, *args, **kwargs):
        for arg in args:
            iterable = arg.items() if isinstance(arg, collections.Mapping) else arg
            for key, value in iterable:
                self[key.rstrip('_')] = value
        for key, value in kwargs.items():
            self[key.rstrip('_')] = value


    def __getitem__(self, key):
        try:
            value = dict.__getitem__(self, key.rstrip('_'))
        except KeyError:
            value = ''
        if value is False or value is None:
            return value
        else:
            return Attr(value)


    def __str__(self):
        return ' '.join(
            '{}="{}"'.format(key, self[key]) for key in sorted(self)
            if not key.startswith('_') and self[key] is not False and self[key] is not None
        )


    def __html__(self): # this don't work properly (with autoescape?!). Looks like Jinja bug, caused by magic overuse
        return self.__str__()


    def copy(self):
        return Attrs(dict.copy(self))


def render_prepend(attrs):
    div_classes = []
    prepend, append = attrs.pop('prepend', ''), attrs.pop('append', '')
    if prepend or append:
        addon_html = ""
        if prepend:
            div_classes.append('input-prepend')
            addon_html = """<span class="add-on">{}</span>""".format(prepend)
        if append:
            div_classes.append('input-append')
        return Markup(
            """<div class="{}">{}""".format(" ".join(sorted(div_classes)), addon_html)
        )
    else:
        return ""


def render_append(attrs):
    prepend, append = attrs.pop('prepend', ''), attrs.pop('append', '')
    if prepend or append:
        addon_html = """<span class="add-on">{}</span>""".format(append) if append else ""
        return Markup(
            """{}</div>""".format(addon_html)
        )
    else:
        return ""


def render_messages(messages):
    if messages.get('error'):
        error = """<small class="help-block">{}</small>""".format('. '.join(messages.get('error', [])))
    else:
        error = ""
    if messages.get('warning'):
        warning = """<small class="help-block">{}</small>""".format('. '.join(messages.get('warning', [])))
    else:
        warning = ""
    if messages.get('info'):
        info = """<small class="help-block">{}</small>""".format('. '.join(messages.get('info', [])))
    else:
        info = ""
    if messages.get('success'):
        success = """<small class="help-block">{}</small>""".format('. '.join(messages.get('success', [])))
    else:
        success = ""
    if error or warning or info or success:
        messages = """
        <div>
            {error}
            {success}
            {warning}
            {info}
        </div>
        """.format(**locals())
    else:
        messages = ""
    return Markup(messages)


def render_label(field, caption, attrs={}, description=None, tooltip=None):
    attrs = Attrs(attrs.copy())
    attrs['for'] = field.fullname
    attrs['required'] = attrs['required'] or field.required
    return Markup(
        """
        <label class="control-label" {attrs}>{caption}{description}{tooltip}</label>
        """.format(
            attrs = Attrs(attrs),
            caption = caption,
            description = (""" <span class="muted">{}</span>""".format(description) if description else ''),
            tooltip = (""" <a href="#" data-toggle="tooltip" title="{}"><i class="fa fa-question-circle"></i></a>""".format(tooltip) if tooltip else '')
        )
    )


__all__ = (
    'Attr', 'Attrs',
    'render_prepend', 'render_append', 'render_messages',
    'render_label',
)
