# -*- coding: utf-8 -*-

import re
import sys
from urllib import unquote
from argparse import ArgumentParser, FileType

from premailer import Premailer

_url_var_fix_re = re.compile(r'href="(?P<url>.+?)"')
_exclude_email_re = re.compile(r'<!-- email-exclude -->.*?'
                               '<!-- end-email-exclude -->',
                               re.DOTALL)


def get_argparser():
    prs = ArgumentParser()
    add = prs.add_argument

    add('in_file')
    add('out_file', nargs='?', type=FileType('w'), default=sys.stdout)
    add('--style', nargs='?')
    return prs


def fix_screwed_url(match):
    # premailer really takes a dump on templated hrefs
    unquoted_url = unquote(match.group('url'))
    unquoted_url = unquoted_url.replace('&amp;', '&')

    return ' href="' + unquoted_url + '" '


def main():
    parser = get_argparser()
    args = parser.parse_args()

    out_file = args.out_file
    html_text = open(args.in_file).read()

    p = Premailer(html=html_text,
                  external_styles=args.style)
    inlined_html = p.transform()
    inlined_html = _url_var_fix_re.sub(fix_screwed_url, inlined_html)
    inlined_html = _exclude_email_re.sub('', inlined_html)
    out_file.write(inlined_html)


if __name__ == '__main__':
    main()
