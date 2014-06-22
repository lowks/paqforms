from unittest.mock import Mock
from nose.tools import assert_raises

from paqforms4.bootstrap import *
from . import clean


class Test_Text:
    def __init__(self):
        self.widget = TextWidget('Username')
        self.field = Mock()
        self.field.widget = self.widget
        self.field.__class__.__name__ = 'Str'
        self.field.name = 'username'
        self.field.fullname = 'username'
        self.field.required = False
        self.field.validators = []
        self.field.has_error = False
        self.field.messages = {}

    def test_call_empty_value(self):
        self.field.format = lambda: ''
        assert clean("""<input id="username" name="username" type="text" value=""/>""") in clean(self.widget(self.field))

    def test_call_ok_value(self):
        self.field.format = lambda: 'gizmo'
        assert clean("""<input id="username" name="username" type="text" value="gizmo"/>""") in clean(self.widget(self.field))

    def test_call_html_entity_value(self):
        self.field.format = lambda: '"'
        assert clean("""<input id="username" name="username" type="text" value="&quot;"/>""") in clean(self.widget(self.field))

    def test_call_render(self):
        self.field.format = lambda: 'gizmo'
        assert clean(self.widget(self.field)) == clean(
            """
            <div class="control-group" data-name="username" data-widget="Text" id="group-username">
                <label class="control-label" for="username">Username</label>
                <div class="controls">
                    <input id="username" name="username" type="text" value="gizmo"/>
                </div>
            </div>
            """
        )

    def test_call_custom_attrs(self):
        self.field.value = []
        assert 'class="my-class"' in self.widget(self.field, attrs={'class': 'my-class'}) # TODO add count

class Test_Password:
    def __init__(self):
        self.widget = PasswordWidget('Password')
        self.field = Mock()
        self.field.widget = self.widget
        self.field.__class__.__name__ = 'Password'
        self.field.name = 'password'
        self.field.fullname = 'password'
        self.field.required = False
        self.field.validators = []
        self.field.has_error = False
        self.field.messages = {}

    def test_call_empty_value(self):
        self.field.format = lambda: ''
        assert clean("""<input id="password" name="password" type="password" value=""/>""") in clean(self.widget(self.field))

    def test_call_ok_value(self):
        self.field.format = lambda: 'gizmo'
        assert clean("""<input id="password" name="password" type="password" value="gizmo"/>""") in clean(self.widget(self.field))

    def test_call_html_entity_value(self):
        self.field.format = lambda: '"'
        assert clean("""<input id="password" name="password" type="password" value="&quot;"/>""") in clean(self.widget(self.field))

    def test_call_render(self):
        self.field.format = lambda: 'gizmo'
        assert clean(self.widget(self.field)) == clean(
            """
            <div class="control-group" data-name="password" data-widget="Password" id="group-password">
                <label class="control-label" for="password">Password</label>
                <div class="controls">
                    <input id="password" name="password" type="password" value="gizmo"/>
                </div>
            </div>
            """
        )

    def test_call_custom_attrs(self):
        self.field.value = []
        assert 'class="my-class"' in self.widget(self.field, attrs={'class': 'my-class'}) # TODO add count

class Test_Textarea:
    def __init__(self):
        self.widget = TextareaWidget('Comment')
        self.field = Mock()
        self.field.widget = self.widget
        self.field.__class__.__name__ = 'Textarea'
        self.field.name = 'comment'
        self.field.fullname = 'comment'
        self.field.required = False
        self.field.validators = []
        self.field.has_error = False
        self.field.messages = {}

    def test_call_empty_value(self):
        self.field.format = lambda: ''
        assert clean("""<textarea id="comment" name="comment"></textarea>""") in clean(self.widget(self.field))

    def test_call_ok_value(self):
        self.field.format = lambda: 'gizmo'
        assert clean("""<textarea id="comment" name="comment">gizmo</textarea>""") in clean(self.widget(self.field))

    def test_call_html_entity_value(self):
        self.field.format = lambda: '"'
        assert clean("""<textarea id="comment" name="comment">&quot;</textarea>""") in clean(self.widget(self.field))

    def test_call_render(self):
        self.field.format = lambda: 'gizmo'
        assert clean(self.widget(self.field)) == clean(
            """
            <div class="control-group" data-name="comment" data-widget="Textarea" id="group-comment">
                <label class="control-label" for="comment">Comment</label>
                <div class="controls">
                    <textarea id="comment" name="comment">gizmo</textarea>
                </div>
            </div>
            """
        )

    def test_call_custom_attrs(self):
        self.field.value = []
        assert 'class="my-class"' in self.widget(self.field, attrs={'class': 'my-class'}) # TODO add count

