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

EMAIL = '''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;">
<head style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;">
<meta name="viewport" content="width=device-width" style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;">
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;">
<title style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;">the WEEKLYPEDIA (1 / 1)</title>

</head>
 
<body bgcolor="#ede0ce" style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;-webkit-font-smoothing: antialiased;-webkit-text-size-adjust: none;height: 100%;width: 100%;">

<!-- body -->
<table class="body-wrap" style="margin: 0;padding: 20px;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;width: 100%;">
        <tr style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;">
                <td style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;"></td>
                <td class="container" bgcolor="#fff" style="margin: 0 auto;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;border: 1px solid #f0f0f0;display: block;max-width: 600px;clear: both;">

                        <!-- content -->
                        <div class="content" style="margin: 0 auto;padding: 20px;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;max-width: 600px;display: block;">
                        <table style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;width: 100%;">
                                <tr style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;">
                                        <td style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;">
                                                <h1 style="margin: 40px 0 10px;padding: 0;font: 800 &quot;serif&quot;;font-size: 36px;line-height: 1.2;text-transform: uppercase;margin-bottom: 15px;color: #000;font-weight: 200;text-align: center;border-top: 1px solid #222222;margin-top: 58px;"><span style="margin: 0;padding: 0 20px;font: 400 14px/21px;font-size: 100%;line-height: 1.6;text-transform: none;position: relative;top: -28px;background: #fff;"><em style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;">the</em> WEEKLYPEDIA</span></h1>
                                                <p style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 14px;line-height: 1.6;margin-bottom: 10px;font-weight: normal;"><em style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;">Volume 1, Issue 1 (en Wikipedia)</em></p>
                                                <p style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 14px;line-height: 1.6;margin-bottom: 10px;font-weight: normal;">Hello there, welcome to our first weekly digest of Wikipedia activity.</p>
                                                <h2 style="margin: 40px 0 10px;padding: 0;font: 800 &quot;serif&quot;;font-size: 28px;line-height: 1.2;text-transform: uppercase;margin-bottom: 15px;color: #000;font-weight: 200;">Articles</h2>
                                                <p style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 14px;line-height: 1.6;margin-bottom: 10px;font-weight: normal;">This week, 32448 authors made 663298 contributions to 295103 different articles. The top 20 articles for the week:</p>
                                                <ol style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 14px;line-height: 1.6;margin-bottom: 10px;font-weight: normal;">
                                                        
                                                        <li style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;margin-left: 5px;list-style-position: inside;"><a href="https://en.wikipedia.org/wiki/Gun_control" target="_blank" style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;color: #348eda;">Gun_control</a> (577 contributions by 31 authors)</li>
                                                        
                                                        <li style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;margin-left: 5px;list-style-position: inside;"><a href="https://en.wikipedia.org/wiki/Genesis_creation_narrative" target="_blank" style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;color: #348eda;">Genesis_creation_narrative</a> (419 contributions by 46 authors)</li>
                                                        
                                                        <li style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;margin-left: 5px;list-style-position: inside;"><a href="https://en.wikipedia.org/wiki/Pamela_Geller" target="_blank" style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;color: #348eda;">Pamela_Geller</a> (205 contributions by 19 authors)</li>
                                                        
                                                        <li style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;margin-left: 5px;list-style-position: inside;"><a href="https://en.wikipedia.org/wiki/Cities_and_towns_during_the_Syrian_Civil_War" target="_blank" style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;color: #348eda;">Cities_and_towns_during_the_Syrian_Civil_War</a> (163 contributions by 20 authors)</li>
                                                        
                                                        <li style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;margin-left: 5px;list-style-position: inside;"><a href="https://en.wikipedia.org/wiki/List_of_scientists_opposing_the_mainstream_scientific_assessment_of_global_warming" target="_blank" style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;color: #348eda;">List_of_scientists_opposing_the_mainstream_scientific_assessment_of_global_warming</a> (157 contributions by 22 authors)</li>
                                                        
                                                        <li style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;margin-left: 5px;list-style-position: inside;"><a href="https://en.wikipedia.org/wiki/Phil_Robertson" target="_blank" style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;color: #348eda;">Phil_Robertson</a> (132 contributions by 18 authors)</li>
                                                        
                                                        <li style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;margin-left: 5px;list-style-position: inside;"><a href="https://en.wikipedia.org/wiki/United_States" target="_blank" style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;color: #348eda;">United_States</a> (126 contributions by 11 authors)</li>
                                                        
                                                        <li style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;margin-left: 5px;list-style-position: inside;"><a href="https://en.wikipedia.org/wiki/Nazism" target="_blank" style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;color: #348eda;">Nazism</a> (121 contributions by 9 authors)</li>
                                                        
                                                        <li style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;margin-left: 5px;list-style-position: inside;"><a href="https://en.wikipedia.org/wiki/Single-payer_health_care" target="_blank" style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;color: #348eda;">Single-payer_health_care</a> (116 contributions by 6 authors)</li>
                                                        
                                                        <li style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;margin-left: 5px;list-style-position: inside;"><a href="https://en.wikipedia.org/wiki/Edward_Makuka_Nkoloso" target="_blank" style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;color: #348eda;">Edward_Makuka_Nkoloso</a> (106 contributions by 6 authors)</li>
                                                        
                                                        <li style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;margin-left: 5px;list-style-position: inside;"><a href="https://en.wikipedia.org/wiki/Acupuncture" target="_blank" style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;color: #348eda;">Acupuncture</a> (103 contributions by 11 authors)</li>
                                                        
                                                        <li style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;margin-left: 5px;list-style-position: inside;"><a href="https://en.wikipedia.org/wiki/Traditional_Chinese_medicine" target="_blank" style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;color: #348eda;">Traditional_Chinese_medicine</a> (100 contributions by 10 authors)</li>
                                                        
                                                        <li style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;margin-left: 5px;list-style-position: inside;"><a href="https://en.wikipedia.org/wiki/Libertarianism" target="_blank" style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;color: #348eda;">Libertarianism</a> (98 contributions by 9 authors)</li>
                                                        
                                                        <li style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;margin-left: 5px;list-style-position: inside;"><a href="https://en.wikipedia.org/wiki/Main_Page" target="_blank" style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;color: #348eda;">Main_Page</a> (89 contributions by 52 authors)</li>
                                                        
                                                        <li style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;margin-left: 5px;list-style-position: inside;"><a href="https://en.wikipedia.org/wiki/Anti-Serb_pogrom_in_Sarajevo" target="_blank" style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;color: #348eda;">Anti-Serb_pogrom_in_Sarajevo</a> (89 contributions by 14 authors)</li>
                                                        
                                                        <li style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;margin-left: 5px;list-style-position: inside;"><a href="https://en.wikipedia.org/wiki/Rupert_Sheldrake" target="_blank" style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;color: #348eda;">Rupert_Sheldrake</a> (86 contributions by 11 authors)</li>
                                                        
                                                        <li style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;margin-left: 5px;list-style-position: inside;"><a href="https://en.wikipedia.org/wiki/Soccer_in_Australia" target="_blank" style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;color: #348eda;">Soccer_in_Australia</a> (85 contributions by 7 authors)</li>
                                                        
                                                        <li style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;margin-left: 5px;list-style-position: inside;"><a href="https://en.wikipedia.org/wiki/Bitcoin" target="_blank" style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;color: #348eda;">Bitcoin</a> (82 contributions by 10 authors)</li>
                                                        
                                                        <li style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;margin-left: 5px;list-style-position: inside;"><a href="https://en.wikipedia.org/wiki/Thomas_Jefferson" target="_blank" style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;color: #348eda;">Thomas_Jefferson</a> (80 contributions by 10 authors)</li>
                                                        
                                                        <li style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;margin-left: 5px;list-style-position: inside;"><a href="https://en.wikipedia.org/wiki/Far-right_politics" target="_blank" style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;color: #348eda;">Far-right_politics</a> (80 contributions by 7 authors)</li>
                                                        
                                                </ol>
                                                <h2 style="margin: 40px 0 10px;padding: 0;font: 800 &quot;serif&quot;;font-size: 28px;line-height: 1.2;text-transform: uppercase;margin-bottom: 15px;color: #000;font-weight: 200;">Discussions</h2>
                                                <p style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 14px;line-height: 1.6;margin-bottom: 10px;font-weight: normal;">The most active 5 discussions:</p>
                                                <ol style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 14px;line-height: 1.6;margin-bottom: 10px;font-weight: normal;">
                                                        
                                                        <li style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;margin-left: 5px;list-style-position: inside;"><a href="https://en.wikipedia.org/wiki/Gun_control" target="_blank" style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;color: #348eda;">Gun_control</a> (31 authors)</li>
                                                        
                                                        <li style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;margin-left: 5px;list-style-position: inside;"><a href="https://en.wikipedia.org/wiki/Genesis_creation_narrative" target="_blank" style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;color: #348eda;">Genesis_creation_narrative</a> (46 authors)</li>
                                                        
                                                        <li style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;margin-left: 5px;list-style-position: inside;"><a href="https://en.wikipedia.org/wiki/Pamela_Geller" target="_blank" style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;color: #348eda;">Pamela_Geller</a> (19 authors)</li>
                                                        
                                                        <li style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;margin-left: 5px;list-style-position: inside;"><a href="https://en.wikipedia.org/wiki/Cities_and_towns_during_the_Syrian_Civil_War" target="_blank" style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;color: #348eda;">Cities_and_towns_during_the_Syrian_Civil_War</a> (20 authors)</li>
                                                        
                                                        <li style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;margin-left: 5px;list-style-position: inside;"><a href="https://en.wikipedia.org/wiki/List_of_scientists_opposing_the_mainstream_scientific_assessment_of_global_warming" target="_blank" style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;color: #348eda;">List_of_scientists_opposing_the_mainstream_scientific_assessment_of_global_warming</a> (22 authors)</li>
                                                        
                                                </ol>
                                                <p style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 14px;line-height: 1.6;margin-bottom: 10px;font-weight: normal;">Learn more about the <a href="#" style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;color: #348eda;">Weeklypedia Digest</a>
                                        </p></td>
                                </tr>
                        </table>
                        </div>
                        <!-- /content -->
                                                                        
                </td>
                <td style="margin: 0;padding: 0;font: &quot;serif&quot;;font-size: 100%;line-height: 1.6;"></td>
        </tr>
</table>
<!-- /body -->

</body>
</html>
'''

if __name__ == '__main__':
    mc = Mailinglist(KEY)
    import pdb; pdb.set_trace()
