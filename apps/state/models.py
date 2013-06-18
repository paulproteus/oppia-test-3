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

"""Model for an Oppia state."""

__author__ = 'Sean Lip'

import copy
import importlib

from oppia.apps.base_model.models import BaseModel
from oppia.apps.base_model.models import Converter
from oppia.apps.base_model.models import django_internal_attrs
from oppia.apps.exploration.models import Exploration
from oppia.apps.parameter.models import ParamChange
from oppia.apps.widget.models import InteractiveWidget
from oppia.apps.widget.models import Widget
from oppia.data.objects.models import objects
from oppia import feconf
from oppia import utils

from django.db import models
from json_field import JSONField


class Content(BaseModel):
    """Non-interactive content in a state."""
    type = models.CharField(max_length=100, choices=[
        ('text', 'text'),
        ('image', 'image'),
        ('video', 'video'),
        ('widget', 'widget')
    ])
    value = models.TextField(default='')

    def put(self):
        self.full_clean()
        self.save()


class Rule(BaseModel):
    """A rule for an answer classifier."""
    # TODO(sll): Ensure the types for param_changes are consistent.

    # The name of the rule.
    name = models.CharField(max_length=100)
    # Parameters for the classification rule. TODO(sll): Make these the actual params.
    inputs = JSONField(default={})
    # The id of the destination state.
    dest = models.CharField(max_length=100, blank=True)
    # Feedback to give the reader if this rule is triggered.
    feedback = JSONField(default=[])

    _param_changes = JSONField(default=[])

    def __setattr__(self, item, value):
        """Encode a list of ParamChange objects to JSON object."""
        if item == 'param_changes':
            assert isinstance(value, list)
            for val in value:
                assert isinstance(val, ParamChange)
            self.__dict__['_param_changes'] = Converter.encode(value)
        elif item == 'feedback':
            assert isinstance(value, list)
            for val in value:
                assert isinstance(val, basestring)
            self.__dict__['feedback'] = value
        elif item in django_internal_attrs or item in [
            '_param_changes',
            'name',
            'inputs',
            'dest',
            'feedback',
            '_json_field_cache'
        ]:
            self.__dict__[item] = value
        else:
            raise AttributeError(item)

    @property
    def param_changes(self):
        """Return a list of ParamChange objects from JSON object stored in _param_changes"""
        param_changes = []
        for pc in self._param_changes:
            param_change = ParamChange(
                name=pc['__ParamChange__']['name'],
                description=pc['__ParamChange__']['description'],
                obj_type=pc['__ParamChange__']['obj_type'],
                values=pc['__ParamChange__']['values']
            )
            param_changes.append(param_change)
        return param_changes


class AnswerHandlerInstance(BaseModel):
    """An answer event stream (submit, click, drag, etc.)."""
    name = models.CharField(max_length=100, default='submit')
    # A list of Rule objects
    _rules = JSONField(default=[])
    classifier = models.CharField(max_length=100)

    def __setattr__(self, item, value):
        """We encode a list of Rule objects into a JSON object using
        Converter.encode"""
        if item == 'rules':
            assert isinstance(value, list)
            for val in value:
                assert isinstance(val, Rule)
            self.__dict__['_rules'] = Converter.encode(value)
        elif item in django_internal_attrs or item in [
            '_rules', 'name', 'classifier', '_json_field_cache'
        ]:
            self.__dict__[item] = value
        else:
            raise AttributeError(item)

    @property
    def rules(self):
        """Return a list of Rule objects from JSON object stored in _rules"""
        rules = []
        for rule in self._rules:
            rule_instance = Rule(
                name=rule['__Rule__']['name'],
                inputs=rule['__Rule__']['description'],
                dest=rule['__Rule__']['obj_type'],
                feedback=rule['__Rule__']['values'],
                param_changes=rule['__Rule__']['param_changes']
            )
            rules.append(rule_instance)
        return rules


class WidgetInstance(BaseModel):
    """An instance of a widget."""
    # The id of the interactive widget class for this state.
    widget_id = models.CharField(max_length=100, default='Continue')
    # Parameters for the interactive widget view, stored as key-value pairs.
    # Each parameter is single-valued. The values may be Jinja templates that
    # refer to state parameters.
    params = JSONField(default={})
    # If true, keep the widget instance from the previous state if both are of
    # the same type.
    sticky = models.BooleanField(default=False)
    # Answer handlers and rulesets.
    _handlers = JSONField(default=[])

    def __setattr__(self, item, value):
        """We encode a list of AnswerHandler objects into a JSON object using
        Converter.encode"""
        if item == 'handlers':
            assert isinstance(value, list)
            for val in value:
                assert isinstance(val, AnswerHandlerInstance)
            self.__dict__['_handlers'] = Converter.encode(value)
        elif item == 'params':
            assert isinstance(value, dict)
            for val in value:
                assert isinstance(val, basestring)
            self.__dict__['params'] = value
        elif item in django_internal_attrs or item in [
            '_handlers', 'widget_id', 'params', 'sticky', '_json_field_cache'
        ]:
            self.__dict__[item] = value
        else:
            raise AttributeError(item)

    @property
    def handlers(self):
        """Returns a list of AnswerHandlerInstance objects"""
        handlers = []
        for handler in self._handlers:
            handler_instance = AnswerHandlerInstance(
                name=handler['__AnswerHandlerInstance__']['name'],
                rules=handler['__AnswerHandlerInstance__']['rules'],
                classifier=handler['__AnswerHandlerInstance__']['classifier']
            )
            handlers.append(handler_instance)
        return handlers


