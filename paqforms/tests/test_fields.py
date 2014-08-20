import decimal
import datetime
import babel.support; nt = babel.support.NullTranslations()

from collections import OrderedDict
from werkzeug.datastructures import MultiDict
from unittest.mock import Mock
from nose.tools import assert_raises

from paqforms.converters import *
from paqforms.helpers import *
from paqforms.validators import *
from paqforms.fields import Field, FieldField, FormField
from paqforms.fields import *


class Post:
    def __init__(self, content=None, comments=[], tags=[]):
        self.content = content
        self.comments = comments
        self.tags = tags

class Comment:
    def __init__(self, content=None):
        self.content = content


# `dict` models
comment_content_field = Field('content', default='...', required=True, converters=StrConverter(), name='content')
comment_form = FormField(
    'comment', [comment_content_field], name='comment'
)

post_content_field = Field('content', default='...', required=True, converters=StrConverter(), name='content')
post_comments_field = FieldField('comments', comment_form, name='comments')
post_tag_field = Field('tag', converters=StrConverter(), name='tag')
post_tags_field = FieldField('tags', post_tag_field, name='tags')
post_form = FormField(
    'post', [post_content_field, post_tags_field, post_comments_field], name='post'
)

# `object` models
Comment_content_field = Field('content', default='...', required=True, converters=StrConverter(), name='content')
Comment_form = FormField(
    'comment', [Comment_content_field], default=lambda: Comment(), name='comment'
)

Post_content_field = Field('content', default='...', required=True, converters=StrConverter(), name='content')
Post_comments_field = FieldField('comments', Comment_form, name='comments')
Post_tag_field = Field('tag', converters=StrConverter(), name='tag')
Post_tags_field = FieldField('tags', Post_tag_field, name='tags')
Post_form = FormField(
    'post', [Post_content_field, Post_comments_field, Post_tags_field], default=lambda: Post(), name='post'
)


class Test_Field:
    def test_feed(self):
        # returns self
        field = Field('something', converters=StrConverter()).feed(value='x', data=None)
        assert field.feed_value == 'x'
        assert not field.feed_data

        # replaces previous
        field.feed(None, data='y')
        assert not field.feed_value
        assert field.feed_data == 'y'

        # has 2 arguments: value and data
        field.feed(value='x', data='y')
        assert field.feed_value == 'x'
        assert field.feed_data == 'y'

    def test_feed_nothing(self):
        """
        No data means no validation at all
        Values stick to defaults
        """
        # required & implicit default
        field = Field('', required=True, converters=StrConverter()).feed(None)
        assert field.value is None
        assert not field.messages.get('error')

        # optional & implicit default
        field = Field('', required=False, converters=StrConverter()).feed(None)
        assert field.value is None
        assert not field.messages.get('error')

        # required & explicit default
        field = Field('', default='xxx', required=True, converters=StrConverter()).feed(None)
        assert field.value == 'xxx'
        assert not field.messages.get('error')

        # optional & explicit default
        field = Field('', default='xxx', required=False, converters=StrConverter())
        field.feed(None)
        assert field.value == 'xxx'
        assert not field.messages.get('error')

    def test_feed_empty(self):
        """
        Validators are applicable to (is not None) values only
        """
        # required
        field = Field('', required=True, converters=StrConverter()).feed(None, data='', submit=True)
        assert field.messages.get('error')

        # optional
        field = Field('', required=False, converters=StrConverter()).feed(None, data='', submit=True)
        assert field.value is None
        assert not field.messages.get('error')

    def test_feed_data(self):
        """
        Fields lose `.value` at errors
        """
        # valid
        field = Field('', required=True, converters=IntConverter()).feed(None, data='125', submit=True)
        assert field.value == 125
        assert not field.messages.get('error')

        # invalid
        field = Field('', required=True, converters=IntConverter()).feed(None, data='12d', submit=True)
        assert field.messages.get('error')

    def test_feed_value(self):
        """
        Paqforms do not validate `value`!
        """
        # valid
        field = Field('', required=True, converters=IntConverter())
        field.feed(value=125)
        assert field.value == 125
        assert not field.messages.get('error')

        # invalid
        field = Field('', required=True, converters=IntConverter())
        field.feed(value='12d')
        assert field.value == '12d'
        assert not field.messages.get('error')

    def test_feed_value_and_data(self):
        """
        `data` overrides `value`
        """
        # valid
        field = Field(TextWidget(''), converters=IntConverter(), required=True)
        field.feed(value=11, data='12', submit=True)
        assert field.value == 12
        assert not field.messages.get('error')

    def test_converters(self):
        a = Field(None, converters=StrConverter())


