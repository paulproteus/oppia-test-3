# coding: utf-8
#
# Copyright 2012 Google Inc. All Rights Reserved.
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

"""Stores various configuration options and constants for Oppia."""

import os
import jinja2

# Code contributors, in alphabetical order.
CODE_CONTRIBUTORS = [
    'Jeremy Emerson',
    'Koji Ashida',
    'Manas Tungare',
    'Reinaldo Aguiar',
    'Sean Lip',
    'Stephanie Federwisch',
    'Wilson Hong',
    'Yana Malysheva',
]

# Idea contributors, in alphabetical order.
IDEA_CONTRIBUTORS = [
    'Alex Kauffmann',
    'Catherine Colman',
    'John Cox',
    'Neil Fraser',
    'Pavel Simakov',
    'Peter Norvig',
    'Phil Wagner',
    'Philip Guo',
]

# Demo explorations to load on startup. The id assigned to each exploration
# is based on the index of the exploration in this list, so if you want to
# add a new exploration and preserve the existing ids, add that exploration
# to the end of the list.
# Each item is represented as a tuple: (filename, title, category, image_name).
# The fourth element is optional. Note that the filename omits the .yaml suffix.
# The images are in /data/images.
DEMO_EXPLORATIONS = [
    ('welcome', 'Welcome to Oppia!', 'Welcome'),
    ('pitch', 'Pitch Perfect', 'Music', 'pitch.png'),
    ('counting', 'Three Balls', 'Mathematics', 'counting.png'),
    ('boot_verbs', 'Boot Verbs', 'Languages', 'boot_verbs.png'),
    ('hola', '¡Hola!', 'Languages'),
    ('landmarks', 'Landmarks', 'Geography'),
    ('adventure', 'Parametrized Adventure', 'Interactive Fiction'),
]

# Whether to unconditionally log info messages.
DEBUG = False

# Whether we should serve the development or production experience.
DEV = (os.environ.get('SERVER_SOFTWARE')
       and os.environ['SERVER_SOFTWARE'].startswith('Development'))

# The directory containing the HTML/JS/CSS templates.
TEMPLATE_DIR = os.path.join(
    os.path.dirname(__file__),
    'templates/dev/head' if DEV else 'templates/prod/head'
)

# The directory containing third-party files.
THIRD_PARTY_DIR = 'third_party'

# The directory containing this file (used for finding embedded data)
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.join(_THIS_DIR, 'data')

# The directories containing sample classifiers, explorations and widgets.
SAMPLE_CLASSIFIERS_DIR = os.path.join(_DATA_DIR, 'classifiers')
SAMPLE_EXPLORATIONS_DIR = os.path.join(_DATA_DIR, 'explorations')
SAMPLE_IMAGES_DIR = os.path.join(_DATA_DIR, 'images')
INTERACTIVE_WIDGETS_DIR = os.path.join(_DATA_DIR, 'widgets/interactive')
NONINTERACTIVE_WIDGETS_DIR = os.path.join(_DATA_DIR, 'widgets/noninteractive')

OBJECT_TEMPLATES_DIR = os.path.join(_DATA_DIR, 'objects/templates')

# The jinja environment used for loading object view and edit templates.
OBJECT_JINJA_ENV = jinja2.Environment(
    autoescape=True,
    loader=jinja2.FileSystemLoader(os.path.join(
        os.path.dirname(__file__), OBJECT_TEMPLATES_DIR))
)

# The jinja environment used for loading frontend templates.
loader = jinja2.FileSystemLoader(TEMPLATE_DIR)
JINJA_ENV = jinja2.Environment(autoescape=True, loader=loader)


def include_js_file(name):
    """Include a raw JS file in the template without evaluating it."""
    assert name.endswith('.js')
    return jinja2.Markup(loader.get_source(JINJA_ENV, name)[0])

JINJA_ENV.globals['include_js_file'] = include_js_file
JINJA_ENV.filters.update({
    'is_list': lambda x: isinstance(x, list),
    'is_dict': lambda x: isinstance(x, dict),
})

END_DEST = 'END'

# Default name for a state.
DEFAULT_STATE_NAME = '[untitled state]'

# Default file name for newly-created files for download.
DEFAULT_FILE_NAME = 'New file'

ACCEPTED_IMAGE_FORMATS = [('gif', 'gif'), ('jpeg', 'jpeg'), ('png', 'png')]

# Set this to True to allow file uploads via YAML in the gallery and editor pages.
ALLOW_YAML_FILE_UPLOAD = False

# Prefixes for widget ids in the datastore.
INTERACTIVE_PREFIX = 'interactive'
NONINTERACTIVE_PREFIX = 'noninteractive'
