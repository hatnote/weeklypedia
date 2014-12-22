# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime, timedelta
from os.path import dirname, join as pjoin

from argparse import ArgumentParser

from clastic.render import AshesRenderFactory

from web import (comma_int,
                 ISSUE_TEMPLATES_PATH)

from common import (SUPPORTED_LANGS, SIGNUP_MAP)

from bake import (get_past_issue_paths,
                  get_issue_data,
                  render_issue,
                  render_and_save_archives,
                  render_index,
                  save_issue)


def get_argparser():
    desc = 'Out with the old template, in with the new.'
    prs = ArgumentParser(description=desc)
    prs.add_argument('--lang', default=None)
    return prs

def reprocess(render_context, lang):
    ret = []
    render_index(render_context)
    render_and_save_archives(render_context)
    all_issue_paths = get_past_issue_paths(lang)
    for issue_path in all_issue_paths:
        issue_date = issue_path.rpartition('/')[2]
        print issue_date
        issue_data = get_issue_data(lang, issue_date)
        issue_data['signup_url'] = SIGNUP_MAP[lang]
        if not issue_data.get('issue_number'):
            print 'no data for %s' % issue_date
            continue
        fmt = 'html'
        issue_rerendered = render_issue(issue_data, 
                                        render_context, 
                                        format=fmt)
        final_issue = save_issue(fmt, 
                                 issue_rerendered, 
                                 lang,
                                 is_dev=False,
                                 date=issue_date)
        ret.append(final_issue)
    return ret



if __name__ == '__main__':
    issue_ashes_env = AshesRenderFactory(ISSUE_TEMPLATES_PATH,
                                         filters={'ci': comma_int}).env
    parser = get_argparser()
    args = parser.parse_args()

    if not args.lang:
        for lang in SUPPORTED_LANGS:
            print 'Rerendering %s' % lang
            reprocess(issue_ashes_env, lang)
        print 'complete'
    
    if args.lang in SUPPORTED_LANGS:
        lang = args.lang
        reprocess(issue_ashes_env, lang)
        print 'Rerendered %s' % lang
