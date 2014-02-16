# -*- coding: utf-8 -*-

import os
import json
import urllib2
from datetime import datetime

from clastic import Application, render_json, render_json_dev, render_basic
from clastic.render import AshesRenderFactory
from clastic.meta import MetaApplication
from clastic.middleware import GetParamMiddleware

from mail import Mailinglist, KEY

_CUR_PATH = os.path.dirname(os.path.abspath(__file__))
LANG_MAP = json.load(open(os.path.join(_CUR_PATH, 'language_codes.json')))

API_BASE_URL = 'http://tools.wmflabs.org/weeklypedia/fetch/'
DEFAULT_LANGUAGE = 'en'

HISTORY_FILE = 'history.json'


def fetch_rc(lang=DEFAULT_LANGUAGE):
    if lang not in LANG_MAP:
        raise KeyError('unknown language code: %r' % lang)
    response = urllib2.urlopen(API_BASE_URL + lang)
    content = response.read()
    data = json.loads(content)
    return data


def get_language_list():
    return sorted(LANG_MAP.keys())


def send(sendkey, ashes_env, lang=DEFAULT_LANGUAGE, list_id=''):
    render_ctx = fetch_rc(lang=lang)
    render_ctx['issue_number'] = 2
    render_ctx['language'] = LANG_MAP[lang]
    changes_html = ashes_env.render('template.html', render_ctx)
    changes_text = ashes_env.render('template.txt', render_ctx)
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
    history[lang].append(render_ctx)
    with open(os.path.join(_CUR_PATH, HISTORY_FILE), 'w') as outfile:
        json.dump(history, outfile)
    return 'Success: sent issue %s' % render_ctx['issue_number']


def view_rendered(ashes_env, lang=DEFAULT_LANGUAGE, format=None):
    format = format or 'html'
    render_ctx = fetch_rc(lang=lang)
    render_ctx['issue_number'] = 2
    render_ctx['date'] = datetime.utcnow().strftime('%B %d, %Y')
    render_ctx['short_lang_name'] = lang
    render_ctx['full_lang_name'] = LANG_MAP[lang]
    if format == 'json':
        ret = render_ctx
    elif format == 'html':
        ret = ashes_env.render('template.html', render_ctx)
    else:
        ret = ashes_env.render('template.txt', render_ctx)
    return render_basic(ret)


def load_history():
    with open(os.path.join(_CUR_PATH, HISTORY_FILE)) as infile:
        history = json.load(infile)
    return history


def main_page():
    return ':-|'


def create_app():
    gpm = GetParamMiddleware(['sendkey', 'list_id'])
    routes = [('/', main_page, render_basic),
              ('/meta', MetaApplication()),
              ('/send', send, render_basic),
              ('/_dump_environ', lambda request: request.environ, render_json_dev),
              ('/view', get_language_list, render_basic),
              ('/view/<lang>/<format?>', view_rendered),
              ('/fetch/', fetch_rc, render_json),
              ('/fetch/<lang>', fetch_rc, render_json)]
    ashes_render = AshesRenderFactory(_CUR_PATH, filters={'ci': comma_int})
    resources = {'ashes_env': ashes_render.env}
    return Application(routes, resources, middlewares=[gpm])


def comma_int(val):
    try:
        return '{0:,}'.format(val)
    except ValueError:
        return val


wsgi_app = create_app()


if __name__ == '__main__':
    wsgi_app.serve(use_meta=False)
