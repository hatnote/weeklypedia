# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime, timedelta
from os.path import dirname, join as pjoin

from babel.dates import format_date
from dateutil.parser import parse as parse_date
from ashes import TemplateNotFound

from mail import Mailinglist, KEY
from fetch import get_latest_data_path

from common import (DATA_BASE_PATH,
                    DEFAULT_LANGUAGE,
                    DEFAULT_INTRO,
                    DEBUG,
                    CUSTOM_INTRO_PATH,
                    LANG_MAP,
                    LOCAL_LANG_MAP,
                    SUBJECT_TMPL,
                    SUPPORTED_LANGS,
                    SIGNUP_MAP,
                    mkdir_p)

_CUR_PATH = dirname(os.path.abspath(__file__))

INDEX_PATH = pjoin(dirname(_CUR_PATH), 'static', 'index.html')
ARCHIVE_BASE_PATH = pjoin(dirname(_CUR_PATH), 'static', 'archive')
ARCHIVE_PATH_TMPL = '{lang_shortcode}/{date_str}{dev_flag}/weeklypedia_{date_str}{dev_flag}{email_flag}.{fmt}'
ARCHIVE_PATH_HTML_TMPL = '{date_str}/{file_name}'
ARCHIVE_TITLE_TMPL = 'weeklypedia_{date_str}.html'
ARCHIVE_DATA_TITLE_TMPL = 'weeklypedia_{date_str}.json'
ARCHIVE_INDEX_PATH_TMPL = ARCHIVE_BASE_PATH + '/{lang_shortcode}/index.html'
ARCHIVE_PATH_TMPL = pjoin(ARCHIVE_BASE_PATH, ARCHIVE_PATH_TMPL)


class Issue(object):
    def __init__(self,
                 lang,
                 custom_issue=None,
                 custom_subject=None,
                 include_dev=DEBUG):
        self.lang = lang
        self.full_lang_name = LANG_MAP[lang]
        past_issue_paths = get_past_issue_paths(lang, include_dev=include_dev)
        if custom_issue:
            issue_path = [path for path in past_issue_paths
                          if custom_issue in path][0]
            # what if there is a _dev issue?
        else:
            issue_path = sorted(past_issue_paths)[-1]
        self.fns = os.listdir(issue_path)
        email_html_path = [fn for fn in self.fns if fn.endswith('_e.html')][0]
        text_path = [fn for fn in self.fns if fn.endswith('.txt')][0]
        json_path = [fn for fn in self.fns if fn.endswith('.json')][0]
        info = json.load(open(pjoin(issue_path, json_path)))
        self.email_html_path = pjoin(issue_path, email_html_path)
        self.text_path = pjoin(issue_path, text_path)
        self.number = info['issue_number']
        self.subject = custom_subject
        if not custom_subject:
            self.subject = SUBJECT_TMPL.format(lang_name=self.full_lang_name,
                                               issue_number=self.number)

    def read_html(self):
        return open(self.email_html_path).read()

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
    past_issue_fns = sorted(os.listdir(lang_path))
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


def get_issue_data(lang, date):
    arch_data_title = ARCHIVE_DATA_TITLE_TMPL.format(date_str=date)
    archive_data_path = ARCHIVE_PATH_HTML_TMPL.format(lang_shortcode=lang,
                                                      date_str=date,
                                                      file_name=arch_data_title)
    archive_file = os.path.join(ARCHIVE_BASE_PATH, lang, archive_data_path)
    issue_data = json.load(open(archive_file))
    return issue_data


def prep_latest_issue(lang=DEFAULT_LANGUAGE,
                      intro=None,
                      include_dev=DEBUG):
    if intro is None:
        try:
            intro = open(CUSTOM_INTRO_PATH).read()
            intro = intro.decode('utf-8').strip()
        except:
            print 'got exception reading custom intro, skipping'
            intro = None
        if not intro:
            intro = DEFAULT_INTRO
    issue_info = {'intro': intro,
                  'issue_number': get_next_issue_number(lang)}
    latest_issue_p = get_latest_data_path(lang, include_dev=include_dev)
    issue_data = json.load(open(latest_issue_p))
    issue_data.update(issue_info)
    return issue_data


