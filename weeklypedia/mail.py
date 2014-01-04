import mailchimp
from secrets import KEY

ENWP_LIST = 'f811608f69'

class Mailinglist(object):
    def __init__(self, key):
        self.client = mailchimp.Mailchimp(key)
        self.next_campaign = self.get_next_campaign()
        print self.client.helper.ping()

    def new_campaign(self, subject, content, list_id=ENWP_LIST):
        opts = {
            'list_id': list_id,
            'subject': subject,
            'from_email': 'stephenlaporte@gmail.com',
            'from_name': 'Weeklypedia Digest',
            'to_name': 'Weeklypedia Digest'
        }
        cont = {
            'html': content,
        }
        resp = self.client.campaigns.create(type='plaintext',
                                            options=opts,
                                            content=cont)
        self.next_campaign = resp.get('id')
        print resp

    def send_next_campaign(self):
        resp = self.client.campaigns.send(self.next_campaign)
        print resp

    def new_subscriber(self, email, list_id=ENWP_LIST):
        resp = self.client.lists.subscribe(list_id, {'email': email})
        print resp

    def get_next_campaign(self):
        campaigns = self.client.campaigns.list()
        return campaigns['data'][0]['id']

if __name__ == '__main__':
    mc = Mailinglist(KEY)
    import pdb; pdb.set_trace()
