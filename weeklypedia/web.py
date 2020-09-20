# -*- coding: utf-8 -*-

import os
from os.path import dirname, join as pjoin

import sys
sys.path.insert(0, os.path.expanduser('~/projects/clastic'))

from clastic import Application, render_json, render_basic, POST
from clastic.render import AshesRenderFactory
from clastic.meta import MetaApplication
from clastic.middleware.form import PostDataMiddleware
from clastic.static import StaticApplication

from fetch import fetch_rc
from bake import (Issue,
                  render_issue,
                  prep_latest_issue,
                  bake_latest_issue,
                  render_and_save_archives,
                  render_archive,
                  SUPPORTED_LANGS,
                  DEFAULT_LANGUAGE,
                  LANG_MAP)

_CUR_PATH = dirname(os.path.abspath(__file__))
ISSUE_TEMPLATES_PATH = pjoin(_CUR_PATH, 'issue_templates')
SITE_TEMPLATES_PATH = pjoin(_CUR_PATH, 'site_templates')
STATIC_PATH = os.path.abspath(_CUR_PATH + '/../static/')


def get_language_list():
    return sorted(LANG_MAP.keys())


def get_rendered_issue(issue_ashes_env, lang=DEFAULT_LANGUAGE, format=None):
    issue_data = prep_latest_issue(lang)
    return render_issue(issue_data, issue_ashes_env, format=format)


def get_archive(issue_ashes_env, lang):
    return render_archive(issue_ashes_env, lang)


def get_control_info():
    return {'supported_langs': SUPPORTED_LANGS,
            'test_list_id': TEST_LIST_ID}


def send_issue(lang,
               list_id,
               subject,
               intro,
               send_key,
               issue_ashes_env,
               is_dev=True):
    if is_dev:
        list_id = TEST_LIST_ID
    if subject == '':
        subject = False
    cur_issue = Issue(lang, custom_subject=subject, include_dev=is_dev)
    return cur_issue.send(list_id, send_key)


def create_app():
    pdm = PostDataMiddleware(['lang', 'list_id', 'subject', 'intro', 'send_key', 'is_dev'])
    ma = MetaApplication()
    routes = [('/', ma),
              #('/meta', ma),
              ('/_dump_environ', lambda request: request.environ, render_basic),
              ('/bake', bake_latest_issue, render_basic),
              ('/archive/<lang>', get_archive, render_basic),
              ('/build_archives', render_and_save_archives, render_basic),
              ('/view', get_language_list, render_basic),
              ('/view/<lang>/<format?>', get_rendered_issue, render_basic),
              ('/fetch/', fetch_rc, render_json),
              ('/fetch/<lang>', fetch_rc, render_json),
              ('/publish/', get_control_info, 'controls.html'),
              POST('/publish/send', send_issue, render_basic,
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

wsgi_app = create_app()


if __name__ == '__main__':
    wsgi_app.serve(use_meta=False, use_static=False)
