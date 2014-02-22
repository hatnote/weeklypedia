# -*- coding: utf-8 -*-

import os
import json
import urllib2
from datetime import datetime
from os.path import dirname, join as pjoin

import sys
sys.path.insert(0, os.path.expanduser('~/projects/clastic'))

from clastic import Application, render_json, render_json_dev, render_basic
from clastic.render import AshesRenderFactory
from clastic.meta import MetaApplication
from clastic.middleware import GetParamMiddleware
from clastic.static import StaticApplication


from mail import Mailinglist, KEY

ENABLE_FAKE = True

_CUR_PATH = dirname(os.path.abspath(__file__))
LANG_MAP = json.load(open(pjoin(_CUR_PATH, 'language_codes.json')))

ARCHIVE_BASE_PATH = pjoin(dirname(_CUR_PATH), 'static', 'archive')
ARCHIVE_PATH_TMPL = '{lang_shortcode}/{date_str}{dev_flag}/weeklypedia_{date_str}{dev_flag}.{fmt}'
ARCHIVE_PATH_TMPL = pjoin(ARCHIVE_BASE_PATH, ARCHIVE_PATH_TMPL)

API_BASE_URL = 'http://tools.wmflabs.org/weeklypedia/fetch/'
DEFAULT_LANGUAGE = 'en'

HISTORY_FILE = 'history.json'
STATIC_PATH = os.path.abspath(_CUR_PATH + '/../static/')


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
    with open(pjoin(_CUR_PATH, HISTORY_FILE), 'w') as outfile:
        json.dump(history, outfile)
    return 'Success: sent issue %s' % render_ctx['issue_number']


def get_past_issue_paths(lang, include_dev=False):
    ret = []
    lang_path = pjoin(ARCHIVE_BASE_PATH, lang)
    if not os.path.isdir(lang_path):
        return ret
    past_issue_fns = os.listdir(lang_path)
    for fn in past_issue_fns:
        if not include_dev and fn.endswith('_dev'):
            continue
        full_path = pjoin(lang_path, fn)
        if os.path.isdir(full_path):
            ret.append(full_path)
    return ret


def get_current_issue_number(lang):
    past_issue_count = len(get_past_issue_paths(lang, include_dev=False))
    return past_issue_count + 1


def get_issue_data(lang=DEFAULT_LANGUAGE):
    basic_info = {'short_lang_name': lang,
                  'full_lang_name': LANG_MAP[lang]}
    basic_info['issue_number'] = get_current_issue_number(lang)
    basic_info['date'] = datetime.utcnow().strftime('%B %d, %Y')
    render_ctx = fetch_rc(lang=lang)
    render_ctx.update(basic_info)
    return render_ctx


def get_rendered_issue(ashes_env, lang=DEFAULT_LANGUAGE, format=None):
    render_ctx = get_issue_data(lang)
    return _render_issue(render_ctx, ashes_env, format=format)


def _render_issue(render_ctx, ashes_env, format=None):
    format = format or 'html'
    if format == 'json':
        ret = json.dumps(render_ctx, indent=2, sort_keys=True)
    elif format == 'html':
        ret = ashes_env.render('template.html', render_ctx).encode('utf-8')
    elif format == 'web':
        ret = ashes_env.render('template_nostyles.html', render_ctx).encode('utf-8')
    else:
        ret = ashes_env.render('template.txt', render_ctx).encode('utf-8')
    return ret


def render_and_save_all_formats(ashes_env, lang=DEFAULT_LANGUAGE, is_dev=True):
    ret = []
    render_ctx = get_issue_data(lang=lang)
    for fmt in ('html', 'json', 'txt'):
        fargs = {'fmt': fmt,
                 'date_str': datetime.utcnow().strftime('%Y%m%d'),
                 'lang_shortcode': lang,
                 'dev_flag': ''}
        if is_dev:
            fargs['dev_flag'] = '_dev'
        out_path = ARCHIVE_PATH_TMPL.format(**fargs)
        try:
            out_file = open(out_path, 'w')
        except IOError:
            mkdir_p(os.path.dirname(out_path))
            out_file = open(out_path, 'w')
            # if exception, couldn't create file or parent directories
        with out_file:
            rendered = _render_issue(render_ctx, ashes_env, format=fmt)
            out_file.write(rendered)
        ret.append((out_path, len(rendered)))
    return ret


def mkdir_p(path):
    # bolton
    import os
    import errno
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            return
        raise


def load_history():
    with open(pjoin(_CUR_PATH, HISTORY_FILE)) as infile:
        history = json.load(infile)
    return history


def main_page():
    return ':-|'


def create_app():
    gpm = GetParamMiddleware(['sendkey', 'list_id'])
    routes = [('/', main_page, render_basic),
              ('/meta', MetaApplication()),
              ('/send', send, render_basic),
              ('/_dump_environ', lambda request: request.environ, render_basic),
              ('/view', get_language_list, render_basic),
              ('/view/<lang>/<format?>', get_rendered_issue, render_basic),
              ('/fetch/', fetch_rc, render_json),
              ('/fetch/<lang>', fetch_rc, render_json),
              ('/publish/bake/<lang>', render_and_save_all_formats, render_json),
              ('/static', StaticApplication(STATIC_PATH))]
    ashes_render = AshesRenderFactory(_CUR_PATH, filters={'ci': comma_int})
    resources = {'ashes_env': ashes_render.env}
    return Application(routes, resources, middlewares=[gpm])


def comma_int(val):
    try:
        return '{0:,}'.format(val)
    except ValueError:
        return val


if __name__ == '__main__':
    if ENABLE_FAKE:
        import fake
        fetch_rc = fake.fake_fetch_rc


wsgi_app = create_app()


if __name__ == '__main__':
    wsgi_app.serve(use_meta=False, use_static=False)