def prep_preview(lang=DEFAULT_LANGUAGE, include_dev=DEBUG):
    most_recent = get_past_issue_paths(lang)[-1]
    date = most_recent.rpartition('/')[2]
    issue_title = ARCHIVE_TITLE_TMPL.format(date_str=date)
    issue_path = ARCHIVE_PATH_HTML_TMPL.format(lang_shortcode=lang,
                                               date_str=date,
                                               file_name=issue_title)
    preview_data = get_issue_data(lang, date)
    stats = preview_data['stats']
    preview_data['mainspace'] = preview_data['mainspace'][:5]
    preview_data['stats']['all_users'] = stats['users'] + stats['anon_ip_count']
    preview_data['path'] = 'archive/%s/%s' % (lang, issue_path)
    return preview_data


def bake_latest_issue(issue_ashes_env,
                      lang=DEFAULT_LANGUAGE,
                      intro=None,
                      include_dev=DEBUG):
    ret = {'issues': []}
    issue_data = prep_latest_issue(lang, intro, include_dev)
    issue_data['signup_url'] = SIGNUP_MAP[lang]
    localize_data(issue_data)
    # this fmt is used to generate the path, as well
    for fmt in ('html', 'json', 'txt', 'email'):
        rendered = render_issue(issue_data, issue_ashes_env, format=fmt)
        issue = save_issue(fmt, rendered, lang, is_dev=include_dev)
        ret['issues'].append(issue)
    ret['archives'] = render_and_save_archives(issue_ashes_env)
    return ret


def lang_fallback_render(env, lang, tmpl_name, ctx, fallback_lang='en'):
    try:
        return env.render(lang + '_' + tmpl_name, ctx)
    except TemplateNotFound:
        return env.render(fallback_lang + '_' + tmpl_name, ctx)


def render_issue(render_ctx, issue_ashes_env,
                 intro=DEFAULT_INTRO, format=None):
    format = format or 'html'
    if format == 'json':
        return json.dumps(render_ctx, indent=2, sort_keys=True)
    lang = render_ctx['short_lang_name']
    env, ctx = issue_ashes_env, render_ctx
    if format == 'html':
        ret = lang_fallback_render(env, lang, 'archive.html', ctx)
    elif format == 'email':
        ret = lang_fallback_render(env, lang, 'email.html', ctx)
    elif format == 'txt':
        ret = lang_fallback_render(env, lang, 'email.txt', ctx)
    else:
        raise ValueError('unrecognized render format: %r' % format)
    return ret.encode('utf-8')


def save_issue(fmt, rendered, lang, is_dev=DEBUG, date=False):
    fargs = {'fmt': fmt,
             'date_str': datetime.utcnow().strftime('%Y%m%d'),
             'lang_shortcode': lang,
             'dev_flag': '',
             'email_flag': ''}
    if date:
        fargs['date_str'] = date
    if is_dev:
        fargs['dev_flag'] = '_dev'
    if fmt == 'email':
        fargs['email_flag'] = '_e'
        fargs['fmt'] = 'html'
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
    ret['signup_url'] = SIGNUP_MAP[lang]
    return issue_ashes_env.render('template_archive_index.html', ret)


def render_index(issue_ashes_env):
    next_date = (datetime.now() + timedelta(days=7)).strftime('%B %d, %Y')
    context = {'next_date': next_date,
               'volume': get_next_issue_number(DEFAULT_LANGUAGE)}
    preview = prep_preview(DEFAULT_LANGUAGE)
    context.update(preview)
    rendered_index = issue_ashes_env.render('template_index.html', context)
    rendered_index = rendered_index.encode('utf-8')
    with open(INDEX_PATH, 'w') as out_file:
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


def localize_data(issue_data, lang_code):
    "To be called right before rendering html, etc."

    lang_code = issue_data['short_lang_name']
    eng_lang = LANG_MAP[lang_code]
    full_lang_name = LOCAL_LANG_MAP.get(lang_code, eng_lang)
    issue_data['local'] = {'full_lang_name': full_lang_name}

    # add local_date
    issue_date_str = issue_data['date']
    issue_date = parse_date(issue_date_str)
    local_date = format_date(issue_date, format='long', locale=lang_code)
    issue_data['local']['date'] = local_date

    return
