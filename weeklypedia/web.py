import os
import json
from time import strftime, gmtime
from clastic import Application, render_json, render_json_dev, render_basic
from clastic.render import AshesRenderFactory
from clastic.render import ashes
from clastic.meta import MetaApplication
from clastic.middleware import GetParamMiddleware

from dal import RecentChanges
from mail import Mailinglist, KEY

HISTORY_FILE = 'history.json'
_CUR_PATH = os.path.dirname(os.path.abspath(__file__))

def send(sendkey, lang='et', list_id=''):
    changes_json = fetch_rc(lang=lang)
    ashes_env = ashes.AshesEnv([_CUR_PATH])
    changes_html = ashes_env.render('template.html', changes_json)
    changes_text = ashes_env.render('template.text', changes_json)
    mailinglist = Mailinglist(sendkey + KEY)
    subject = 'Weeklypedia, Issue 2, Estonian Edition'
    mailinglist.new_campaign(subject, 
                             changes_html, 
                             changes_text,
                             list_id=list_id)
    mailinglist.send_next_campaign()
    history = load_history()
    if not history.get(lang):
        history[lang] = []
    history[lang].append(changes_json)
    with open(os.path.join(_CUR_PATH, HISTORY_FILE), 'w') as outfile:
        json.dump(history, outfile)
    return 'Success: sent issue %s' % changes_json['stats']['issue'] 


def fetch_rc(lang='en'):
    history = load_history()
    changes = RecentChanges(lang=lang)
    ret = changes.all()
    ret['stats']['issue'] = 2
    # len(history.get(lang, []))
    ret['stats']['date'] = strftime("%b %d, %Y", gmtime())
    return ret

def load_history():
    with open(os.path.join(_CUR_PATH, HISTORY_FILE)) as infile:
        history = json.load(infile)
    return history
    
def main_page():
    return ':-|'

def create_app():
    sendkey = GetParamMiddleware('sendkey')
    lang = GetParamMiddleware('lang')
    list_id = GetParamMiddleware('list_id')
    routes = [('/', main_page, render_basic),
              ('/meta', MetaApplication),
              ('/send', send, render_basic),
              ('/_dump_environ', lambda request: request.environ, render_json_dev),
              ('/fetch/', fetch_rc, render_json),
              ('/fetch/<lang>', fetch_rc, render_json)]
    ashes_render = AshesRenderFactory(_CUR_PATH, filters={'ci': comma_int})
    return Application(routes, [], ashes_render, middlewares=[sendkey])

def comma_int(val):                                                                                      
    try:                                                                                                 
        return '{0:,}'.format(val)                                                                       
    except ValueError:                                                                                   
        return val


wsgi_app = create_app()
