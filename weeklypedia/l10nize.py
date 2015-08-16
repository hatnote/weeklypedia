
import os
import re
import yaml
from argparse import ArgumentParser

CUR_PATH = os.path.dirname(os.path.abspath(__file__))

DEFAULT_TMPL_DIR = CUR_PATH + '/issue_templates'
BASE_TMPL_DIR = 'base'


def get_argparser():
    prs = ArgumentParser()
    add_arg = prs.add_argument

    add_arg('--lang')
    add_arg('--tmpl-dir', default=DEFAULT_TMPL_DIR)
    return prs


UNTRANSLATED = []

# TODO: stringsubber class
def sub_strings(text, strings_map):
    def sub_one(match):
        string_name = match.group(1)
        string_name_lower = string_name.lower()
        try:
            string = strings_map[string_name_lower]
        except KeyError:
            UNTRANSLATED.append(string_name)
            string = match.group(0)
        return string

    ret = re.sub(r'\$(\w+)\$', sub_one, text)
    return ret


def main():
    prs = get_argparser()
    args = prs.parse_args()
    lang = args.lang
    tmpl_dir = args.tmpl_dir

    strings_path = tmpl_dir + '/strings/' + lang + '_strings.yaml'
    try:
        strings_bytes = open(strings_path).read()
    except IOError as ioe:
        raise RuntimeError('expected strings file at %r (%r)'
                           % (strings_path, ioe))
    strings_map = yaml.load(strings_bytes)

    base_tmpl = tmpl_dir + '/' + BASE_TMPL_DIR + '/' + 'template.txt'  # tmp
    print sub_strings(open(base_tmpl).read(), strings_map)

    return


if __name__ == '__main__':
    main()
