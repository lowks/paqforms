#encoding: utf8
from __future__ import unicode_literals

import peewee

from paqforms.rest_peewee import *


class Model(peewee.Model):
    class Meta(object):
        database = peewee.SqliteDatabase(':memory:')

class Post(Model):
    id = peewee.PrimaryKeyField()
    title = peewee.CharField()
    content = peewee.CharField()

    def __unicode__(self):
        return self.title

Post.create_table()
post1 = Post(title='My first post', content='...')
post2 = Post(title='And second one', content='...')
post3 = Post(title='Here we go', content='...')
post1.save()
post2.save()
post3.save()


def test_post_ids():
    assert post1.id == 1
    assert post2.id == 2
    assert post3.id == 3


class Test_QueryChoiceField(object):
    def test_feed(self):
        field = QueryChoiceField(query=Post.select().order_by(Post.id), default=lambda: post2)
        assert field.choices == [(None, u''), (post1, unicode(post1)), (post2, unicode(post2)), (post3, unicode(post3))]
        field.feed(data='1')
        assert field.value == post1
        field.feed(data='3')
        assert field.value == post3

class Test_QueryMultiChoiceField(object):
    def test_feed(self):
        field = QueryMultiChoiceField(query=Post.select().order_by(Post.id), default=lambda: [post1, post2])
        assert field.choices == [(None, u''), (post1, unicode(post1)), (post2, unicode(post2)), (post3, unicode(post3))]
        field.feed(data=['1'])
        assert field.value == [post1]
        field.feed(data=['1', '3'])
        assert field.value == [post1, post3]