class Test_Checkbox:
    def __init__(self):
        self.widget = CheckboxWidget('Agree')
        self.field = Mock()
        self.field.widget = self.widget
        self.field.__class__.__name__ = 'Checkbox'
        self.field.name = 'agree'
        self.field.fullname = 'agree'
        self.field.required = False
        self.field.validators = []
        self.field.has_error = False
        self.field.messages = {}

    def test_call_true_value(self):
        self.field.format = lambda: '1'
        assert (
            clean("""
            <input checked="1" id="agree" name="agree" type="checkbox" value="1"/>
            """) in clean(self.widget(self.field))
        )

    def test_call_false_value(self):
        self.field.value = False
        assert (
            clean("""
            <input id="agree" name="agree" type="checkbox" value="1"/>
            """) in clean(self.widget(self.field))
        )

    def test_call_render(self):
        self.field.format = lambda: '1'
        assert clean(self.widget(self.field)) == clean(
            """
            <div class="control-group" data-name="agree" data-widget="Checkbox" id="group-agree">
                <div class="controls">
                    <label class="checkbox control-label" for="agree">
                        <input checked="1" id="agree" name="agree" type="checkbox" value="1"/>
                        Agree
                    </label>
                </div>
            </div>
            """
        )

    def test_call_custom_attrs(self):
        self.field.format = lambda: False
        assert 'class="my-class"' in self.widget(self.field, attrs={'class': 'my-class'}) # TODO add count

class Test_Select:
    def __init__(self):
        self.widget = SelectWidget('Great House', options=['Baratheons', 'Lannisters', 'Starks'])
        self.field = Mock()
        self.field.widget = self.widget
        self.field.__class__.__name__ = 'Select'
        self.field.name = 'greathouse'
        self.field.fullname = 'greathouse'
        self.field.required = False
        self.field.validators = []
        self.field.has_error = False
        self.field.messages = {}
        self.field.choices = ['baratheons', 'lannisters', 'starks']
        self.field.format_value = lambda value: value
        self.field.is_chosen = lambda value: value == self.field.value

    def test_call_empty_value(self):
        self.field.value = None
        assert (
            clean("""
            <select id="greathouse" name="greathouse">
                <option value="baratheons">Baratheons</option>
                <option value="lannisters">Lannisters</option>
                <option value="starks">Starks</option>
            </select>
            """) in clean(self.widget(self.field))
        )

    def test_call_absend_value(self):
        self.field.value = 'tally'
        assert (
            clean("""
            <select id="greathouse" name="greathouse">
                <option value="baratheons">Baratheons</option>
                <option value="lannisters">Lannisters</option>
                <option value="starks">Starks</option>
            </select>
            """) in clean(self.widget(self.field))
        )

    def test_call_ok_value(self):
        self.field.value = 'lannisters'
        assert (
            clean("""
            <select id="greathouse" name="greathouse">
                <option value="baratheons">Baratheons</option>
                <option selected="1" value="lannisters">Lannisters</option>
                <option value="starks">Starks</option>
            </select>
            """) in clean(self.widget(self.field))
        )

    def test_call_html_entity_value(self):
        """
        Never use unsafe HTML values (& will be converterd to &amp; on render therefore losing the POST <=> MODEL relation)
        """
        pass

    def test_call_render(self):
        self.field.value = None
        assert clean(self.widget(self.field)) == clean("""
            <div class="control-group" data-name="greathouse" data-widget="Select" id="group-greathouse">
                <label class="control-label" for="greathouse">Great House</label>
                <div class="controls">
                    <select id="greathouse" name="greathouse">
                        <option value="baratheons">Baratheons</option>
                        <option value="lannisters">Lannisters</option>
                        <option value="starks">Starks</option>
                    </select>
                </div>
            </div>
            """
        )

    def test_call_custom_attrs(self):
        self.field.value = []
        assert 'class="my-class"' in self.widget(self.field, attrs={'class': 'my-class'}) # TODO add count

class Test_MultiSelect:
    def __init__(self):
        self.widget = SelectWidget('Great Houses', multiple=True, options=['Baratheons', 'Lannisters', 'Starks'])
        self.field = Mock()
        self.field.widget = self.widget
        self.field.__class__.__name__ = 'MultiSelect'
        self.field.name = 'greathouses'
        self.field.fullname = 'greathouses'
        self.field.required = False
        self.field.validators = []
        self.field.has_error = False
        self.field.messages = {}
        self.field.choices = ['baratheons', 'lannisters', 'starks']
        self.field.format_value = lambda value: value
        self.field.is_chosen = lambda value: value in self.field.value

    def test_call_empty_value(self):
        self.field.value = []
        assert (
            clean(
            """
            <select id="greathouses" multiple="1" name="greathouses">
                <option value="baratheons">Baratheons</option>
                <option value="lannisters">Lannisters</option>
                <option value="starks">Starks</option>
            </select>
            """) in clean(self.widget(self.field))
    )

    def test_call_absend_value(self):
        self.field.value = ['tally']
        assert (
            clean(
                """
                <select id="greathouses" multiple="1" name="greathouses">
                    <option value="baratheons">Baratheons</option>
                    <option value="lannisters">Lannisters</option>
                    <option value="starks">Starks</option>
                </select>
                """
            ) in clean(self.widget(self.field))
        )

    def test_call_ok_value(self):
        self.field.value = ['lannisters', 'starks']
        assert (
            clean(
                """
                <select id="greathouses" multiple="1" name="greathouses">
                    <option value="baratheons">Baratheons</option>
                    <option selected="1" value="lannisters">Lannisters</option>
                    <option selected="1" value="starks">Starks</option>
                </select>
                """
            ) in clean(self.widget(self.field))
        )

    def test_call_html_entity_value(self):
        """
        Never use unsafe HTML values (& will be converterd to &amp; on render therefore losing the POST <=> MODEL relation)
        """
        pass

    def test_call_basic(self):
        self.field.value = []
        assert clean(self.widget(self.field)) == clean("""
            <div class="control-group" data-name="greathouses" data-widget="Select" id="group-greathouses">
                <label class="control-label" for="greathouses">Great Houses</label>
                <div class="controls">
                    <select id="greathouses" multiple="1" name="greathouses">
                        <option value="baratheons">Baratheons</option>
                        <option value="lannisters">Lannisters</option>
                        <option value="starks">Starks</option>
                    </select>
                </div>
            </div>
            """
        )

    def test_call_custom_attrs(self):
        self.field.value = []
        assert 'class="my-class"' in self.widget(self.field, attrs={'class': 'my-class'}) # TODO add count

