# -*- coding: utf-8 -*-
import os
import json
import urllib2
from datetime import datetime
from os.path import dirname, join as pjoin

DEBUG = True

API_BASE_URL = 'http://tools.wmflabs.org/weeklypedia/fetch/'
DEFAULT_LANGUAGE = 'ko'
_CUR_PATH = dirname(os.path.abspath(__file__))
LANG_MAP = json.load(open(pjoin(_CUR_PATH, 'language_codes.json')))

ARCHIVE_BASE_PATH = pjoin(dirname(_CUR_PATH), 'static', 'data')
ARCHIVE_PATH_TMPL = '{lang_shortcode}/{date_str}{dev_flag}/weeklypedia_{lang_shortcode}_{date_str}{dev_flag}.{fmt}'
ARCHIVE_PATH_TMPL = pjoin(ARCHIVE_BASE_PATH, ARCHIVE_PATH_TMPL)


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

def fetch_rc(lang=DEFAULT_LANGUAGE):
    if lang not in LANG_MAP:
        raise KeyError('unknown language code: %r' % lang)
    response = urllib2.urlopen(API_BASE_URL + lang)
    content = response.read()
    data = json.loads(content)
    basic_info = {'short_lang_name': lang,
                  'full_lang_name': LANG_MAP[lang]}
    display_date = datetime.utcnow().strftime('%B %d, %Y').replace(' 0', ' ')
    basic_info['date'] = display_date
    data.update(basic_info)
    return data

def render_rc(render_ctx):
    return json.dumps(render_ctx, indent=2, sort_keys=True)

def save(render_ctx, is_dev=DEBUG):
    fargs = {'fmt': 'json',
             'date_str': datetime.utcnow().strftime('%Y%m%d'),
             'lang_shortcode': render_ctx['short_lang_name'],
             'dev_flag': ''}
    if is_dev:
        fargs['dev_flag'] = '_dev'
    out_path = ARCHIVE_PATH_TMPL.format(**fargs)
    rendered = render_rc(render_ctx)
    try:
        out_file = open(out_path, 'w')
    except IOError:
        mkdir_p(os.path.dirname(out_path))
        out_file = open(out_path, 'w')
        # if exception, couldn't create file or parent directories
    with out_file:
        out_file.write(rendered)
    return (out_path, len(rendered))

def fetch_and_save(lang=DEFAULT_LANGUAGE, debug=DEBUG):
    fetch_resp = fetch_rc(lang)
    save_resp = save(fetch_resp, debug)
    return save_resp

def get_argparser():
    from argparse import ArgumentParser
    desc = "fetch json data from labs"
    prs = ArgumentParser(description=desc)
    prs.add_argument('--lang', default=DEFAULT_LANGUAGE)
    prs.add_argument('--debug', default=DEBUG, action='store_true')
    return prs

if __name__ == '__main__':
    parser = get_argparser()
    args = parser.parse_args()
    fetch_and_save(args.lang, args.debug)
    import pdb; pdb.set_trace();
