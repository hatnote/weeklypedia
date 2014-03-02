# -*- coding: utf-8 -*-

import os
import json
import urllib2
from datetime import datetime
from os.path import dirname, join as pjoin

import sys
sys.path.insert(0, os.path.expanduser('~/projects/clastic'))

from clastic import Application, render_json, render_basic, POST
from clastic.render import AshesRenderFactory
from clastic.meta import MetaApplication
from clastic.middleware.form import PostDataMiddleware
from clastic.static import StaticApplication

from mail import Mailinglist, KEY, TEST_LIST_ID

ENABLE_FAKE = True

_CUR_PATH = dirname(os.path.abspath(__file__))
ISSUE_TEMPLATES_PATH = pjoin(_CUR_PATH, 'issue_templates')
SITE_TEMPLATES_PATH = pjoin(_CUR_PATH, 'site_templates')

ARCHIVE_BASE_PATH = pjoin(dirname(_CUR_PATH), 'static', 'archive')
ARCHIVE_PATH_TMPL = '{lang_shortcode}/{date_str}{dev_flag}/weeklypedia_{date_str}{dev_flag}.{fmt}'
ARCHIVE_PATH_TMPL = pjoin(ARCHIVE_BASE_PATH, ARCHIVE_PATH_TMPL)

API_BASE_URL = 'http://tools.wmflabs.org/weeklypedia/fetch/'
LANG_MAP = json.load(open(pjoin(_CUR_PATH, 'language_codes.json')))
SUPPORTED_LANGS = ['en', 'de', 'fr', 'ko', 'et', 'sv', 'it', 'ca']
DEFAULT_LANGUAGE = 'en'

# lol at punctuation like Panic! at the Disco or Godspeed You! etc.
DEFAULT_INTRO = 'Hello there! Welcome to our weekly digest of Wikipedia activity.'

HISTORY_FILE = 'history.json'
SUBJECT_TMPL = 'Weeklypedia {lang_name} #{issue_number}'

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
    return past_issue_count


def get_next_issue_number(lang):
    return get_current_issue_number(lang=lang) + 1


def get_issue_data(lang=DEFAULT_LANGUAGE,
                   intro=DEFAULT_INTRO):
    basic_info = {'short_lang_name': lang,
                  'full_lang_name': LANG_MAP[lang]}
    basic_info['intro'] = intro
    basic_info['issue_number'] = get_current_issue_number(lang)
    basic_info['date'] = datetime.utcnow().strftime('%B %d, %Y')
    render_ctx = fetch_rc(lang=lang)
    render_ctx.update(basic_info)
    return render_ctx


def get_rendered_issue(issue_ashes_env, lang=DEFAULT_LANGUAGE, format=None):
    render_ctx = get_issue_data(lang)
    return _render_issue(render_ctx, issue_ashes_env, format=format)


def _render_issue(render_ctx, issue_ashes_env, intro=DEFAULT_INTRO, format=None):
    format = format or 'html'
    if format == 'json':
        return json.dumps(render_ctx, indent=2, sort_keys=True)

    if format == 'html':
        ret = issue_ashes_env.render('template.html', render_ctx)
    elif format == 'web':
        ret = issue_ashes_env.render('template_nostyles.html', render_ctx)
    else:
        ret = issue_ashes_env.render('template.txt', render_ctx)
    return ret.encode('utf-8')


def render_and_save_all_formats(issue_ashes_env,
                                lang=DEFAULT_LANGUAGE, 
                                intro=DEFAULT_INTRO,
                                is_dev=True):
    ret = []
    render_ctx = get_issue_data(lang=lang, intro=intro)
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
            rendered = _render_issue(render_ctx, issue_ashes_env, format=fmt)
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


def get_control_info():
    return {'supported_langs': SUPPORTED_LANGS,
            'test_list_id': TEST_LIST_ID}


def render_save_send(lang, 
                     list_id, 
                     intro, 
                     send_key, 
                     issue_ashes_env, 
                     is_dev=True):
    if is_dev:
        list_id = TEST_LIST_ID
    render_and_save_all_formats(issue_ashes_env,
                                lang=lang, 
                                intro=intro, 
                                is_dev=is_dev)
    return _send(lang, list_id, send_key, is_dev=is_dev)


def _send(lang, list_id, send_key, is_dev=False):
    lang_name = LANG_MAP[lang]
    issue_number = get_current_issue_number(lang)
    subject = SUBJECT_TMPL.format(lang_name=lang_name,
                                  issue_number=issue_number)
    mailinglist = Mailinglist(send_key + KEY)

    past_issue_paths = get_past_issue_paths(lang, include_dev=is_dev)
    issue_path = sorted(past_issue_paths)[-1]
    issue_fns = os.listdir(issue_path)
    issue_html_path = [fn for fn in issue_fns if fn.endswith('.html')][0]
    issue_text_path = [fn for fn in issue_fns if fn.endswith('.txt')][0]
    issue_html = open(pjoin(issue_path, issue_html_path)).read()
    issue_text = open(pjoin(issue_path, issue_text_path)).read()
    mailinglist.new_campaign(subject,
                             issue_html,
                             issue_text,
                             list_id=list_id)
    mailinglist.send_next_campaign()
    return 'Success: sent issue %s' % lang


def create_app():
    pdm = PostDataMiddleware(['lang', 'list_id', 'intro', 'send_key', 'is_dev'])
    ma = MetaApplication()
    routes = [('/', ma),
              #('/meta', ma),
              ('/_dump_environ', lambda request: request.environ, render_basic),
              ('/view', get_language_list, render_basic),
              ('/view/<lang>/<format?>', get_rendered_issue, render_basic),
              ('/fetch/', fetch_rc, render_json),
              ('/fetch/<lang>', fetch_rc, render_json),
              ('/publish/', get_control_info, 'controls.html'),
              ('/publish/bake/<lang>', render_and_save_all_formats, render_json),
              POST('/publish/send', render_save_send, render_basic,
                   middlewares=[pdm]),
              ('/static', StaticApplication(STATIC_PATH))]
    site_rf = AshesRenderFactory(SITE_TEMPLATES_PATH)
    issue_rf = AshesRenderFactory(ISSUE_TEMPLATES_PATH,
                                  filters={'ci': comma_int})
    resources = {'issue_ashes_env': issue_rf.env}
    return Application(routes, resources,
                       render_factory=site_rf)


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
