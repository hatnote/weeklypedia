# -*- coding: utf-8 -*-

import os
import json
from os.path import dirname
from argparse import ArgumentParser
from clastic.render import AshesRenderFactory

from common import DEBUG, DEBUG_LIST_ID

from web import (comma_int,
				 ISSUE_TEMPLATES_PATH)

from bake import (Issue,
                  bake_latest_issue,
                  SUPPORTED_LANGS)

_CUR_PATH = dirname(os.path.abspath(__file__))
IDS = json.load(open(os.path.join(_CUR_PATH, 'secrets.json'))).get('list_ids')


def send_issue(lang, send_key, is_dev=False):
	list_id = IDS.get(lang)
	if is_dev:
		list_id = DEBUG_LIST_ID
	cur_issue = Issue(lang, include_dev=is_dev)
	return cur_issue.send(list_id, send_key)
	print (list_id, send_key)

def get_argparser():
	desc = 'Bake and send Weeklypedia issues. (Please fetch first)'
	prs = ArgumentParser(description=desc)
	prs.add_argument('--lang', default=None)
	prs.add_argument('--key', default=None)
	prs.add_argument('--bake_all', default=False, action='store_true')
	prs.add_argument('--debug', default=DEBUG, action='store_true')
	return prs


if __name__ == '__main__':
	issue_ashes_env = AshesRenderFactory(ISSUE_TEMPLATES_PATH,
                                  		 filters={'ci': comma_int}).env
	parser = get_argparser()
	args = parser.parse_args()
	debug = args.debug
	send_key = args.key
	if args.bake_all:
		for lang in SUPPORTED_LANGS:
			bake_latest_issue(issue_ashes_env, lang=lang, include_dev=debug)
	if args.lang in SUPPORTED_LANGS:
		if not send_key:
			raise ValueError('Requires key')
		lang = args.lang
		print bake_latest_issue(issue_ashes_env, lang=lang, include_dev=debug)
		print send_issue(lang, send_key, debug)
