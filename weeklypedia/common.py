# -*- coding: utf-8 -*-

import os
import json
from os.path import dirname, join as pjoin
from boltons.fileutils import mkdir_p

DEBUG = False

DEFAULT_LANGUAGE = 'en'
DEFAULT_INTRO = 'Hello there! Welcome to our weekly digest of Wikipedia activity.'
SUBJECT_TMPL = 'Weeklypedia {lang_name} #{issue_number}'

DEBUG_LIST_ID = "a5ecbc7404"

_CUR_PATH = dirname(os.path.abspath(__file__))

LANG_MAP = json.load(open(pjoin(_CUR_PATH, 'language_codes.json')))
LOCAL_LANG_MAP = {'en': u'English',
                  'de': u'Deutsch',
                  'eo': u'Esperanto',
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

SENDY_IDS = {'ca': '9sW1OtFlCbJlYgxSXuahHQ',
             'zh': 'aSQ6TT0VKpw0tmzBPaRZDg',
             'da': '0cs1zVQp3892EjjL0763350TeQ',
             'en': 'rFf1E97OGw9qMfZh1F81KA',
             #'en': 'VN7NFOFUPp5WjrbMSH7Puw', # debug
             'es': 'HTPao3LPmzm0UrCNxfBUgA',
             'eo': 'H804892jOtJrNTukmVWOlrbA',
             'et': 'db8mkJ2Tl6pnNUIIVfMFog',
             'fr': 'ELz1OOSd3olC6LSCJmCqhw',
             'de': 't0892Imxu8HTkzoPkrow11MQ',
             'it': 'EkOruTQZ64fx7V5k9heZNw',
             'kn': 'Dn9KffuyqLRKSY9XAwPCHQ',
             'ko': '65Y8dYqreq2Frkav2WmJ9Q',
             'lv': 'zgfaJH8Jskz7VxNai9zc763A',
             'sv': 'bqpefw4ZBxMBHxrTz9dPKg',
             'fa': 'mRGhgpBb4RnwDe25RtP8fA',
             'el': 'Ts6mbUlmOCiD0mlWPL8T4A',
             'oc': 'OrhmrHkNlTRR9KWNMAgDMQ',
             'ru': 'IUDkAYoiJDQ7P3AQtLIAhQ',
             'es': '5EzGTlwChgHME1TDa763nncA',
             'te': 'rp4VkbQ1p2QXi560nIrF3w',
             'ur': 'QiUlnjE3S9kPdvpzWQdK5Q',
             'uk': 'gYfAtFPIVbJgVLkEfpO892Uw '}

SUPPORTED_LANGS = SENDY_IDS.keys()

API_BASE_URL = 'http://weeklypedia.toolforge.org/fetch/'

ARCHIVE_BASE_PATH = pjoin(dirname(_CUR_PATH), 'static', 'archive')
ARCHIVE_URL = 'https://weekly.hatnote.com/archive/%s/index.html'

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


# def mkdir_p(path):
#     # bolton
#     import errno
#     try:
#         os.makedirs(path)
#     except OSError as exc:
#         if exc.errno == errno.EEXIST and os.path.isdir(path):
#             return
#         raise
