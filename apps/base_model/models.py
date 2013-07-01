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

primitive = (basestring, bool, float, int)


class BaseModel(models.Model):
    """A model class containing all common methods"""

    @classmethod
    def attr_list(cls):
        return cls._meta.get_all_field_names()

    def _pre_put_hook(self):
        pass

    def put(self):
        self._pre_put_hook()
        self.full_clean()
        self.save()
        return self

    @classmethod
    def get(cls, entity_id):
        try:
            entity = cls.objects.get(id=entity_id)
        except cls.DoesNotExist:
            entity = None
        return entity

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
            if not cls.get(new_id, strict=False):
                return new_id

        raise Exception('New id generator is producing too many collisions.')

    @classmethod
    def get(cls, entity_id, strict=True):
        """Gets an entity by id. Fails noisily if strict == True."""
        if not entity_id:
            entity = None
        else:
            try:
                entity = cls.objects.get(id=entity_id)
            except cls.DoesNotExist:
                entity = None

        if strict and not entity:
            raise Exception('Entity for class %s with id %s not found' %
                            (cls.__name__, entity_id))
        return entity

    class Meta:
        abstract = True


class DummyModel(models.Model):
    pass

dummymodel = DummyModel()

django_internal_attrs = dir(dummymodel)
internal_attrs = ['_json_field_cache']

all_internal_attrs = django_internal_attrs + internal_attrs
