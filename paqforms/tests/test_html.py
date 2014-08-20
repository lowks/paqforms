from markupsafe import Markup

from paqforms.html import *
from . import clean

class Test_Attr:
    def test_escape(self):
        assert str(Attr('a')) == 'a'
        assert str(Attr('"')) == '&quot;'
        assert str(Attr("'")) == "'"
        assert str(Attr("<")) == "&lt;"
        assert str(Attr(">")) == "&gt;"
        assert str(Attr("&")) == "&amp;"


    def test_in(self):
        attr = Attr('http://somehost/#someanchor')
        assert '#' in attr
        assert '?' not in attr

    #def test_sortable(self): --- off now
    #    attr1 = Attr('control-group')
    #    attr1 += 'hidden'
    #    attr2 = Attr('hidden')
    #    attr2 += 'control-group'
    #    assert str(attr1) == str(attr2) == 'control-group hidden'


class Test_Attrs:
    def test_escape(self):
        attrs = Attrs({'x': '"'})
        assert str(attrs) == 'x="&quot;"'


    def test_none(self):
        attrs = Attrs({'x': None})
        assert str(attrs) == ''


    def test_booleans(self):
        attrs = Attrs({'x': True, 'y': False})
        assert str(attrs['x']) == '1'
        assert attrs['y'] is False
        assert str(attrs) == 'x="1"'


    def test_numerals(self):
        attrs = Attrs({'x': 7.3, 'y': 25, 'z': -8})
        assert str(attrs['x']) == '7.3'
        assert str(attrs['y']) == '25'
        assert str(attrs['z']) == '-8'
        assert str(attrs) == 'x="7.3" y="25" z="-8"'


    def test_undescore_prefix(self):
        attrs = Attrs({'_x': 'ok'})
        assert str(attrs['_x']) == 'ok'
        assert 'x' not in attrs
        assert str(attrs) == ''


    def test_underscore_suffix(self):
        attrs = Attrs({'x_': 'ok'})
        assert str(attrs['x_']) == str(attrs['x']) == 'ok'
        assert str(attrs) == 'x="ok"'


    def test_take_prefixed(self):
        attrs_dict = {'class': 'test'}
        attrs_obj = Attrs.take_prefixed(attrs_dict, 'control-group-')
        assert attrs_dict == {'class': 'test'}
        assert attrs_obj == {}

        attrs_dict = {'class': 'test1', 'control-group-class': 'test2'}
        attrs_obj = Attrs.take_prefixed(attrs_dict, 'control-group-')
        assert attrs_dict == {'class': 'test1'}
        assert attrs_obj == {'class': 'test2'}


    def test_attr_autogen(self):
        attrs = Attrs()
        assert str(' hidden ' + attrs['class']) == 'hidden'
        assert str(attrs['class'] + ' hidden ') == 'hidden'

        attrs = Attrs({'class_': 'test'})
        assert str(attrs['class'] + ' hidden ') == 'test hidden'
        assert str(' hidden ' + attrs['class']) == 'hidden test'

        attrs = Attrs({'class_': 'test'})
        assert str(attrs['class'] + 'hidden') == 'test hidden'
        assert str('hidden' + attrs['class']) == 'hidden test'


def test_render_prepend_attrs_empty():
    attrs = {
    }
    assert clean(render_prepend(attrs)) == clean("")


def test_render_prepend_attrs_prepend_only():
    attrs = {
        'prepend': '-prepend-',
    }
    assert clean(render_prepend(attrs)) == clean("""<div class="input-prepend"><span class="add-on">-prepend-</span>""")


def test_render_prepend_attrs_append_only():
    attrs = {
        'append': '-append-',
    }
    assert clean(render_prepend(attrs)) == clean("""<div class="input-append">""")


def test_render_prepend_attrs_prepend_and_append():
        attrs = {
            'prepend': '-prepend-',
            'append': '-append-',
        }
        assert clean(render_prepend(attrs)) == clean("""<div class="input-append input-prepend"><span class="add-on">-prepend-</span>""")


def test_render_append_attrs_empty():
    attrs = {
    }
    assert clean(render_append(attrs)) == clean("")


def test_render_append_attrs_prepend_only():
    attrs = {
        'prepend': '-prepend-',
    }
    assert clean(render_append(attrs)) == clean("""</div>""")


def test_render_append_attrs_append_only():
    attrs = {
        'append': '-append-',
    }
    assert clean(render_append(attrs)) == clean("""<span class="add-on">-append-</span></div>""")


def test_render_append_attrs_prepend_and_append():
        attrs = {
            'prepend': '-prepend-',
            'append': '-append-',
        }
        assert clean(render_append(attrs)) == clean("""<span class="add-on">-append-</span></div>""")
