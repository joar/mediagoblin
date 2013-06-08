# GNU MediaGoblin -- federated, autonomous media hosting
# Copyright (C) 2011, 2012 MediaGoblin contributors.  See AUTHORS.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pytest

import urlparse

from mediagoblin.tools import template, mail

from mediagoblin.db.models import Notification, CommentNotification
from mediagoblin.db.base import Session

from mediagoblin.notifications import mark_comment_notification_seen

from mediagoblin.tests.tools import fixture_add_comment, \
    fixture_media_entry, fixture_add_user, \
    fixture_comment_subscription


class TestNotifications:
    @pytest.fixture(autouse=True)
    def setup(self, test_app):
        self.test_app = test_app

        # TODO: Possibly abstract into a decorator like:
        # @as_authenticated_user('chris')
        self.test_user = fixture_add_user()

        self.current_user = None

        self.login()

    def login(self, username=u'chris', password=u'toast'):
        response = self.test_app.post(
            '/auth/login/', {
                'username': username,
                'password': password})

        response.follow()

        assert urlparse.urlsplit(response.location)[2] == '/'
        assert 'mediagoblin/root.html' in template.TEMPLATE_TEST_CONTEXT

        ctx = template.TEMPLATE_TEST_CONTEXT['mediagoblin/root.html']

        assert Session.merge(ctx['request'].user).username == username

        self.current_user = ctx['request'].user

    def logout(self):
        self.test_app.get('/auth/logout/')
        self.current_user = None

    def test_comment_email_subscription(self):
        pass

    def test_comment_unsubscription(self):
        pass

    def test_comment_notification(self):
        '''
        Test
        - if a notification is created when posting a comment on
          another users media entry.
        - that the comment data is consistent and exists.

        '''
        user = fixture_add_user('otherperson', password='nosreprehto')

        media_entry = fixture_media_entry(uploader=user.id, state=u'processed')

        subscription = fixture_comment_subscription(media_entry)

        media_uri_id = '/u/{0}/m/{1}/'.format(user.username,
                                              media_entry.id)
        media_uri_slug = '/u/{0}/m/{1}/'.format(user.username,
                                                media_entry.slug)

        self.test_app.post(
            media_uri_id + 'comment/add/',
            {
                'comment_content': u'Test comment #42'
            }
        )

        notifications = Notification.query.filter_by(
            user_id=user.id).all()

        assert len(notifications) == 1

        notification = notifications[0]

        assert type(notification) == CommentNotification
        assert notification.seen == False
        assert notification.user_id == user.id
        assert notification.subject.get_author.id == self.test_user.id
        assert notification.subject.content == u'Test comment #42'

        # Save the ids temporarily because of DetachedInstanceError
        notification_id = notification.id
        comment_id = notification.subject.id

        self.logout()
        self.login('otherperson', 'nosreprehto')

        self.test_app.get(media_uri_slug + '/c/{0}/'.format(comment_id))

        notification = Notification.query.filter_by(id=notification_id).first()

        assert notification.seen == True
