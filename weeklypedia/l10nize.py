
import os
import re
import yaml
from argparse import ArgumentParser

CUR_PATH = os.path.dirname(os.path.abspath(__file__))

DEFAULT_TMPL_DIR = CUR_PATH + '/issue_templates'
BASE_TMPL_DIR = 'base'

L10N_SRC_MAP = {'template.txt': {'text_only': True},
                'template.html': {}}
# 'email.html': {}}


def get_argparser():
    prs = ArgumentParser()
    add_arg = prs.add_argument

    add_arg('--lang')
    add_arg('--tmpl-dir', default=DEFAULT_TMPL_DIR)
    return prs


class StringSubber(object):
    def __init__(self, strings_map):
        self.strings_map = strings_map
        self.subbable_re = re.compile(r'\$(\w+)\$')

    def get_subbed(self, text):
        self.unsubbed = []
        return self.subbable_re.sub(self._sub_one_match, text)

    def _sub_one_match(self, match):
        string_name = match.group(1)
        string_name_lower = string_name.lower()
        try:
            string = self.strings_map[string_name_lower]
        except KeyError:
            self.unsubbed.append(string_name)
            string = match.group(0)
        return string


def main():
    prs = get_argparser()
    args = prs.parse_args()
    lang = args.lang
    orig_tmpl_dir = args.tmpl_dir
    tmpl_dir = os.path.abspath(orig_tmpl_dir)

    strings_path = tmpl_dir + '/strings/' + lang + '_strings.yaml'
    try:
        strings_bytes = open(strings_path).read()
    except IOError as ioe:
        raise RuntimeError('expected strings file at %r (%r)'
                           % (strings_path, ioe))
    strings_map = yaml.load(strings_bytes)
    string_subber = StringSubber(strings_map)

    base_tmpl_base_path = tmpl_dir + '/' + BASE_TMPL_DIR + '/'
    for src_fn, options in L10N_SRC_MAP.items():
        base_tmpl_path = base_tmpl_base_path + src_fn
        base_bytes = open(base_tmpl_path).read()
        base_text = base_bytes.decode('utf-8')
        subbed_text = string_subber.get_subbed(base_text)
        subbed_bytes = subbed_text.encode('utf-8')

        if string_subber.unsubbed:
            print ('could not find substitutions for %r in %r'
                   % (string_subber.unsubbed, base_tmpl_path))

        target_path = tmpl_dir + '/' + lang + '_' + src_fn

        if '$' in subbed_text:
            print ('possible malformed substitution target, '
                   'check for occurrences of "$" in output: %r'
                   % target_path)

        with open(target_path, 'w') as f:  # TODO: atomic_save bolton
            f.write(subbed_bytes)
    return


if __name__ == '__main__':
    main()
