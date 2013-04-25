# coding: utf-8
#
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

__author__ = 'Jeremy Emerson'

from oppia.apps.image.models import Image
from django.utils import unittest
from django.core.exceptions import ValidationError
from django.core.files import File


class ImageUnitTests(unittest.TestCase):
    """Test image models."""

    def test_image_class(self):
        """Test the Image class."""
        # An Image must have the 'raw' property set.
        image = Image(id='The hash id')
        with self.assertRaises(ValidationError):
            image.put()

        # TODO: image format validation.
        # The 'raw' property must be a valid image.
        # with self.assertRaises(AssertionError):
        #     image.raw = 'The image'

        # Set the 'raw' property to be a valid image, then do a put().
        with open('oppia/tests/data/img.png') as f:
            image.raw = File(f)
            image_file_content = image.raw.read()
            image.put()

        # Retrieve the image.
        retrieved_image = Image.objects.get(id='The hash id')
        # Read its content
        retrieved_content = retrieved_image.raw.read()
        self.assertEqual(retrieved_content, image_file_content)