class Test_FieldField:
    def test_feed_save_input(self):
        field = Field('something', converters=StrConverter())
        field.feed(value=['x'])
        assert field.feed_value == ['x']
        assert not field.feed_data
        field.feed([], data=['y'])
        assert not field.feed_value
        assert field.feed_data == ['y']
        field.feed(value=['x'], data=['y'])
        assert field.feed_value == ['x']
        assert field.feed_data == ['y']

    def test_feed_nothing(self):
        # Comment
        post_tags_field.feed(None)
        assert post_tags_field.value == []

        # Post
        post_comments_field.feed(None)
        assert post_comments_field.value == []

    def test_feed_value(self):
        # Comment
        post_tags_field.feed(value=['tag1', 'tag2'])
        assert post_tags_field.value == ['tag1', 'tag2']
        assert post_tags_field.fields[0].value == 'tag1'
        assert post_tags_field.fields[1].value == 'tag2'
        assert len(post_tags_field.fields) == 2

        # Post
        post_comments_field.feed(value=[{'content': 'post-content1'}, {'content': 'post-content2'}])
        assert post_comments_field.value == [{'content': 'post-content1'}, {'content': 'post-content2'}]
        assert post_comments_field.fields[0].value == {'content': 'post-content1'}
        assert post_comments_field.fields[1].value == {'content': 'post-content2'}
        assert len(post_comments_field.fields) == 2

    def test_feed_data(self):
        # Comment
        post_tags_field.feed([], data=['tag1', 'tag2'], submit=True)
        assert post_tags_field.value == ['tag1', 'tag2']
        assert post_tags_field.fields[0].value == 'tag1'
        assert post_tags_field.fields[1].value == 'tag2'
        assert len(post_tags_field.fields) == 2

        # Post
        post_comments_field.feed([], data=[{'content': 'post-content1'}, {'content': 'post-content2'}], submit=True)
        assert post_comments_field.value == [{'content': 'post-content1'}, {'content': 'post-content2'}]
        assert post_comments_field.fields[0].value == {'content': 'post-content1'}
        assert post_comments_field.fields[1].value == {'content': 'post-content2'}
        assert len(post_comments_field.fields) == 2

    def test_feed_value_and_data(self):
        # Comment
        post_tags_field.feed(value=['tag1', 'tag2'], data=['tag1*', 'tag2*'], submit=True) # new data
        assert post_tags_field.value == ['tag1*', 'tag2*']
        assert post_tags_field.fields[0].value == 'tag1*'
        assert post_tags_field.fields[1].value == 'tag2*'
        assert len(post_tags_field.fields) == 2

        post_tags_field.feed(value=['tag1', 'tag2'], data=['tag1*'], submit=True) # shorter data
        assert post_tags_field.value == ['tag1*']

        post_tags_field.feed(value=['tag1', 'tag2'], data=['tag1*', 'tag2*', 'tag3*'], submit=True) # longer data
        assert post_tags_field.value == ['tag1*', 'tag2*', 'tag3*']

        # Post
        post_comments_field.feed( # new data
            value = [{'content': 'post-content1'}, {'content': 'post-content2'}],
            data = [{'content': 'post-content1*'}, {'content': 'post-content2*'}],
            submit = True
        )
        assert post_comments_field.value == [{'content': 'post-content1*'}, {'content': 'post-content2*'}]
        assert post_comments_field.fields[0].value == {'content': 'post-content1*'}
        assert post_comments_field.fields[1].value == {'content': 'post-content2*'}
        assert len(post_comments_field.fields) == 2

        post_comments_field.feed( # shorter data
            value = [{'content': 'post-content1'}, {'content': 'post-content2'}],
            data = [{'content': 'post-content1*'}],
            submit = True
        )
        assert post_comments_field.value == [{'content': 'post-content1*'}]


        post_comments_field.feed( # longer data
            value = [{'content': 'post-content1'}, {'content': 'post-content2'}],
            data = [{'content': 'post-content1*'}, {'content': 'post-content2*'}, {'content': 'post-content3*'}],
            submit = True
        )
        assert post_comments_field.value == [{'content': 'post-content1*'}, {'content': 'post-content2*'}, {'content': 'post-content3*'}]


