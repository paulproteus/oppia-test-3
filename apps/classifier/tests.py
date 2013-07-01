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

"""Tests for the Classifier model."""

__author__ = 'Sean Lip'

from oppia.apps.classifier.models import Classifier
from oppia.apps.classifier.models import RuleSpec
from django.utils import unittest


class ClassifierModelUnitTests(unittest.TestCase):
    """Test the Classifier model."""

    def test_loading_and_deletion_of_classifiers(self):
        """Test loading and deletion of the default classifiers."""
        self.assertEqual(Classifier.objects.count(), 0)

        Classifier.load_default_classifiers()
        classifiers = Classifier.objects.all()
        classifier_ids = [classifier.id for classifier in classifiers]
        self.assertIn('Coord2DClassifier', classifier_ids)
        self.assertEqual(classifiers.count(), 7)

        Classifier.delete_all_classifiers()
        self.assertEqual(Classifier.objects.count(), 0)

    def test_setting_and_getting_attrs(self):
        """Test __getattr__ and __setattr__ methods"""
        rspec = RuleSpec(name='test name', checks=['test check'])
        classifier = Classifier(id='test id', rules=[rspec])
        classifier.put()

        classifiers = Classifier.objects.all()
        self.assertEqual(classifiers.count(), 1)
        new_classifier = classifiers[0]
        self.assertEqual(new_classifier.rules, [rspec])
