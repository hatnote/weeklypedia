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
SENDKEY = json.load(open(os.path.join(_CUR_PATH, 'secrets.json'))).get('key')
SUPPORTED_LANGS = ['en', 'de', 'fr', 'ko', 'et', 'sv', 'it', 'ca']
API_BASE_URL = 'http://tools.wmflabs.org/weeklypedia/fetch/'

DATA_BASE_PATH = pjoin(dirname(_CUR_PATH), 'static', 'data')
DATA_PATH_TMPL = '{lang_shortcode}/{date_str}{dev_flag}/weeklypedia_{lang_shortcode}_{date_str}{dev_flag}.json'
DATA_PATH_TMPL = pjoin(DATA_BASE_PATH, DATA_PATH_TMPL)

CUSTOM_INTRO_PATH = pjoin(DATA_BASE_PATH, 'custom_intro.txt')


def mkdir_p(path):
    # bolton
    import errno
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            return
        raise