class Test_FormField:
    def test_feed_save_input(self):
        field = Field('something', StrConverter())
        field.feed(value={'x': 'x'})
        assert field.feed_value == {'x': 'x'}
        assert not field.feed_data
        field.feed({}, data={'y': 'y'})
        assert not field.feed_value
        assert field.feed_data == {'y': 'y'}
        field.feed(value={'x': 'x'}, data={'y': 'y'})
        assert field.feed_value == {'x': 'x'}
        assert field.feed_data == {'y': 'y'}

    def test_feed_nothing(self):
        # Comment
        comment_form.feed({})
        assert comment_form.value == {'content': '...'}
        assert comment_form.fields['content'].value == '...'

        # Post
        post_form.feed({})
        assert post_form.value == {'content': '...', 'tags': [], 'comments': []}
        assert post_form.fields['content'].value == '...'
        assert post_form.fields['tags'].value == []
        assert post_form.fields['comments'].value == []

    def test_feed_nothing_objectify(self):
        # Comment
        Comment_form.feed(None)
        assert type(Comment_form.value) == Comment
        assert Comment_form.value.content == '...'

        # Post
        Post_form.feed(None)
        assert type(Post_form.value) == Post
        assert Post_form.value.content == '...'
        assert Post_form.value.tags == []
        assert Post_form.value.comments == []

    def test_feed_dict_value(self):
        # Comment
        comment_form.feed(value={'content': 'content'})
        assert comment_form.value == {'content': 'content'}
        assert comment_form.fields['content'].value == 'content'

        # Post
        post_form.feed(value={'content': 'post-content', 'tags': ['tag1', 'tag2'], 'comments': [{'content': 'comment-content1'}, {'content': 'comment-content2'}]})
        assert post_form.value == {'content': 'post-content', 'tags': ['tag1', 'tag2'], 'comments': [{'content': 'comment-content1'}, {'content': 'comment-content2'}]}
        assert post_form.fields['content'].value == 'post-content'
        assert post_form.fields['tags'].value == ['tag1', 'tag2']
        assert post_form.fields['tags'].fields[0].value == 'tag1'
        assert post_form.fields['tags'].fields[1].value == 'tag2'
        assert len(post_form.fields['tags'].fields) == 2
        assert post_form.fields['comments'].value == [{'content': 'comment-content1'}, {'content': 'comment-content2'}]
        assert post_form.fields['comments'].fields[0].value == {'content': 'comment-content1'}
        assert post_form.fields['comments'].fields[1].value == {'content': 'comment-content2'}
        assert post_form.fields['comments'].fields[0].fields['content'].value == 'comment-content1'
        assert post_form.fields['comments'].fields[1].fields['content'].value == 'comment-content2'
        assert len(post_form.fields['comments'].fields) == 2

    def test_feed_obj_value(self):
        # Comment
        comment_form.feed(value=Comment(content='comment-content'))
        assert type(comment_form.value) == Comment
        assert comment_form.value.content == 'comment-content'
        assert comment_form.fields['content'].value == 'comment-content'

        # Post
        post_form.feed(value=Post(content='post-content', tags=['tag1', 'tag2'], comments=[Comment(content='comment-content1'), Comment(content='comment-content2')]))
        assert type(post_form.value) == Post
        assert post_form.value.content == 'post-content'
        assert post_form.value.tags == ['tag1', 'tag2']
        assert type(post_form.value.comments[0]) == Comment
        assert type(post_form.value.comments[1]) == Comment
        assert post_form.value.comments[0].content == 'comment-content1'
        assert post_form.value.comments[1].content == 'comment-content2'
        assert len(post_form.value.comments) == 2

    def test_feed_dictdata(self):
        # Comment
        comment_form.feed({}, {'content': 'content'}, submit=True)
        assert comment_form.value == {'content': 'content'}
        assert comment_form.fields['content'].value == 'content'

        # Post
        post_form.feed({}, {'content': 'post-content', 'tags': ['tag1', 'tag2'], 'comments': [{'content': 'comment-content1'}, {'content': 'comment-content2'}]}, submit=True)
        assert post_form.value == {'content': 'post-content', 'tags': ['tag1', 'tag2'], 'comments': [{'content': 'comment-content1'}, {'content': 'comment-content2'}]}
        assert post_form.fields['content'].value == 'post-content'
        assert post_form.fields['tags'].value == ['tag1', 'tag2']
        assert post_form.fields['tags'].fields[0].value == 'tag1'
        assert post_form.fields['tags'].fields[1].value == 'tag2'
        assert len(post_form.fields['tags'].fields) == 2
        assert post_form.fields['comments'].value == [{'content': 'comment-content1'}, {'content': 'comment-content2'}]
        assert post_form.fields['comments'].fields[0].value == {'content': 'comment-content1'}
        assert post_form.fields['comments'].fields[1].value == {'content': 'comment-content2'}
        assert post_form.fields['comments'].fields[0].fields['content'].value == 'comment-content1'
        assert post_form.fields['comments'].fields[1].fields['content'].value == 'comment-content2'
        assert len(post_form.fields['comments'].fields) == 2

    def test_feed_objdata(self):
        # Comment
        comment_form.feed({}, data=Comment(content='content'), submit=True)
        assert comment_form.value == {'content': 'content'}

        # Post
        post_form.feed({}, data=Post(content='post-content', tags=['tag1', 'tag2'], comments=[Comment(content='comment-content1'), Comment(content='comment-content2')]), submit=True)
        assert post_form.value == {'content': 'post-content', 'tags': ['tag1', 'tag2'], 'comments': [{'content': 'comment-content1'}, {'content': 'comment-content2'}]}
        assert post_form.fields['content'].value == 'post-content'
        assert post_form.fields['tags'].value == ['tag1', 'tag2']
        assert post_form.fields['tags'].fields[0].value == 'tag1'
        assert post_form.fields['tags'].fields[1].value == 'tag2'
        assert len(post_form.fields['tags'].fields) == 2
        assert post_form.fields['comments'].value == [{'content': 'comment-content1'}, {'content': 'comment-content2'}]
        assert post_form.fields['comments'].fields[0].value == {'content': 'comment-content1'}
        assert post_form.fields['comments'].fields[1].value == {'content': 'comment-content2'}
        assert post_form.fields['comments'].fields[0].fields['content'].value == 'comment-content1'
        assert post_form.fields['comments'].fields[1].fields['content'].value == 'comment-content2'
        assert len(post_form.fields['comments'].fields) == 2

    def test_feed_value_and_data(self):
        # Comment
        comment_form.feed(value={'content': 'content'}, data={'content': 'content*'}, submit=True)
        assert comment_form.value == {'content': 'content*'}
        assert comment_form.fields['content'].value == 'content*'

        # Post
        post_form.feed(
            value = {'content': 'post-content', 'tags': ['tag1', 'tag2'], 'comments': [{'content': 'comment-content1'}, {'content': 'comment-content2'}]},
            data = {'content': 'post-content*', 'tags': ['tag1*', 'tag2*', 'tag3*'], 'comments': [{'content': 'comment-content1*'}]},
            submit = True
        )
        assert post_form.value == {'content': 'post-content*', 'tags': ['tag1*', 'tag2*', 'tag3*'], 'comments': [{'content': 'comment-content1*'}]}
        assert post_form.fields['content'].value == 'post-content*'
        assert post_form.fields['tags'].value == ['tag1*', 'tag2*', 'tag3*']
        assert post_form.fields['tags'].fields[0].value == 'tag1*'
        assert post_form.fields['tags'].fields[1].value == 'tag2*'
        assert post_form.fields['tags'].fields[2].value == 'tag3*'
        assert len(post_form.fields['tags'].fields) == 3
        assert post_form.fields['comments'].value == [{'content': 'comment-content1*'}]
        assert post_form.fields['comments'].fields[0].value == {'content': 'comment-content1*'}
        assert post_form.fields['comments'].fields[0].fields['content'].value == 'comment-content1*'
        assert len(post_form.fields['comments'].fields) == 1

    def test_feed_value_and_data_objectify(self):
        # Comment
        Comment_form.feed(value=Comment(content='content'), data={'content': 'content*'}, submit=True)
        assert type(Comment_form.value) == Comment
        assert Comment_form.value.content == 'content*'

        # Post
        Post_form.feed(
            value = Post(content='post-content', tags=['tag1', 'tag2'], comments=[Comment(content='comment-content1'), Comment(content='comment-content2')]),
            data = {'content': 'post-content*', 'tags': ['tag1*', 'tag2*', 'tag3*'], 'comments': [{'content': 'comment-content1*'}]},
            submit = True
        )
        assert type(Post_form.value) == Post
        assert Post_form.value.content == 'post-content*'
        assert Post_form.value.tags == ['tag1*', 'tag2*', 'tag3*']
        assert type(Post_form.value.comments[0]) == Comment
        assert Post_form.value.comments[0].content == 'comment-content1*'
        assert len(Post_form.value.comments) == 1

    def test_feed_partial_data(self):
        post_form.feed(
            value = {'content': 'post-content', 'tags': ['tag1', 'tag2'], 'comments': [{'content': 'comment-content1'}, {'content': 'comment-content2'}]},
            data = {'content': 'post-content*', 'tags': [], 'comments': []},
            submit = True
        )
        assert post_form.value == {
            'content': 'post-content*',
            'tags': [],
            'comments': [],
        }

    def test_feed_partial_form(self):
        value = {
            'id': 1,
            'username': 'some-username',
            'password': 'some-password',
        }
        password_field = Field('password', name='password')
        password_edit_form = FormField('password_edit', [password_field])
        password_edit_form.feed(
            value = value,
            data = {'password': 'new-password'},
            submit = True
        )
        assert password_edit_form.value == {
            'id': 1,
            'username': 'some-username',
            'password': 'new-password',
        }

    def test_feed_unknown_data(self):
        comment_form.feed({}, data={'content': 'content', 'hack': True}, submit=True)
        assert comment_form.value == {'content': 'content'}
        assert comment_form.fields['content'].value == 'content'
        assert not 'hack' in comment_form.fields

    def test_form_argument(self):
        a = Field(None)
        b = Field(None)
        form1 = FormField(None, OrderedDict([('a', a), ('b', b)]))
        assert form1.prototypes['a'] == a
        assert form1.prototypes['b'] == b
        form2 = FormField(None, form1)
        assert form2.prototypes['a'] == a
        assert form2.prototypes['b'] == b


