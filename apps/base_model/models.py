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


class BaseModel(models.Model):
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