class Test_MultiCheckbox:
    def __init__(self):
        self.widget = MultiCheckboxWidget('Great Houses', options=['Baratheons', 'Lannisters', 'Starks'])
        self.field = Mock()
        self.field.widget = self.widget
        self.field.__class__.__name__ = 'MultiCheckbox'
        self.field.name = 'greathouses'
        self.field.fullname = 'greathouses'
        self.field.required = False
        self.field.validators = []
        self.field.has_error = False
        self.field.messages = {}
        self.field.choices = ['baratheons', 'lannisters', 'starks']
        self.field.format_value = lambda value: value
        self.field.is_chosen = lambda value: value in self.field.value

    def test_call_empty_value(self):
        self.field.value = []
        assert (
            clean("""<input id="greathouses-baratheons" name="greathouses-1" type="checkbox" value="baratheons"/>""")
            in clean(self.widget(self.field))
        )
        assert (
            clean("""<input id="greathouses-lannisters" name="greathouses-2" type="checkbox" value="lannisters"/>""")
            in clean(self.widget(self.field))
        )
        assert (
            clean("""<input id="greathouses-starks" name="greathouses-3" type="checkbox" value="starks"/>""")
            in clean(self.widget(self.field))
        )

    def test_call_absend_value(self):
        self.field.value = ['tally']
        assert (
            clean("""<input id="greathouses-baratheons" name="greathouses-1" type="checkbox" value="baratheons"/>""")
            in clean(self.widget(self.field))
        )
        assert (
            clean("""<input id="greathouses-lannisters" name="greathouses-2" type="checkbox" value="lannisters"/>""")
            in clean(self.widget(self.field))
        )
        assert (
            clean("""<input id="greathouses-starks" name="greathouses-3" type="checkbox" value="starks"/>""")
            in clean(self.widget(self.field))
        )

    def test_call_ok_value(self):
        self.field.value = ['lannisters', 'starks']
        assert (
            clean("""<input id="greathouses-baratheons" name="greathouses-1" type="checkbox" value="baratheons"/>""")
            in clean(self.widget(self.field))
        )
        assert (
            clean("""<input checked="1" id="greathouses-lannisters" name="greathouses-2" type="checkbox" value="lannisters"/>""")
            in clean(self.widget(self.field))
        )
        assert (
            clean("""<input checked="1" id="greathouses-starks" name="greathouses-3" type="checkbox" value="starks"/>""")
            in clean(self.widget(self.field))
        )

    def test_call_html_entity_value(self):
        """
        Never use unsafe HTML values (& will be converterd to &amp; on render therefore losing the POST <=> MODEL relation)
        """
        pass

    def test_call_basic(self):
        self.field.value = []
        assert clean(self.widget(self.field)) == clean(
            """
            <div class="control-group" data-name="greathouses" data-widget="MultiCheckbox" id="group-greathouses">
                <fieldset>
                    <legend>
                        <label class="checkbox control-label" for="greathouses">
                            <input data-tag="toggler" id="greathouses" type="checkbox"/>
                            Great Houses
                        </label>
                    </legend>
                    <div class="controls">
                        <label class="checkbox control-label" for="greathouses-baratheons">
                            <input id="greathouses-baratheons" name="greathouses-1" type="checkbox" value="baratheons"/>
                            Baratheons
                        </label>
                    </div>
                    <div class="controls">
                        <label class="checkbox control-label" for="greathouses-lannisters">
                            <input id="greathouses-lannisters" name="greathouses-2" type="checkbox" value="lannisters"/>
                            Lannisters
                        </label>
                    </div>
                    <div class="controls">
                        <label class="checkbox control-label" for="greathouses-starks">
                            <input id="greathouses-starks" name="greathouses-3" type="checkbox" value="starks"/>
                            Starks
                        </label>
                    </div>
                </fieldset>
            </div>
            """
        )

    def test_call_custom_attrs(self):
        self.field.value = []
        assert 'class="my-class"' in self.widget(self.field, attrs={'class': 'my-class'}) # TODO add count

# TODO test error output