# -*- coding: utf-8 -*-

import os
import json
from os.path import dirname, join as pjoin
from collections import OrderedDict

DEBUG = False

SENDY_URL = 'https://mailer.hatnote.com/s/'

DEFAULT_LANGUAGE = 'en'
DEFAULT_INTRO = 'Hello there! Welcome to our weekly digest of Wikipedia activity.'
SUBJECT_TMPL = 'Weeklypedia {lang_name} #{issue_number}'

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
                  'uk': 'Ukrainian',
                  'cs': u'Česká',
                  'nn': u'Norwegian (Nynorsk)',
                  'no': u'Norwegian (Bokmål)',
                  'pt': u'Portuguese'}

SENDY_KEY = json.load(open(os.path.join(_CUR_PATH, 'secrets.json'))).get('sendy_key')

DEBUG_ID = 'VN7NFOFUPp5WjrbMSH7Puw'
SENDY_IDS = OrderedDict([('en', 'rFf1E97OGw9qMfZh1F81KA'),
                         ('ca', '9sW1OtFlCbJlYgxSXuahHQ'),
                         ('zh', 'aSQ6TT0VKpw0tmzBPaRZDg'),
                         ('cs', 'ZnzIC6KALxUnATGSCgSL9A'),
                         ('da', '0cs1zVQp3892EjjL0763350TeQ'),
                         #'en': 'ccIjgMNDQjgxlFR8MrQS3g', # load testing
                         ('eo', 'H804892jOtJrNTukmVWOlrbA'),
                         ('et', 'db8mkJ2Tl6pnNUIIVfMFog'),
                         ('fr', 'ELz1OOSd3olC6LSCJmCqhw'),
                         ('de', 't0892Imxu8HTkzoPkrow11MQ'),
                         ('el', 'Ts6mbUlmOCiD0mlWPL8T4A'),
                         ('it', 'EkOruTQZ64fx7V5k9heZNw'),
                         ('kn', 'Dn9KffuyqLRKSY9XAwPCHQ'),
                         ('ko', '65Y8dYqreq2Frkav2WmJ9Q'),
                         ('lv', 'zgfaJH8Jskz7VxNai9zc763A'),
                         ('no', 'YZ8GZhp892aMyCubrWonlk1g'),
                         ('nn', 'zMq9SHu6IJBno892Cksmm1iw'),
                         ('oc', 'OrhmrHkNlTRR9KWNMAgDMQ'),
                         ('fa', 'mRGhgpBb4RnwDe25RtP8fA'),
                         ('pt', 'iSA7TOz98ws763PmuSDz4BNg'),
                         ('ru', 'IUDkAYoiJDQ7P3AQtLIAhQ'),
                         ('es', '5EzGTlwChgHME1TDa763nncA'),
                         ('sv', 'bqpefw4ZBxMBHxrTz9dPKg'),
                         ('te', 'rp4VkbQ1p2QXi560nIrF3w'),
                         ('uk', 'gYfAtFPIVbJgVLkEfpO892Uw'),
                         ('ur', 'QiUlnjE3S9kPdvpzWQdK5Q'),])
                        

SUPPORTED_LANGS = SENDY_IDS.keys()

API_BASE_URL = 'http://weeklypedia.toolforge.org/fetch/'

DATA_BASE_PATH = pjoin(dirname(_CUR_PATH), 'static', 'data')
DATA_PATH_TMPL = '{lang_shortcode}/{date_str}{dev_flag}/weeklypedia_{lang_shortcode}_{date_str}{dev_flag}.json'
DATA_PATH_TMPL = pjoin(DATA_BASE_PATH, DATA_PATH_TMPL)

CUSTOM_INTRO_PATH = pjoin(DATA_BASE_PATH, 'custom_intro.txt')
