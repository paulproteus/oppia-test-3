# Copyright 2012 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Controllers for the profile page."""

__author__ = 'sfederwisch@google.com (Stephanie Federwisch)'

from apps.exploration.models import Exploration
from apps.statistics.models import Statistics
from controllers.base import BaseHandler
import utils
import logging

from google.appengine.api import users


class ProfilePage(BaseHandler):
    """The profile page."""

    def get(self):
        """Handles GET requests."""
        self.values.update({
            'nav_mode': 'profile',
        })
        self.render_template('profile/profile.html')


class ProfileHandler(BaseHandler):
    """Provides data for the profile gallery."""

    def get(self):
        """Handles GET requests."""
        user = users.get_current_user()
        exp_ids = Exploration.get_explorations_user_can_edit(user)
        improvable = Statistics.get_top_ten_improvable_states(exp_ids)
        explorations = []
        for exp_id in exp_ids:
          exp = Exploration.get(exp_id)
          explorations.append(
              {'name': exp.title, 
               'id': exp.id,
               'image_id': exp.image_id})

        self.values.update({
            'improvable': improvable,
            'explorations': explorations,
        })
        self.render_json(self.values)