class Test_Form:
    def test_declaration(self):
        class TestForm(BaseForm):
            a = Field(None, converters=StrConverter(), default='xyz')
            b = Field(None, converters=IntConverter(), default=123)
            c = Field(None, converters=BoolConverter(), default=True)

        assert len(TestForm.prototypes) == 3

        assert type(TestForm.prototypes['a']) == Field
        assert type(TestForm.prototypes['b']) == Field
        assert type(TestForm.prototypes['c']) == Field

        assert TestForm.prototypes['a'].name == 'a'
        assert TestForm.prototypes['b'].name == 'b'
        assert TestForm.prototypes['c'].name == 'c'

        assert not hasattr(TestForm, 'a')
        assert not hasattr(TestForm, 'b')
        assert not hasattr(TestForm, 'c')

    def test_instantiation(self):
        class TestForm(BaseForm):
            a = Field(None, converters=StrConverter(), default='xyz')
            b = Field(None, converters=IntConverter(), default=123)
            c = Field(None, converters=BoolConverter(), default=True)

        form = TestForm({})
        form2 = TestForm({})

        assert form.fields['a'] != form2.fields['a']
        assert form.fields['b'] != form2.fields['b']
        assert form.fields['c'] != form2.fields['c']

        assert form.fields['a'].name == form2.fields['a'].name == 'a'
        assert form.fields['b'].name == form2.fields['b'].name == 'b'
        assert form.fields['c'].name == form2.fields['c'].name == 'c'

        assert len(TestForm.prototypes) == 3
        assert len(form.prototypes) == 3

        assert TestForm.prototypes == form.prototypes

        assert type(form.fields['a']) == type(form.prototypes['a'])
        assert type(form.fields['b']) == type(form.prototypes['b'])
        assert type(form.fields['c']) == type(form.prototypes['c'])

        assert form.fields['a'] != form.prototypes['a']
        assert form.fields['b'] != form.prototypes['b']
        assert form.fields['c'] != form.prototypes['c']

        assert not hasattr(TestForm, 'a')
        assert not hasattr(TestForm, 'b')
        assert not hasattr(TestForm, 'c')

        assert not hasattr(form, 'a')
        assert not hasattr(form, 'b')
        assert not hasattr(form, 'c')

    def test_declaration_complex_example(self):
        class CommentForm(BaseForm):
            content = Field(None)

        assert CommentForm.prototypes['content'].name == 'content'
        assert len(CommentForm.prototypes) == 1
        assert type(CommentForm.prototypes['content']) == Field

        class PostForm(BaseForm):
            content = Field(None)
            comments = FieldField(None, FormField(None, prototypes=CommentForm)) # TODO check FieldField(CommentForm)
            tags = FieldField(None, Field(None))

        assert PostForm.prototypes['content'].name == 'content'
        assert PostForm.prototypes['comments'].name == 'comments'
        assert PostForm.prototypes['tags'].name == 'tags'
        assert len(PostForm.prototypes) == 3

    def test_instantiation_complex_example(self):
        class CommentForm(BaseForm):
            content = Field(None)

        form = CommentForm({})

        assert form.prototypes['content'].name == 'content'
        assert len(form.prototypes) == 1
        assert type(form.fields['content']) == type(form.prototypes['content'])
        assert form.fields['content'] != form.prototypes['content']

        class PostForm(BaseForm):
            content = Field(None)
            comments = FieldField(None, prototype=FormField(None, prototypes=CommentForm))
            tags = FieldField(None, Field(None))

        form = PostForm({})

        assert form.prototypes['content'].name == 'content'
        assert form.prototypes['comments'].name == 'comments'
        assert form.prototypes['tags'].name == 'tags'
        assert len(form.prototypes) == 3
        assert type(form.prototypes['content']) == type(form.fields['content'])
        assert form.prototypes['content'] != form.fields['content']
        assert type(form.prototypes['comments']) == type(form.fields['comments'])
        assert form.prototypes['comments'] != form.fields['comments']
        assert type(form.prototypes['tags']) == type(form.fields['tags'])
        assert form.prototypes['tags'] != form.fields['tags']

    def test_iteration(self):
        class TestForm(BaseForm):
            a = Field(None)
            b = Field(None)
            c = Field(None)

        form = TestForm({})

        assert OrderedDict(TestForm) == TestForm.prototypes
        assert OrderedDict(form) == form.fields

    def test_inheritance_classes(self):
        class TestForm1(BaseForm):
            email = Field(None, converters=StrConverter(), default='default-email')

        class TestForm2(TestForm1):
            job = Field(None, converters=StrConverter(), default='default-job')

        class TestForm3(TestForm2):
            email = Field(None, converters=StrConverter(), default='default-email-override')

        assert TestForm2.prototypes['email'] == TestForm1.prototypes['email']
        assert TestForm3.prototypes['job'] == TestForm2.prototypes['job']
        assert TestForm3.prototypes['email'] != TestForm1.prototypes['email']

        assert TestForm1.prototypes['email'].default == 'default-email'
        assert TestForm2.prototypes['email'].default == 'default-email'
        assert TestForm2.prototypes['job'].default == 'default-job'
        assert TestForm3.prototypes['email'].default == 'default-email-override'
        assert TestForm3.prototypes['job'].default == 'default-job'

    def test_multi_inheritance_classes(self):
        class TestForm1(BaseForm):
            email = Field(None, converters=StrConverter())

        class TestForm2(BaseForm):
            job = Field(None, converters=StrConverter())

        class TestForm3(TestForm1, TestForm2):
            skype = Field(None, converters=StrConverter())

        assert list(TestForm3.prototypes.keys()) == ['email', 'job', 'skype']

    def test_inheritance_objects(self):
        class TestForm1(BaseForm):
            email = Field(None, converters=StrConverter(), default='default-email')

        class TestForm2(TestForm1):
            job = Field(None, converters=StrConverter(), default='default-job')

        class TestForm3(TestForm2):
            email = Field(None, converters=StrConverter(), default='default-email-override')

        # Test objects
        form1 = TestForm1({})
        form2 = TestForm2({})
        form3 = TestForm3({})

        assert form2.prototypes['email'] == form1.prototypes['email']
        assert form3.prototypes['job'] == form2.prototypes['job']
        assert form3.prototypes['email'] != form1.prototypes['email']

        assert form1.prototypes['email'].default == 'default-email'
        assert form2.prototypes['email'].default == 'default-email'
        assert form2.prototypes['job'].default == 'default-job'
        assert form3.prototypes['email'].default == 'default-email-override'
        assert form3.prototypes['job'].default == 'default-job'

    def test_setattr_classes(self):
        email_field_in_Form1 = Field(None)
        job_field_in_Form2 = Field(None)
        email_field_in_Form3 = Field(None)

        class TestForm1(BaseForm):
            email = email_field_in_Form1

        class TestForm2(TestForm1):
            job = job_field_in_Form2

        class TestForm3(TestForm2):
            email = email_field_in_Form3

        assert TestForm1.prototypes['email'] == email_field_in_Form1
        assert list(TestForm1.prototypes.keys()) == ['email']
        assert TestForm2.prototypes['email'] == email_field_in_Form1
        assert TestForm2.prototypes['job'] == job_field_in_Form2
        assert list(TestForm2.prototypes.keys()) == ['email', 'job']
        assert TestForm3.prototypes['email'] == email_field_in_Form3
        assert TestForm3.prototypes['job'] == job_field_in_Form2
        assert list(TestForm3.prototypes.keys()) == ['email', 'job']

        # Replace `email` field in `TestForm1` ---------------------------------
        email_field_in_Form1_new = Field(None)
        TestForm1.email = email_field_in_Form1_new

        # check it does not change child classes
        assert TestForm1.prototypes['email'] == email_field_in_Form1_new
        assert list(TestForm1.prototypes.keys()) == ['email']
        assert TestForm2.prototypes['email'] == email_field_in_Form1
        assert TestForm2.prototypes['job'] == job_field_in_Form2
        assert list(TestForm2.prototypes.keys()) == ['email', 'job']
        assert TestForm3.prototypes['email'] == email_field_in_Form3
        assert TestForm3.prototypes['job'] == job_field_in_Form2
        assert list(TestForm3.prototypes.keys()) == ['email', 'job']

        # Replace `email` field in `TestForm3` ---------------------------------
        email_field_in_Form3_new = Field(None)
        TestForm3.email = email_field_in_Form3_new

        # check it does not change super classes
        assert TestForm1.prototypes['email'] == email_field_in_Form1_new
        assert list(TestForm1.prototypes.keys()) == ['email']
        assert TestForm2.prototypes['email'] == email_field_in_Form1
        assert TestForm2.prototypes['job'] == job_field_in_Form2
        assert list(TestForm2.prototypes.keys()) == ['email', 'job']
        assert TestForm3.prototypes['email'] == email_field_in_Form3_new
        assert TestForm3.prototypes['job'] == job_field_in_Form2
        assert list(TestForm3.prototypes.keys()) == ['email', 'job']

        # Add `age` field to `TestForm1` ---------------------------------------
        age_field_in_Form1 = Field(None)
        TestForm1.age = age_field_in_Form1

        # check it does not change super classes
        assert TestForm1.prototypes['email'] == email_field_in_Form1_new
        assert TestForm1.prototypes['age'] == age_field_in_Form1
        assert list(TestForm1.prototypes.keys()) == ['email', 'age']
        assert TestForm2.prototypes['email'] == email_field_in_Form1
        assert TestForm2.prototypes['job'] == job_field_in_Form2
        assert list(TestForm2.prototypes.keys()) == ['email', 'job']
        assert TestForm3.prototypes['email'] == email_field_in_Form3_new
        assert TestForm3.prototypes['job'] == job_field_in_Form2
        assert list(TestForm3.prototypes.keys()) == ['email', 'job']

        # check order
        assert list(TestForm1.prototypes.keys()) == ['email', 'age']

        # Add `age` field to `TestForm3` ---------------------------------------
        age_field_in_Form3 = Field(None)
        TestForm3.age = age_field_in_Form3

        # check it does not change ancestor classes
        assert TestForm1.prototypes['email'] == email_field_in_Form1_new
        assert TestForm1.prototypes['age'] == age_field_in_Form1
        assert list(TestForm1.prototypes.keys()) == ['email', 'age']
        assert TestForm2.prototypes['email'] == email_field_in_Form1
        assert TestForm2.prototypes['job'] == job_field_in_Form2
        assert list(TestForm2.prototypes.keys()) == ['email', 'job']
        assert TestForm3.prototypes['email'] == email_field_in_Form3_new
        assert TestForm3.prototypes['job'] == job_field_in_Form2
        assert TestForm3.prototypes['age'] == age_field_in_Form3
        assert list(TestForm3.prototypes.keys()) == ['email', 'job', 'age']

        # check it works after all this pain ^_^
        form1 = TestForm1({}, data={'email': 'x', 'job': 'y', 'age': 'z'}, submit=True)
        form2 = TestForm2({}, data={'email': 'x', 'job': 'y', 'age': 'z'}, submit=True)
        form3 = TestForm3({}, data={'email': 'x', 'job': 'y', 'age': 'z'}, submit=True)

        assert form1.value == {'email': 'x', 'age': 'z'} # drops job
        assert form2.value == {'email': 'x', 'job': 'y'} # drops age
        assert form3.value == {'email': 'x', 'job': 'y', 'age': 'z'}

    def test_field_reordering(self):
        email_field_in_Form1 = Field(None)
        job_field_in_Form2 = Field(None)
        email_field_in_Form3 = Field(None)

        class TestForm1(BaseForm):
            email = email_field_in_Form1

        class TestForm2(TestForm1):
            job = job_field_in_Form2

        class TestForm3(TestForm2):
            email = email_field_in_Form3

        # Reorder `TestForm2` prototypes
        TestForm2.prototypes = OrderedDict([
            ('job', TestForm2.prototypes['job']),
            ('email', TestForm2.prototypes['email']),
        ])

        # check it does not change other classes
        assert list(TestForm1.prototypes.keys()) == ['email']
        assert list(TestForm2.prototypes.keys()) == ['job', 'email']
        assert list(TestForm3.prototypes.keys()) == ['email', 'job']

        # check it works after this ^_^
        form2 = TestForm2({}, data={'job': 'y', 'email': 'x'}, submit=True)
        assert form2.value == {'job': 'y', 'email': 'x'}

    def test_Model(self):
        class TestForm(BaseForm):
            something = Field(None)

        # model
        form = TestForm({'something': 'good'})
        assert form.value == {'something': 'good'}

        # data
        form = TestForm({}, data={'something': 'good'}, submit=True)
        assert form.value == {'something': 'good'}

        # model + data
        form = TestForm({'something': 'bad'}, data={'something': 'good'}, submit=True)
        assert form.value == {'something': 'good'}

        class MyModel:
            def __init__(self, something=None):
                self.something = something

            def __eq__(self, other):
                try:
                    return self.something == other.something
                except AttributeError:
                    return False

        class TestForm(BaseForm):
            something = Field(None)

        # model
        form = TestForm(model={'something': 'good'})
        assert form.value == {'something': 'good'}

        # data
        form = TestForm(model=MyModel(), data={'something': 'good'}, submit=True)
        assert form.value == MyModel(something='good')

        # model + data
        form = TestForm(model={'something': 'bad'}, data={'something': 'good'}, submit=True)
        assert form.value == {'something': 'good'}

    def test_default_value(self):
        class TestForm(BaseForm):
            a = Field(None, converters=StrConverter(), default='xyz')
            b = Field(None, converters=IntConverter(), default=123)
            c = Field(None, converters=BoolConverter(), default=True)

        form = TestForm({})

        assert form.value == {'a': 'xyz', 'b': 123, 'c': True}
        assert form.fields['a'].value == 'xyz'
        assert form.fields['b'].value == 123
        assert form.fields['c'].value == True

    def test_feed_value(self):
        class TestForm(BaseForm):
            a = Field(None, converters=StrConverter(), default='xyz')
            b = Field(None, converters=IntConverter(), default=123)
            c = Field(None, converters=BoolConverter(), default=True)

        form = TestForm(model={'a': 'zyx', 'c': False})
        assert form.value == {'a': 'zyx', 'b': 123, 'c': False}

    def test_feed_data(self):
        class TestForm(BaseForm):
            a = Field(None, converters=StrConverter(), default='xyz')
            b = Field(None, converters=IntConverter(), default=123)
            c = Field(None, converters=BoolConverter(), default=True)

        form = TestForm({}, data={'a': 'zyx', 'b': 123, 'c': False}, submit=True)
        assert form.value == {'a': 'zyx', 'b': 123, 'c': False}

    def test_feed_value_and_data(self):
        class TestForm(BaseForm):
            a = Field(None, converters=StrConverter(), default='xyz')
            b = Field(None, converters=IntConverter(), default=123)
            c = Field(None, converters=BoolConverter(), default=True)

        form = TestForm(
            model = {'a': 'zyx', 'c': False},
            data = {'a': 'xyz*', 'b': 1, 'c': True},
            submit = True
        )
        assert form.value == {'a': 'xyz*', 'b': 1, 'c': True}

    def test_feed_value_and_data_partial_form(self):
        model = {
            'id': 1,
            'username': 'some-username',
            'password': 'some-password',
        }

        class PasswordEditForm(BaseForm):
            password = Field(None)

        form = PasswordEditForm(
            model = model,
            data = {'password': 'new-password'},
            submit = True
        )
        assert form.value == {
            'id': 1,
            'username': 'some-username',
            'password': 'new-password',
        }

    def test_ok(self):
        class LoginForm(BaseForm):
            username = Field(None, required=True)
            password = Field(None, required=True)
        form = LoginForm({}, data={}, submit=True)
        assert not form.ok
        form = LoginForm({}, data={'username': 'admin', 'password': 'admin'}, submit=True)
        assert form.ok

    def test_nested_forms_combinations(self):
        class PasswordForm(BaseForm):
            password = Field(None)
            repassword = Field(None)

        # A) Without Form referencing
        class EditForm_A(BaseForm):
            password = FormField(None, [PasswordForm.prototypes['password'], PasswordForm.prototypes['repassword']])

        # B) Via Form class
        class EditForm_B(BaseForm):
            password = FormField(None, PasswordForm)

        assert EditForm_A.prototypes['password'].prototypes == EditForm_B.prototypes['password'].prototypes

        form_A = EditForm_B({}, data={'password': {'password': 'test', 'repassword': 'test'}})
        form_B = EditForm_B({}, data={'password': {'password': 'test', 'repassword': 'test'}})

        assert form_A.value == form_B.value

    def test_messages(self):
        class TestForm(BaseForm):
            number = Field(None, converters=IntConverter(), default=0)
        form_en = TestForm({}, data={'number': 'xyz'}, locale='en', submit=True)
        form_ru = TestForm({}, data={'number': 'xyz'}, locale='ru', submit=True)
        assert form_en.messages.get('number', {}).get('error')
        assert form_en.fields['number'].messages.get('error', []) == ['Invalid value']
        assert form_ru.messages.get('number', {}).get('error')
        assert form_ru.fields['number'].messages.get('error', []) == ['Некорректное значение']

    def test_deepcopy(self):
        class FirstForm(BaseForm):
            demox = Field(None, required=False, validators=[EmailValidator()])

        class SecondForm(BaseForm):
            demoy = Field(None, required=False)

        class MyForm(FirstForm, SecondForm):
            pass

        CloneForm = MyForm.deepcopy()
        CloneForm.prototypes['demox'].required = True
        assert MyForm.prototypes['demox'].required
        assert not CloneForm.prototypes['demox'].required


