# -*- coding: utf-8 -*-

import os
import json
import urllib2
from datetime import datetime


from common import LANG_MAP, DEBUG, DEFAULT_LANGUAGE, API_BASE_URL
from common import DATA_BASE_PATH, DATA_PATH_TMPL, mkdir_p


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
    fargs = {'date_str': datetime.utcnow().strftime('%Y%m%d'),
             'lang_shortcode': render_ctx['short_lang_name'],
             'dev_flag': ''}
    if is_dev:
        fargs['dev_flag'] = '_dev'
    out_path = DATA_PATH_TMPL.format(**fargs)
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


def get_past_data_paths(lang, include_dev=DEBUG):
    ret = []
    lang_path = os.path.join(DATA_BASE_PATH, lang)
    if not os.path.isdir(lang_path):
        return ret
    past_issue_fns = os.listdir(lang_path)
    for fn in past_issue_fns:
        if not include_dev and fn.endswith('_dev'):
            continue
        full_path = os.path.join(lang_path, fn)
        if os.path.isdir(full_path):
            ret.append(full_path)
    return ret


def get_latest_data_path(lang, include_dev=DEBUG):
    past_issue_paths = get_past_data_paths(lang, include_dev=include_dev)
    issue_path = sorted(past_issue_paths)[-1]
    latest_issue_fn = sorted(os.listdir(issue_path))[-1]
    return os.path.join(issue_path, latest_issue_fn)



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
    if args.debug:
        print get_latest_data_path(args.lang, include_dev=True)
        import pdb; pdb.set_trace();
