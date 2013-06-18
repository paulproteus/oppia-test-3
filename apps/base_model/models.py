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

"""Base model class."""

__author__ = 'Sean Lip'

import base64
import hashlib

from oppia import utils

from django.db import models

primitive = (int, bool, basestring)


class BaseModel(models.Model):
    """A model class containing all common methods"""

    json_field_schema = {}
    simple_attrs = []

    def _pre_put_hook(self):
        pass

    def __setattr__(self, item, value):
        if item in self.json_field_schema and isinstance(value, (list, dict)):
            assert type(self.json_field_schema[item]) == type(value)
            try:
                if isinstance(value, list):
                    for val in value:
                        assert isinstance(val, self.json_field_schema[item][0])
                    self.__dict__['_%s' % item] = Converter.encode(value)
                elif isinstance(value, dict):
                    for key, val in value:
                        assert key in self.json_field_schema[item].keys()
                        assert isinstance(val, self.json_field_schema[item][key])
                    self.__dict__['_%s' % item] = Converter.encode(value)
            except Exception as e:
                raise ValueError(e)
        elif item in all_internal_attrs or item in self.simple_attrs:
            self.__dict__[item] = value
        elif item[0] == '_' and item[1:] in self.json_field_schema:
            self.__dict__[item] = value
        else:
            raise AttributeError(item)

    def __getattr__(self, item):
        schema = self.json_field_schema
        if item in schema and \
                isinstance(schema[item], list):
            if isinstance(schema[item][0], primitive):
                return self.__dict__['_%s' % item]
            elif isinstance(schema[item][0], object):
                object_list = []
                obj_class = schema[item][0]
                arg_list = obj_class.json_field_schema.keys() \
                    + obj_class.simple_attrs
                for instance in self.__dict__['_%s' % item]:
                    arg_dict = {}
                    for arg in arg_list:
                        arg_dict[arg] = instance['__%s__' % (
                            obj_class.__name__)].get(arg)
                    obj = obj_class(**arg_dict)
                    object_list.append(obj)
                return object_list
        else:
            return self.__getattribute__(item)

    def put(self):
        self._pre_put_hook()
        self.full_clean()
        self.save()

    class Meta:
        abstract = True


class IdModel(BaseModel):
    """A model stub which has an explicit id property."""
    id = models.CharField(max_length=100, primary_key=True)

    @classmethod
    def get_new_id(cls, entity_name):
        """Gets a new 12-character id for an entity, based on its name.

        Raises:
            Exception: if an id cannot be generated within a reasonable number
              of attempts.
        """
        MAX_RETRIES = 10
        RAND_RANGE = 127*127
        for i in range(MAX_RETRIES):
            new_id = base64.urlsafe_b64encode(
                hashlib.sha1(
                    '%s%s' % (entity_name.encode('utf-8'),
                              utils.get_random_int(RAND_RANGE))
                ).digest())[:12]
            if not cls.objects.get(id=new_id):
                return new_id

        raise Exception('New id generator is producing too many collisions.')

    @classmethod
    def get(cls, entity_id, strict=True, parent=None):
        """Gets an entity by id. Fails noisily if strict == True."""
        entity = cls.get_by_id(entity_id, parent=parent)
        if strict and not entity:
            raise Exception('Entity for class %s with id %s not found' %
                            (cls.__name__, entity_id))
        return entity

    class Meta:
        abstract = True


class Converter():
    """A class containing different encoder/decoder functions."""

    @classmethod
    def encode(cls, obj):
        """A custom encoder to encode both built-in and custom objects into
        JSON-serializable python objects recursively.

        Custom objects are encoded as dict with one key, '__TypeName__' where
        'TypeName' is the actual name of the class to which the object belongs.
        That single key maps to another dict which is just the encoded __dict__
        of the object being encoded."""

        if isinstance(
            obj, (int, long, float, complex, bool, basestring, type(None))
        ):
            return obj
        elif isinstance(obj, list):
            return [cls.encode(item) for item in obj]
        elif isinstance(obj, (set, tuple, complex)):
            raise NotImplementedError
        elif isinstance(obj, dict):
            result = {}
            for key in obj:
                # Every Model instance in django has a ModelState object,
                # which we don't want to be serialized. Hence, we get rid
                # of it.
                if key != '__ModelState__':
                    result[key] = cls.encode(obj[key])
            return result
        else:
            obj_dict = cls.encode(obj.__dict__)
            return {'__%s__' % (obj.__class__.__name__): obj_dict}


class DummyModel(models.Model):
    pass

dummymodel = DummyModel()

django_internal_attrs = dir(dummymodel)
internal_attrs = ['_json_field_cache', ]

all_internal_attrs = django_internal_attrs + internal_attrs
