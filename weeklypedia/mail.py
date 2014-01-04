import os
from json import load

import mailchimp

_CUR_PATH = os.path.dirname(os.path.abspath(__file__))
KEY = load(open(os.path.join(_CUR_PATH, 'secrets.json'))).get('mc')


DEFAULT_LIST = 'a5ecbc7404'
#              'f811608f69'
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
        opts = {
            'list_id': list_id,
            'subject': subject,
            'from_email': 'stephenlaporte@gmail.com',
            'from_name': 'Weeklypedia Digest',
            'to_name': 'Weeklypedia Digest'
        }
        cont = {
            'html': html_content,
            'text': text_content,
        }
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
