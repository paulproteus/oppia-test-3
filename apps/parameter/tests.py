# Copyright 2013 Google Inc. All Rights Reserved.
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

"""Tests for parameter models."""

__author__ = 'Sean Lip'

from django.utils import unittest
from oppia.apps.parameter.models import Parameter


class ParameterUnitTests(unittest.TestCase):
    """Test the Parameter class."""

    def test_parameter_class(self):
        """Tests the Parameter class."""
        # Raise an error because no obj_type is specified.
        with self.assertRaises(TypeError):
            model = Parameter(name='param1', values=['hello'])

        # Raise an error because the value does not match the obj_type.
        with self.assertRaises(TypeError):
            model = Parameter(name='param1', obj_type='Int', values=['hello'])

        model = Parameter(name='param1', obj_type='Int', values=[6])
        model.put()

        self.assertEqual(model.value, 6)

        model.values = []
        model.put()
        self.assertIsNone(model.value)
