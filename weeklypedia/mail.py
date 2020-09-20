# -*- coding: utf-8 -*-

import os
import json

import requests

from common import SENDY_KEY, SENDY_URL


def sendy_send_campaign(subject, text_content, html_content, list_id):
    url = SENDY_URL + 'api/campaigns/create.php'
    data = {'from_name': 'Weeklypedia Digest',
            'from_email': 'weeklypedia@hatnote.com',
            'reply_to': 'weeklypedia@hatnote.com',
            'title': subject,
            'subject': subject,
            'plain_text': text_content,
            'html_text': html_content,
            'list_ids': list_id,
            'send_campaign': 1,
            'api_key': SENDY_KEY}
    resp = requests.post(url, data=data)
    return resp