class Test_FlaskForm:
    def test(self):
        from flask import Request
        from flask.testing import EnvironBuilder
        from paqforms.i18n import get_translations
        from paqforms.bootstrap import FormWidget

        class MyForm(BaseForm):
            def feed(self, value={}, data={}, submit=False):
                data = variable_decode(data)
                submit = submit.method in {'POST', 'PUT', 'DELETE'}
                BaseForm.feed(self, value, data, submit)

            def is_multidict(self, data):
                return hasattr(data, 'getlist')

        class CommentForm(MyForm):
            content = Field(None)

        class PostForm(MyForm):
            content = Field(None)
            comments = FieldField(None, FormField('', prototypes=CommentForm))
            tags = FieldField(None, Field(None))

        data = MultiDict([
            ('content', 'post-content-1'),
            ('comments-1.content', 'comment-content-1'),
            ('comments-2.content', 'comment-content-2'),
            ('tags-1', 'tag-1'),
            ('tags-2', 'tag-2'),
            ('tags-3', 'tag-3'),
        ])
        builder = EnvironBuilder(method='POST', data=data)
        environ = builder.get_environ()

        form = PostForm({}, data=data, submit=Request(environ))
        assert form.value == {
            'content': 'post-content-1',
            'comments': [{'content': 'comment-content-1'}, {'content': 'comment-content-2'}],
            'tags': ['tag-1', 'tag-2', 'tag-3'],
        }


