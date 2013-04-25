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

"""Models for Oppia classifiers."""

__author__ = 'Sean Lip'

import os
import json

from oppia.apps.base_model.models import BaseModel, CustomTypeEncoder, decode_value
from oppia import feconf
from oppia import utils

from django.db import models
from jsonfield import JSONField


class RuleSpec(models.Model):
    """A rule specification in a classifier."""
    # Python code for the rule, e.g. "equals(x)"
    rule = models.CharField(max_length=50, blank=True)
    # Human-readable text used to display the rule in the UI, e.g. "Answer is
    # equal to {{x|MusicNote}}".
    name = models.TextField(blank=True)
    # Python code for pre-commit checks on the rule parameters.
    # JSON object containing a list of checks
    _checks = JSONField()

    def __setattr__(self, item, value):
        if item == 'checks':
            self.value = value
            assert isinstance(value, list)
            if value:
                assert isinstance(value[0], (str, unicode))
            self.__dict__['_checks'] = json.dumps(value)
        else:
            self.__dict__[item] = value

    @property
    def checks(self):
        """Construct a list of RuleSpec objects from the JSON object stored in _rules"""
        checks = []
        for check in decode_value(self._checks):
            checks.append(check)
        return checks


class RulesEncoder(CustomTypeEncoder):
    """A custom encoder to encode RuleSpec objects recursively."""
    types = (RuleSpec)


class Classifier(BaseModel):
    """An Oppia classifier."""

    # The id is the same as the directory name for this classifier.
    # id is inherited from BaseModel

    # Rule specifications for the classifier.
    # A JSON object containing a list of Rule specifications.
    _rules = JSONField()

    def __setattr__(self, item, value):
        """We encode a list of RuleSpec objects into a JSON object using RulesEncoder"""
        if item == 'rules':
            assert isinstance(value, list)
            if value:
                assert isinstance(value[0], RuleSpec)
            self.__dict__['_rules'] = json.dumps(value, cls=RulesEncoder)
        else:
            self.__dict__[item] = value

    @property
    def rules(self):
        """Construct a list of RuleSpec objects from the JSON object stored in _rules"""
        rules = []
        for rule in decode_value(self._rules):
            rulespec = RuleSpec(rule=rule['__RuleSpec__']['rule'], name=rule['__RuleSpec__']['name'])
            checks = rule['__RuleSpec__'].get('_checks', [])
            if checks:
                rulespec._checks = checks
            rules.append(rulespec)
        return rules

    @classmethod
    def delete_all_classifiers(cls):
        """Deletes all classifiers."""
        classifier_list = Classifier.objects.all()
        for classifier in classifier_list:
            classifier.delete()

    @classmethod
    def get_classifier_ids(cls):
        """Gets a list of the classifiers in the system."""
        return [d for d in os.listdir(feconf.SAMPLE_CLASSIFIERS_DIR)
                if os.path.isdir(
                    os.path.join(feconf.SAMPLE_CLASSIFIERS_DIR, d))]

    @classmethod
    def load_default_classifiers(cls):
        """Loads the default classifiers."""
        classifier_ids = cls.get_classifier_ids()

        for classifier_id in classifier_ids:
            rules_filepath = os.path.join(
                feconf.SAMPLE_CLASSIFIERS_DIR, classifier_id,
                '%sRules.yaml' % classifier_id)
            with open(rules_filepath) as f:
                rule_dict = utils.dict_from_yaml(f.read().decode('utf-8'))
                rules = []
                for rule in rule_dict:
                    r_spec = RuleSpec(rule=rule, name=rule_dict[rule]['name'])
                    if 'checks' in rule_dict[rule]:
                        r_spec.checks = rule_dict[rule]['checks']
                    rules.append(r_spec)
                Classifier(id=classifier_id, rules=rules).put()

    def put(self):
        self.full_clean()
        self.save()