class State(IdModel):
    """A state which forms part of an exploration."""
    # NB: This element's parent should be an Exploration.

    def get_default_rule(self):
        return Rule(name='Default', dest=self.id)

    def get_default_handler(self):
        return AnswerHandlerInstance(rules=[self.get_default_rule()])

    def get_default_widget(self):
        return WidgetInstance(handlers=[self.get_default_handler()])

    def _pre_put_hook(self):
        """Ensures that the widget and at least one handler for it exists."""
        # Every state should have a parent exploration.
        if not self.key.parent():
            raise Exception('This state does not have a parent exploration.')

        # Every state should have an interactive widget.
        if not self.widget:
            self.widget = self.get_default_widget()
        elif not self.widget.handlers:
            self.widget.handlers = [self.get_default_handler()]

        # TODO(sll): Do other validation.

        # Add the corresponding AnswerHandler classifiers for easy reference.
        widget = InteractiveWidget.get(self.widget.widget_id)
        for curr_handler in self.widget.handlers:
            for w_handler in widget.handlers:
                if w_handler.name == curr_handler.name:
                    curr_handler.classifier = w_handler.classifier

    # Human-readable name for the state.
    name = models.CharField(max_length=100, default=feconf.DEFAULT_STATE_NAME)
    # The content displayed to the reader in this state.
    _content = JSONField(default=[])
    # Parameter changes associated with this state.
    _param_changes = JSONField(default=[])
    # The interactive widget associated with this state. Set to be the default
    # widget if not explicitly specified by the caller.
    _widget = JSONField(default=[])
    # A dict whose keys are unresolved answers associated with this state, and
    # whose values are their counts.
    unresolved_answers = JSONField(default={})
    parent = models.ForeignKey(Exploration, related_name='states')

    def __setattr__(self, item, value):
        if item == 'content':
            assert isinstance(value, list)
            for val in value:
                assert isinstance(val, Content)
            self.__dict__['_content'] = Converter.encode(value)
        elif item == 'param_changes':
            assert isinstance(value, list)
            for val in value:
                assert isinstance(val, ParamChange)
            self.__dict__['_param_changes'] = Converter.encode(value)
        elif item == 'widget':
            assert isinstance(value, list)
            for val in value:
                assert isinstance(val, WidgetInstance)
            self.__dict__['_widget'] = Converter.encode(value)
        elif item == 'unresolved_answers':
            assert isinstance(value, dict)
            for key, val in value.iteritems():
                assert isinstance(key, basestring)
                assert isinstance(val, int)
            self.__dict__['unresolved_answers'] = value
        elif item in django_internal_attrs or item in [
            'name', '_content', '_param_changes', '_widget', '_json_field_cache'
        ]:
            self.__dict__[item] = value
        else:
            raise AttributeError(item)

    @classmethod
    def create(cls, exploration, name, state_id=None):
        """Creates a new state."""
        state_id = state_id or cls.get_new_id(name)
        new_state = cls(id=state_id, parent=exploration, name=name)
        new_state.put()
        return new_state

    def to_dict(self):
        output = {}
        for key in ['id', 'name']:
            output[key] = getattr(self, key)

        output['param_changes'] = self._param_changes
        output['content'] = self._content
        output['widget'] = self._widget

        return output

    def as_dict(self):
        """Gets a Python dict representation of the state."""
        state_dict = copy.deepcopy(self.to_dict())
        state_dict.update({'id': self.id, 'name': self.name,
                           'unresolved_answers': self.unresolved_answers})
        return state_dict

    def internals_as_dict(self, human_readable_dests=False):
        """Gets a Python dict of the internals of the state."""
        state_dict = copy.deepcopy(self.to_dict())
        # Remove the computed 'classifier' property.
        for handler in state_dict['widget']['handlers']:
            del handler['classifier']

        if human_readable_dests:
            # Change the dest ids to human-readable names.
            for handler in state_dict['widget']['handlers']:
                for rule in handler['rules']:
                    if rule['dest'] != feconf.END_DEST:

                        dest_state = State.objects.get(
                            id=rule['dest'], parent=self.parent)

                        rule['dest'] = dest_state.name
        return state_dict

    @classmethod
    def get_by_name(cls, name, exploration, strict=True):
        """Gets a state by name. Fails noisily if strict == True."""
        assert name and exploration
        state = cls.objects.get(parent=exploration, name=name)
        if strict and not state:
            raise Exception('State %s not found.' % name)
        return state

    @classmethod
    def _get_id_from_name(cls, name, exploration):
        """Converts a state name to an id. Handles the END state case."""
        if name == feconf.END_DEST:
            return feconf.END_DEST
        return State.get_by_name(name, exploration).id

    @classmethod
    def modify_using_dict(cls, exploration, state, sdict):
        """Modifies the properties of a state using values from a dict."""
        state.content = [
            Content(type=item['type'], value=item['value'])
            for item in sdict['content']
        ]

        state.param_changes = []
        for pc in sdict['param_changes']:
            instance = exploration.get_param_change_instance(
                pc['name'], pc['obj_type'])
            instance.values = pc['values']
            state.param_changes.append(instance)

        wdict = sdict['widget']
        state.widget = WidgetInstance(
            widget_id=wdict['widget_id'], sticky=wdict['sticky'],
            params=wdict['params'], handlers=[])

        # Augment the list of parameters in state.widget with the default widget
        # params.
        for wp in Widget.objects.get(id=wdict['widget_id']).params:
            if wp.name not in wdict['params']:
                state.widget.params[wp.name] = wp.value

        for handler in wdict['handlers']:
            handler_rules = [Rule(
                name=rule['name'],
                inputs=rule['inputs'],
                dest=State._get_id_from_name(rule['dest'], exploration),
                feedback=rule['feedback']
            ) for rule in handler['rules']]

            state.widget.handlers.append(AnswerHandlerInstance(
                name=handler['name'], rules=handler_rules))

        state.put()
        return state

    def transition(self, answer, params, handler_name):
        """Handle feedback interactions with readers."""

        recorded_answer = answer
        # TODO(sll): This is a special case for multiple-choice input
        # which should really be handled generically.
        if self.widget.widget_id == 'interactive-MultipleChoiceInput':
            recorded_answer = self.widget.params['choices'][int(answer)]

        handlers = [h for h in self.widget.handlers if h.name == handler_name]
        if not handlers:
            raise Exception('No handlers found for %s' % handler_name)
        handler = handlers[0]

        if handler.classifier is None:
            selected_rule = handler.rules[0]
        else:
            # Import the relevant classifier module.
            classifier_module = '.'.join([
                feconf.SAMPLE_CLASSIFIERS_DIR.replace('/', '.'),
                handler.classifier, handler.classifier])
            Classifier = importlib.import_module(classifier_module)

            norm_answer = Classifier.DEFAULT_NORMALIZER().normalize(answer)
            if norm_answer is None:
                raise Exception('Could not normalize %s.' % answer)

            selected_rule = self.find_first_match(
                handler, Classifier, norm_answer, params)

        feedback = (utils.get_random_choice(selected_rule.feedback)
                    if selected_rule.feedback else '')
        return selected_rule.dest, feedback, selected_rule, recorded_answer

    def find_first_match(self, handler, Classifier, norm_answer, params):
        for ind, rule in enumerate(handler.rules):
            if rule.name == 'Default':
                return rule

            func_name, param_list = self.get_classifier_info(
                self.widget.widget_id, handler.name, rule, params)
            param_list = [norm_answer] + param_list
            classifier_output = getattr(Classifier, func_name)(*param_list)

            match, _ = utils.normalize_classifier_return(classifier_output)

            if match:
                return rule

        raise Exception('No matching rule found for handler %s.' % handler.name)

    def get_typed_object(self, mutable_rule, param):
        param_spec = mutable_rule[mutable_rule.find('{{' + param) + 2:]
        param_spec = param_spec[param_spec.find('|') + 1:]
        normalizer_string = param_spec[: param_spec.find('}}')]
        return getattr(objects, normalizer_string)

    def get_classifier_info(self, widget_id, handler_name, rule, state_params):
        classifier_func = rule.name.replace(' ', '')
        first_bracket = classifier_func.find('(')
        mutable_rule = InteractiveWidget.objects.get(id=widget_id).get_readable_name(
            handler_name, rule.name)

        func_name = classifier_func[: first_bracket]
        str_params = classifier_func[first_bracket + 1: -1].split(',')

        param_list = []
        for index, param in enumerate(str_params):
            parsed_param = rule.inputs[param]
            if isinstance(parsed_param, basestring) and '{{' in parsed_param:
                parsed_param = utils.parse_with_jinja(
                    parsed_param, state_params)

            typed_object = self.get_typed_object(mutable_rule, param)
            normalized_param = typed_object.normalize(parsed_param)
            param_list.append(normalized_param)

        return func_name, param_list

    def put(self):
        self._pre_put_hook()
        self.full_clean()
        self.save()
