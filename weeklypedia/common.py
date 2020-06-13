# -*- coding: utf-8 -*-

import os
import json
from os.path import dirname, join as pjoin

DEBUG = False

DEFAULT_LANGUAGE = 'en'
DEFAULT_INTRO = 'Hello there! Welcome to our weekly digest of Wikipedia activity.'
SUBJECT_TMPL = 'Weeklypedia {lang_name} #{issue_number}'

DEBUG_LIST_ID = "a5ecbc7404"

_CUR_PATH = dirname(os.path.abspath(__file__))

LANG_MAP = json.load(open(pjoin(_CUR_PATH, 'language_codes.json')))
LOCAL_LANG_MAP = {'en': u'English',
                  'de': u'Deutsch',
                  'fr': u'Français',
                  'ko': u'한국어',
                  'et': u'Eesti',
                  'sv': u'Svenska',
                  'da': u'Dansk',
                  'it': u'Italiano',
                  'ca': u'Català',
                  'es': u'Español',
                  'fa': u'فارسی',
                  'ur': u'اردو',
                  'zh': u'中文',
                  'kn': u'ಕನ್ನಡ',
                  'lv': u'Latvian',
                  'el': u'ελληνική',
                  'te': u'తెలుగు',
                  'oc': 'Occitan',
                  'ru': 'Russian',
                  'uk': 'Ukrainian'}
SENDKEY = json.load(open(os.path.join(_CUR_PATH, 'secrets.json'))).get('key')
SUPPORTED_LANGS = ['en', 'de', 'fr', 'ko', 'et', 'sv', 'da', 'it', 'ca', 'es',
                   'fa', 'zh', 'ur', 'kn', 'lv', 'el', 'te', 'oc', 'ru', 'uk']
API_BASE_URL = 'http://weeklypedia.toolforge.org/fetch/'

ARCHIVE_BASE_PATH = pjoin(dirname(_CUR_PATH), 'static', 'archive')

DATA_BASE_PATH = pjoin(dirname(_CUR_PATH), 'static', 'data')
DATA_PATH_TMPL = '{lang_shortcode}/{date_str}{dev_flag}/weeklypedia_{lang_shortcode}_{date_str}{dev_flag}.json'
DATA_PATH_TMPL = pjoin(DATA_BASE_PATH, DATA_PATH_TMPL)

CUSTOM_INTRO_PATH = pjoin(DATA_BASE_PATH, 'custom_intro.txt')

SIGNUP_MAP = {'en': 'http://eepurl.com/MMlpX',
              'de': 'http://eepurl.com/MMlG9',
              'fr': 'http://eepurl.com/MMmVX',
              'ko': 'http://eepurl.com/MMm8n',
              'et': 'http://eepurl.com/MMnlf',
              'sv': 'http://eepurl.com/MMTnP',
              'da': 'http://eepurl.com/Sko4L',
              'it': 'http://eepurl.com/MQTPb',
              'ca': 'http://eepurl.com/M7HU9',
              'eo': 'http://eepurl.com/_RE_X',
              'es': 'http://eepurl.com/br8NNj',
              'fa': 'http://eepurl.com/br8TlT',
              'zh': 'http://eepurl.com/bsmGhT',
              'ur': 'http://eepurl.com/bsmG1P',
              'kn': 'http://eepurl.com/buxugf',
              'lv': 'http://eepurl.com/b0V-yj',
              'el': 'http://eepurl.com/b0WcUr',
              'te': 'http://eepurl.com/b3EjMn',
              'oc': 'http://eepurl.com/dxJIYf',
              'ru': 'http://eepurl.com/dxJJGn',
              'uk': 'http://eepurl.com/dxJKwf'}


def mkdir_p(path):
    # bolton
    import errno
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            return
        raise
