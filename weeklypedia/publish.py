# -*- coding: utf-8 -*-

import os
import json
from os.path import dirname
from argparse import ArgumentParser
from clastic.render import AshesRenderFactory

from common import DEBUG, DEBUG_ID, SUPPORTED_LANGS, SENDY_IDS

from web import (comma_int,
                 ISSUE_TEMPLATES_PATH)

from bake import (Issue,
                  bake_latest_issue,
                  render_and_save_archives,
                  render_index)


def send_issue(lang, custom_issue=None, debug=False, silent=True, nosend=True):
    if debug:
        list_id = DEBUG_ID
        if not silent:
            print '.. sending to debug list (%s)' % list_id
    else:
        list_id = SENDY_IDS[lang]
    cur_issue = Issue(lang, custom_issue=custom_issue, include_dev=debug)
    if not nosend:
        if not silent:
            print '.. sending to %s list (%s)' % (lang, list_id)
        return cur_issue.send(list_id)
    if not silent:
        print '.. not sending "{subject}" to list id {list_id}'.format(list_id=list_id, subject=cur_issue.subject)
    return


def get_argparser():
    desc = 'Bake and send Weeklypedia issues. (Please fetch first)'
    prs = ArgumentParser(description=desc)
    prs.add_argument('--lang', default=None)
    prs.add_argument('--issue', default=None)
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
        if not args.issue:
            bake_latest_issue(issue_ashes_env, lang=lang, include_dev=debug)
        send_issue(lang, custom_issue=args.issue, debug=debug, silent=args.silent, nosend=args.nosend)
    else:
        print '!! language %s not supported' % args.lang
