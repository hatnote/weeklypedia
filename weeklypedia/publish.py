# -*- coding: utf-8 -*-

import os
import json
from os.path import dirname
from argparse import ArgumentParser
from clastic.render import AshesRenderFactory

from common import DEBUG, DEBUG_LIST_ID, SENDKEY

from web import (comma_int,
                 ISSUE_TEMPLATES_PATH)

from bake import (Issue,
                  bake_latest_issue,
                  render_index,
                  SUPPORTED_LANGS)

_CUR_PATH = dirname(os.path.abspath(__file__))

with open(os.path.join(_CUR_PATH, 'secrets.json')) as secrets_json:
    secrets = json.load(secrets_json)
    LIST_ID_MAP = secrets.get('list_ids')
    SENDY_ID_MAP = secrets.get('sendy_ids')


def send_issue(lang, mailer, is_dev=False):
    cur_issue = Issue(lang, include_dev=is_dev)

    if mailer == 'mailchimp':
        if is_dev:
            list_id = DEBUG_LIST_ID
        else:
            list_id = LIST_ID_MAP[lang]
        result = cur_issue.send(list_id, SENDKEY)
    elif mailer == 'sendy':
        list_id = SENDY_ID_MAP[lang]
        result = cur_issue.sendy_send(list_id)
    return result


def get_argparser():
    desc = 'Bake and send Weeklypedia issues. (Please fetch first)'
    prs = ArgumentParser(description=desc)
    prs.add_argument('--lang', default=None)
    prs.add_argument('--bake_all', default=False, action='store_true')
    prs.add_argument('--nosend', default=False, action='store_true')
    prs.add_argument('--debug', default=DEBUG, action='store_true')
    prs.add_argument('--mailer', default='mailchimp')
    return prs


if __name__ == '__main__':
    issue_ashes_env = AshesRenderFactory(ISSUE_TEMPLATES_PATH,
                                         filters={'ci': comma_int}).env
    parser = get_argparser()
    args = parser.parse_args()
    debug = args.debug
    if args.bake_all:
        for lang in SUPPORTED_LANGS:
            bake_latest_issue(issue_ashes_env, lang=lang, include_dev=debug)
    
    if args.lang in SUPPORTED_LANGS:
        lang = args.lang
        mailer = args.mailer
        print bake_latest_issue(issue_ashes_env, lang=lang, include_dev=debug)
        
        if args.nosend:
            print 'not sending...'
        else:
            print send_issue(lang, mailer, debug)
