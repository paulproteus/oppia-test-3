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

"""Models for typed instances."""

__author__ = 'Sean Lip'

from oppia.data.objects.models import objects

from django.db import models
from json_field import JSONField


def get_object_class(cls_name):
    """Gets the object class based on the class name."""
    try:
        assert cls_name != 'BaseObject'

        object_class = getattr(objects, cls_name)
        assert object_class
    except Exception:
        raise TypeError('\'%s\' is not a valid typed object class.' % cls_name)

    return object_class


class TypedInstance(models.Model):
    """Represents an instance of a typed object."""
    def _pre_put_hook(self):
        """Does validation before the model is put into the datastore.

        IMPORTANT: If this model is used as a StructuredProperty in another
        model, this validation hook will NOT be called. Use a
        TypedInstanceProperty instead.
        """
        object_class = get_object_class(self.obj_type)
        return object_class.normalize(self.value)

    # The name of the object's class.
    obj_type = models.CharField(max_length=100)
    # A normalized Python representation of the instance's value.
    value = JSONField()

    def put(self):
        self.full_clean()
        self._pre_put_hook()
        self.save()
