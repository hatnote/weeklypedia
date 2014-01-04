import os
from clastic import Application, render_json, render_json_dev, render_basic
from clastic.render import AshesRenderFactory
from clastic.render.ashes import AshesEnv
from clastic.meta import MetaApplication

from dal import RecentChanges
from mail import Mailinglist, KEY

_CUR_PATH = os.path.dirname(os.path.abspath(__file__))

def send(lang='en'):
	changes = RecentChanges(lang=lang)
	env = AshesEnv([_CUR_PATH])
	mail = env.render('template.html', changes.all())
	mailinglist = Mailinglist(KEY)
	mailinglist.new_campaign('Wikipedia digest (Issue 1)', mail)
	mailinglist.send_next_campaign()
	return 'mail sent'


def fetch_rc(lang='en'):
    changes = RecentChanges(lang=lang)
    return changes.all()


def create_app():
    routes = [('/', fetch_rc, render_json),
              ('/meta', MetaApplication),
              ('/send', send, render_basic),
              ('/_dump_environ', lambda request: request.environ, render_json_dev),
              ('/fetch/', fetch_rc, 'template.html'),
              ('/fetch/<lang>', fetch_rc, 'template.html')]
    ashes_render = AshesRenderFactory(_CUR_PATH, filters={'ci': comma_int})
    return Application(routes, [], ashes_render)


def comma_int(val):                                                                                      
    try:                                                                                                 
        return '{0:,}'.format(val)                                                                       
    except ValueError:                                                                                   
        return val


wsgi_app = create_app()