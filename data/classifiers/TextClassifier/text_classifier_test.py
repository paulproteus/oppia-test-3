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

"""Text classifier tests."""

__author__ = 'Sean Lip'


import TextClassifier
import test_utils


class TextClassifierTest(test_utils.TestBase):

    def testTextClassifier(self):
        assert TextClassifier.equals('hello', 'hello')
        assert TextClassifier.equals('hello', 'Hello')
        assert not TextClassifier.equals('hello', 'goodbye')

        assert TextClassifier.case_sensitive_equals('hello', 'hello')
        assert not TextClassifier.case_sensitive_equals('hello', 'Hello')
        assert not TextClassifier.case_sensitive_equals('hello', 'goodbye')

        assert TextClassifier.starts_with('hello', 'he')
        assert TextClassifier.starts_with('hello', 'HE')
        assert not TextClassifier.starts_with('he', 'hello')

        assert TextClassifier.contains('hello', 'he')
        assert TextClassifier.contains('hello', 'HE')
        assert TextClassifier.contains('hello', 'll')
        assert not TextClassifier.contains('hello', 'ol')

        assert TextClassifier.fuzzy_equals('hell', 'hello')
        assert TextClassifier.fuzzy_equals('hello', 'hell')
        assert TextClassifier.fuzzy_equals('hello', 'hellp')
        assert TextClassifier.fuzzy_equals('hellp', 'hello')
        assert not TextClassifier.fuzzy_equals('hello', 'hello')
        assert not TextClassifier.fuzzy_equals('hellp', 'HEllp')
        assert not TextClassifier.fuzzy_equals('help', 'pleh')