class Test_ChoiceField:
    def test_valid(self):
        field = ChoiceField(
            widget = None,
            choices = [None, 11, 22, 33],
            converters = IntConverter(),
        )
        field.feed(data='11', value=None, submit=True)
        assert field.value == 11

    def test_invalid(self):
        field = ChoiceField(
            widget = None,
            choices = [None, 11, 22, 33],
            converters = IntConverter()
        )
        field.feed(data='44', value=None, submit=True)
        assert field.messages['error']


class Test_MultiChoiceField:
    def test_default_required(self):
        """
        `field.value` from `value` or `default` or `data`
        """
        field = MultiChoiceField(None,
            default = lambda: [22],
            required = True,
            converters = MapConverter(converter=IntConverter()),
        )

        assert field.feed(None).value == [22]

        assert field.feed([]).value == []
        assert field.feed([4]).value == [4]
        assert field.feed(['a']).value == ['a']

        assert field.feed(None, data=[]).value == [22]
        assert field.feed([], data=['4']).value == [4]
        assert field.feed([], data=['a']).messages['error']

    def test_default_optional(self):
        """
        `field.value` from `value` or `default` or `data`
        """
        field = MultiChoiceField(None,
            default = lambda: [22],
            converters = MapConverter(converter=IntConverter()),
        )

        assert field.feed(None).value == [22]

        assert field.feed([]).value == []
        assert field.feed([4]).value == [4]
        assert field.feed(['a']).value == ['a']

        assert field.feed([], []).value == []
        assert field.feed([], ['4']).value == [4]
        assert field.feed([], ['a']).messages['error']

    def test_submit_required(self):
        """
        `field.value` from `data`
        """
        field = MultiChoiceField(None,
            default = lambda: [22],
            required = True,
            converters = MapConverter(converter=IntConverter()),
        )

        assert field.feed({}, submit=True).messages['error']

        assert field.feed([], submit=True).messages['error']
        assert field.feed([4], submit=True).messages['error']
        assert field.feed(['a'], submit=True).messages['error']

        assert field.feed([], data=[], submit=True).messages['error']
        assert field.feed([], data=['4'], submit=True).value == [4]
        assert field.feed([], data=['a'], submit=True).messages['error']

    def test_submit_optional(self):
        """
        `field.value` from `data`
        """
        field = MultiChoiceField(None,
            default = lambda: [22],
            converters = MapConverter(converter=IntConverter()),
        )

        assert field.feed([], submit=True).value == []

        assert field.feed([], submit=True).value == []
        assert field.feed([4], submit=True).value == []
        assert field.feed(['a'], submit=True).value == []

        assert field.feed([], [], submit=True).value == []
        assert field.feed([], ['4'], submit=True).value == [4]
        assert field.feed([], ['a'], submit=True).messages['error']


