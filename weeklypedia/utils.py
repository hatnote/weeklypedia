# -*- coding: utf-8 -*-

import re


named_param_re = re.compile("(\:\w+)")


def translate_named_param_query(query, param_dict):
    match_iter = named_param_re.finditer(query)
    new_query_parts = []
    arg_list = []
    prev_end = 0
    for match in match_iter:
        start, end = match.start(), match.end()
        if prev_end < start:
            new_query_parts.append(query[prev_end:start])
        prev_end = end
        arg_list.append(param_dict[match.group(0)[1:]])
        new_query_parts.append('?')
    tail = query[prev_end:]
    if tail:
        new_query_parts.append(tail)
    return ''.join(new_query_parts), arg_list
