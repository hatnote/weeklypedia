# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime, timedelta
from os.path import dirname, join as pjoin

from mail import Mailinglist, KEY
from fetch import get_latest_data_path

DEFAULT_LANGUAGE = 'en'
SUPPORTED_LANGS = ['en', 'de', 'fr', 'ko', 'et', 'sv', 'it', 'ca']
# lol at punctuation like Panic! at the Disco or Godspeed You! etc.
DEFAULT_INTRO = 'Hello there! Welcome to our weekly digest of Wikipedia activity.'

_CUR_PATH = dirname(os.path.abspath(__file__))
LANG_MAP = json.load(open(pjoin(_CUR_PATH, 'language_codes.json')))
SUBJECT_TMPL = 'Weeklypedia {lang_name} #{issue_number}'

INDEX_PATH = pjoin(dirname(_CUR_PATH), 'static', 'index.html')
ARCHIVE_BASE_PATH = pjoin(dirname(_CUR_PATH), 'static', 'archive')
ARCHIVE_PATH_TMPL = '{lang_shortcode}/{date_str}{dev_flag}/weeklypedia_{date_str}{dev_flag}.{fmt}'
ARCHIVE_PATH_HTML_TMPL = '{date_str}/{file_name}'
ARCHIVE_TITLE_TMPL = 'weeklypedia_{date_str}.html'
ARCHIVE_INDEX_PATH_TMPL = ARCHIVE_BASE_PATH + '/{lang_shortcode}/index.html'
ARCHIVE_PATH_TMPL = pjoin(ARCHIVE_BASE_PATH, ARCHIVE_PATH_TMPL)


class Issue(object):
    def __init__(self, 
                 lang, 
                 custom_issue=None, 
                 custom_subject=None, 
                 include_dev=True):
        self.lang = lang
        self.full_lang_name = LANG_MAP[lang]
        past_issue_paths = get_past_issue_paths(lang, include_dev=include_dev)
        if custom_issue:
            issue_path = [path for path in past_issue_paths \
                          if custom_issue in path][0]
            # what if there is a _dev issue?
        else:
            issue_path = sorted(past_issue_paths)[-1]
        self.fns = os.listdir(issue_path)
        html_path = [fn for fn in self.fns if fn.endswith('.html')][0]
        text_path = [fn for fn in self.fns if fn.endswith('.txt')][0]
        json_path = [fn for fn in self.fns if fn.endswith('.json')][0]
        info = json.load(open(pjoin(issue_path, json_path)))
        self.html_path = pjoin(issue_path, html_path)
        self.text_path = pjoin(issue_path, text_path)
        self.number = info['issue_number']
        self.subject = custom_subject
        if not custom_subject:
            self.subject = SUBJECT_TMPL.format(lang_name=self.full_lang_name,
                                               issue_number=self.number)


    def read_html(self):
        return open(self.html_path).read()


    def read_text(self):
        return open(self.text_path).read()


    def send(self, list_id, send_key):
        mailinglist = Mailinglist(send_key + KEY)
        mailinglist.new_campaign(self.subject,
                                 self.read_html(),
                                 self.read_text(),
                                 list_id=list_id)
        mailinglist.send_next_campaign()
        return 'Success: sent issue %s' % self.lang


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


def prep_latest_issue(lang=DEFAULT_LANGUAGE,
                      intro=DEFAULT_INTRO,
                      format=None,
                      include_dev=True):
    issue_info = {'intro': intro,
                  'issue_number': get_next_issue_number(lang)}
    latest_issue_p = get_latest_data_path(lang, include_dev=include_dev)
    issue_data = json.load(open(latest_issue_p))
    issue_data.update(issue_info)
    return issue_data


def bake_latest_issue(issue_ashes_env,
                      lang=DEFAULT_LANGUAGE,
                      intro=DEFAULT_INTRO,
                      include_dev=True):
    ret = {'issues': []}
    issue_data = prep_latest_issue(lang, intro, include_dev)
    for fmt in ('html', 'json', 'txt'):
        rendered = render_issue(issue_data, issue_ashes_env, format=fmt)
        issue = save_issue(fmt, rendered, lang, issue_ashes_env)
        ret['issues'].append(issue)
    ret['archives'] = render_and_save_archives(issue_ashes_env)
    return ret


def render_issue(render_ctx, issue_ashes_env, intro=DEFAULT_INTRO, format=None):
    format = format or 'html'
    if format == 'json':
        return json.dumps(render_ctx, indent=2, sort_keys=True)

    if format == 'html':
        ret = issue_ashes_env.render('template.html', render_ctx)
    elif format == 'web':
        ret = issue_ashes_env.render('template_archive.html', render_ctx)
    else:
        ret = issue_ashes_env.render('template.txt', render_ctx)
    return ret.encode('utf-8')


def save_issue(fmt, rendered, lang, is_dev):
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
        out_file.write(rendered)
    return (out_path, len(rendered))


def render_archive(issue_ashes_env, lang):
    ret = {}
    ret['issues'] = []
    paths = get_past_issue_paths(lang)
    for archive in paths:
        date = archive.rpartition('/')[2]
        arch_title = ARCHIVE_TITLE_TMPL.format(date_str=date)
        archive_path = ARCHIVE_PATH_HTML_TMPL.format(lang_shortcode=lang,
                                                     date_str=date,
                                                     file_name=arch_title)
        display_date = datetime.strptime(date, '%Y%m%d').strftime('%B %d, %Y')
        display_date = display_date.replace(' 0', ' ')
        ret['issues'].insert(0, {'path': archive_path,
                                 'date': display_date})
    ret['lang'] = LANG_MAP[lang]
    return issue_ashes_env.render('template_archive_index.html', ret)


def render_index(issue_ashes_env):
    next_date = (datetime.now() + timedelta(days=7)).strftime('%B %d, %Y')
    context = {'next_date': next_date,
               'volume': get_next_issue_number(DEFAULT_LANGUAGE)}
    rendered_index = issue_ashes_env.render('template_index.html', context)
    out_file = open(INDEX_PATH, 'w')
    with out_file:
        out_file.write(rendered_index)
    return (INDEX_PATH, len(rendered_index))


def render_and_save_archives(issue_ashes_env):
    ret = []
    for lang in SUPPORTED_LANGS:
        out_path = ARCHIVE_INDEX_PATH_TMPL.format(lang_shortcode=lang)
        out_file = open(out_path, 'w')
        with out_file:
            rendered = render_archive(issue_ashes_env, lang)
            out_file.write(rendered)
        ret.append((out_path, len(rendered)))
    ret.append(render_index(issue_ashes_env))
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