class _Test_BetweenField:
    def test_ok(self):
        field = BetweenField(None, converters=IntConverter())
        field.feed(value={}, data={'min': '1', 'max': '10'}, submit=True)
        assert field.value == {'min': 1, 'max': 10}
        assert not any(messages.get('error') for messages in field.messages.values())

    def test_error(self):
        field = BetweenField(None, converters=IntConverter())
        # TODO throws AttributeError (data missing) - seems ok
        field.feed(value={}, data={'min': '1.0'}, submit=True)
        assert any(messages.get('error') for messages in field.messages.values())

    def test_required(self): # TODO
        field = BetweenField(None, converters=IntConverter()).feed({}, {})
        assert field.value == {'min': None, 'max': None}
        assert not any(messages.get('error') for messages in field.messages.values())


"""
class Test_TextField:
    def test_feed(self):
        field = TextField('Username', default='admin')
        field.name = 'username'
        assert field.caption == 'Username'
        field.feed(data='gizmo')
        assert field.value == 'gizmo'

class LoginForm(BaseForm):
    username = TextField('Username', validators=[LengthValidator(min=1)])
    password = PasswordField('Password')

class Test_Form:
    def test_login_valid(self):
        data = {'username': 'root', 'password': 'root'}
        form = LoginForm(data=data)
        assert form.ok

    def test_login_invalid(self):
        data = {'username': 'root', 'password': ''}
        form = LoginForm(data=data)
        assert not form.ok
"""

# TODO add test missing fields
