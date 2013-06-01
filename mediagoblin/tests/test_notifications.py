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

from mediagoblin.db.models import Notification, CommentNotification, \
    MediaComment
from mediagoblin.db.base import Session

from mediagoblin.tests.tools import fixture_add_collection, \
    fixture_add_comment, fixture_media_entry, fixture_add_user


class TestNotifications:
    @pytest.fixture(autouse=True)
    def setup(self, test_app):
        self.test_app = test_app

        # TODO: Possibly abstract into a decorator like:
        # @as_authenticated_user('chris')
        self.test_user = fixture_add_user()

        self.login()

    def login(self):
        self.test_app.post(
            '/auth/login/', {
                'username': u'chris',
                'password': 'toast'})

    def test_notification(self):
        user = fixture_add_user('otherperson')

        media_entry = fixture_media_entry(uploader=user.id)

        self.test_app.get('/u/{0}/'.format(self.test_user.username))
        self.test_app.get('/u/{0}/'.format(user.username))

        self.test_app.post(
            '/u/{0}/m/{1}/comment/add/'.format(
                user.username, media_entry.id),
            {
                'comment_content': u'Test comment #42'
            }
        )

        notifications = Notification.query.filter_by(
            user_id=user.id).all()

        assert False
