# -*- coding: utf-8 -*-

import os
import json
from os.path import dirname
from argparse import ArgumentParser
from clastic.render import AshesRenderFactory

from common import DEBUG, SUPPORTED_LANGS, SENDY_IDS

from web import (comma_int,
                 ISSUE_TEMPLATES_PATH)

from bake import (Issue,
                  bake_latest_issue,
                  render_and_save_archives,
                  render_index)


def send_issue(lang, is_dev=False):
    cur_issue = Issue(lang, include_dev=is_dev)
    list_id = SENDY_IDS[lang]
    result = cur_issue.send(list_id)
    return result


def get_argparser():
    desc = 'Bake and send Weeklypedia issues. (Please fetch first)'
    prs = ArgumentParser(description=desc)
    prs.add_argument('--lang', default=None)
    prs.add_argument('--bake_all', default=False, action='store_true')
    prs.add_argument('--nosend', default=False, action='store_true')
    prs.add_argument('--only_archives', default=False, action='store_true')
    prs.add_argument('--debug', default=DEBUG, action='store_true')
    prs.add_argument('--silent', default=False, action='store_true')
    return prs


if __name__ == '__main__':
    issue_ashes_env = AshesRenderFactory(ISSUE_TEMPLATES_PATH,
                                         filters={'ci': comma_int}).env
    parser = get_argparser()
    args = parser.parse_args()
    debug = args.debug

    if args.only_archives:
        if not args.silent:
            print '.. only rendering archives'
        render_and_save_archives(issue_ashes_env)
    elif args.bake_all:
        if not args.silent:
            print '.. rendering all issues'
        for lang in SUPPORTED_LANGS:
            if not args.silent:
                print '.. rendering latest for %s' % lang
            bake_latest_issue(issue_ashes_env, lang=lang, include_dev=debug)
    elif args.lang in SUPPORTED_LANGS:
        lang = args.lang
        if not args.silent:
            print '.. rendering latest for %s' % lang
        bake_latest_issue(issue_ashes_env, lang=lang, include_dev=debug)
        if args.nosend:
            if not args.silent:
                print '.. not sending'
        else:
            if not args.silent:
                print '.. sending latest for %s' % lang
            send_issue(lang, debug)
    else:
        print '!! language %s not supported' % args.lang
