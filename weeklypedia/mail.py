# -*- coding: utf-8 -*-

import os
import json

import requests

import mailchimp

_CUR_PATH = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(_CUR_PATH, 'secrets.json')) as secrets_json:
    secrets = json.load(secrets_json)
    KEY = secrets.get('mc')
    SENDY_KEY = secrets.get('sendy_key')

SENDY_URL = 'https://mailer.hatnote.com/s/'
TEST_LIST_ID = "a5ecbc7404"
DEFAULT_LIST = TEST_LIST_ID

#              'f811608f69'


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


class Mailinglist(object):
    def __init__(self, key):
        self.client = mailchimp.Mailchimp(key)
        self.next_campaign = self.get_next_campaign()
        print self.client.helper.ping()

    def new_campaign(self,
                     subject,
                     html_content,
                     text_content,
                     list_id=DEFAULT_LIST):
        opts = {'list_id': list_id,
                'subject': subject,
                'from_email': 'weeklypedia@hatnote.com',
                'from_name': 'Weeklypedia Digest',
                'to_name': 'Weeklypedia Digest'}
        cont = {'html': html_content,
                'text': text_content}
        resp = self.client.campaigns.create(type='regular',
                                            options=opts,
                                            content=cont)
        self.next_campaign = resp.get('id')
        print resp

    def send_next_campaign(self):
        resp = self.client.campaigns.send(self.next_campaign)
        print resp

    def new_subscriber(self, email, list_id=DEFAULT_LIST):
        resp = self.client.lists.subscribe(list_id, {'email': email})
        print resp

    def get_next_campaign(self):
        campaigns = self.client.campaigns.list()
        return campaigns['data'][0]['id']


if __name__ == '__main__':
    mc = Mailinglist(KEY)
    import pdb; pdb.set_trace()
