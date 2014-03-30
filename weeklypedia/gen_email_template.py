# -*- coding: utf-8 -*-

import re
import sys
from argparse import ArgumentParser, FileType

from premailer import Premailer

_url_var_fix_re = re.compile("%7B(?P<var_name>\w+)%7D")
# TODO: get rid of script tags


def get_argparser():
    prs = ArgumentParser()
    add = prs.add_argument

    add('in_file')
    add('out_file', nargs='?', type=FileType('w'), default=sys.stdout)
    return prs


def get_email_template(base_template_text):
    pass


def main():
    parser = get_argparser()
    args = parser.parse_args()

    out_file = args.out_file
    html_text = open(args.in_file).read()

    p = Premailer(html=html_text)
    inlined_html = p.transform()
    inlined_html = _url_var_fix_re.sub('{\g<var_name>}', inlined_html)
    out_file.write(inlined_html)


if __name__ == '__main__':
    main()
