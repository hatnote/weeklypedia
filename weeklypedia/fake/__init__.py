# -*- coding: utf-8 -*-

import os
import json

_CUR_PATH = os.path.dirname(os.path.abspath(__file__))
fake_data = {'en': json.load(open(_CUR_PATH + '/fake_en_data.json'))}


def fake_fetch_rc(lang=None):
    return fake_data.get(lang, fake_data['en'])
