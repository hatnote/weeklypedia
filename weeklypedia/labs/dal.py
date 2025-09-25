# -*- coding: utf-8 -*-

import os
import time
from datetime import datetime, timedelta
import pymysql, pymysql.cursors

from wapiti import WapitiClient

from utils import translate_named_param_query


DB_CONFIG_PATH = os.path.expanduser('~/replica.my.cnf')
DATE_FORMAT = '%Y%m%d%H%M%S'


"""
TODO: something with protections?  (if we ever do this, remember to use rc_actor/actor, not rc_user, etc.)
   here's a query:
    select rc_cur_id, rc_title, actor.actor_name, rc_params
    from recentchanges
    LEFT JOIN actor on rc_actor=actor_id
    where
    rc_timestamp > 20140210215640
    and rc_namespace=0
    and rc_source='mw.log'
    and rc_log_type='protect'
    and rc_log_action='protect'
    and rc_cur_id > 0
    and rc_params LIKE "%indefinite%";

NOTES:

User counts generally don't include anonymous editors, but DO include
bot editors, due to the `COUNT(DISTINCT rc_user)`. `rc_user` is user
id, which is always 0 for unregistered users.

All counts are for the main namespace unless otherwise specified.
"""


class RecentChangesSummarizer(object):
    _ranked_activity_query = '''
            SELECT rc_cur_id AS page_id,
                   rc_title AS title,
                   COUNT(*) AS edits,
                   COUNT(DISTINCT rc_actor) AS users
            FROM recentchanges
            WHERE rc_namespace = %(namespace)s  
            AND rc_source = 'mw.edit'
            AND rc_timestamp > %(start_date)s
            GROUP BY page_id
            ORDER BY edits
            DESC
            LIMIT %(limit)s'''

    _ranked_activity_new_pages_query = '''
            SELECT rc_cur_id AS page_id,
                   rc_title AS title,
                   COUNT(*) AS edits,
                   COUNT(DISTINCT rc_actor) AS users
            FROM recentchanges
            WHERE rc_namespace = %(namespace)s
            AND rc_source = 'mw.edit'
            AND rc_timestamp > %(start_date)s
            AND rc_cur_id IN (SELECT rc_cur_id
                              FROM recentchanges
                              WHERE rc_timestamp > %(start_date)s
                              AND rc_namespace=%(namespace)s
                              AND rc_new=%(is_new)s)
            GROUP BY page_id
            ORDER BY edits
            DESC
            LIMIT %(limit)s'''

    _bounding_revids_query = '''
           SELECT rc_cur_id as page_id,
                  rc_title as title,
                  min(rc_last_oldid) as earliest_rev_id,
                  max(rc_this_oldid) as newest_rev_id
           FROM (SELECT rc_cur_id,
                        rc_title,
                        rc_this_oldid,
                        rc_last_oldid
                 FROM recentchanges
                 WHERE rc_namespace = %(namespace)s
                   AND rc_cur_id = %(page_id)s
                   AND rc_source = 'mw.edit'
                   AND rc_timestamp > %(start_date)s) PageRevs;'''

    _activity_query = '''
           SELECT COUNT(*) AS edits,
                  COUNT(DISTINCT rc_actor) AS users,
                  COUNT(DISTINCT rc_cur_id) AS titles
           FROM recentchanges
           WHERE rc_namespace = %(namespace)s
           AND rc_source = 'mw.edit'
           AND rc_timestamp > %(start_date)s;'''

    _anon_activity_query = '''
        SELECT COUNT(*) AS anon_edits,
           COUNT(DISTINCT actor.actor_name) AS anon_ip_count,
           COUNT(DISTINCT rc_cur_id) AS anon_titles
               FROM recentchanges
               LEFT JOIN actor on rc_actor=actor_id
               WHERE rc_namespace = %(namespace)s
               AND rc_source = 'mw.edit'
               AND rc_timestamp > %(start_date)s
               AND actor.actor_user IS NULL;'''

    _bot_activity_query = '''
           SELECT COUNT(*) AS bot_edits,
                  COUNT(DISTINCT rc_actor) AS bot_count,
                  COUNT(DISTINCT rc_cur_id) AS bot_titles
           FROM recentchanges
           WHERE rc_namespace = %(namespace)s
           AND rc_source = 'mw.edit'
           AND rc_timestamp > %(start_date)s
           AND rc_bot=1;'''


    def __init__(self, lang='en'):
        self.lang = lang
        self.db_title = lang + 'wiki_p'
        self.db_host = lang + 'wiki.labsdb'
        self.connection = pymysql.connect(db=self.db_title,
                                          host=self.db_host,
                                          read_default_file=DB_CONFIG_PATH,
                                          charset=None)

    def _get_cursor(self):
        return self.connection.cursor(pymysql.cursors.DictCursor)  # oursql.DictCursor)

    def _select(self, query, params=None):
        if params is None:
            params = []
        #elif isinstance(params, dict):
        #    old_query, old_params = query, params
        #    query, params = translate_named_param_query(query, params)
        cursor = self._get_cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    def _interval2timedelta(self, arg, default=None):
        default = default or timedelta(days=7)
        if arg is None:
            ret = default
        elif isinstance(arg, (int, float)):
            ret = timedelta(days=arg)
        elif isinstance(arg, timedelta):
            ret = arg
        else:
            ret = default
        return ret

    def get_activity_summary(self, namespace=None, interval=None,
                             end_date=None):
        namespace = namespace or 0
        interval = self._interval2timedelta(interval)

        end_date = end_date or datetime.utcnow()
        start_date = end_date - interval
        start_date_str = start_date.strftime(DATE_FORMAT)
        params = {'namespace': namespace, 'start_date': start_date_str}
        ret = self._select(self._activity_query, params)[0]
        anon_result = self._select(self._anon_activity_query, params)[0]
        bot_result = self._select(self._bot_activity_query, params)[0]
        totals = {'total_users': ret['users'] + anon_result['anon_ip_count']}

        ret.update(anon_result)
        ret.update(bot_result)
        ret.update(totals)
        return ret

    def get_ranked_activity(self, limit=None, namespace=None, interval=None,
                            end_date=None):
        limit = limit or 20
        namespace = namespace or 0  # support multiple? (for talk pages)
        interval = self._interval2timedelta(interval)
        end_date = end_date or datetime.utcnow()
        start_date = end_date - interval
        start_date_str = start_date.strftime(DATE_FORMAT)
        params = {'namespace': namespace,
                  'start_date': start_date_str,
                  'limit': limit}

        results = self._select(self._ranked_activity_query, params)
        for page in results:
            page['title'] = page['title'].decode('utf-8')
            page['title_s'] = page['title'].replace('_', ' ')
            page['rev_ids'] = self.get_bounding_rev_ids(page['page_id'],
                                                        namespace,
                                                        start_date_str)
        return results

    def get_ranked_activity_new_pages(self, limit=None, namespace=None,
                                      interval=None, end_date=None):
        limit = limit or 20
        namespace = namespace or 0
        interval = self._interval2timedelta(interval)
        end_date = end_date or datetime.utcnow()
        start_date = end_date - interval
        start_date_str = start_date.strftime(DATE_FORMAT)
        params = {'namespace': namespace,
                  'start_date': start_date_str,
                  'limit': limit,
                  'is_new': True}  # is_new hmmm

        results = self._select(self._ranked_activity_new_pages_query, params)
        # TODO: can eliminate the rev_ids part by getting newest
        # rev_id in the query
        for page in results:
            page['title'] = page['title'].decode('utf-8')
            page['title_s'] = page['title'].replace('_', ' ')
            page['rev_ids'] = self.get_bounding_rev_ids(page['page_id'],
                                                        namespace,
                                                        start_date_str)
        return results

    def get_mainspace_activity(self, limit=None, interval=None):
        return self.get_ranked_activity(limit=limit,
                                        interval=interval,
                                        namespace=0)

    def get_talkspace_activity(self, limit=None, interval=None):
        return self.get_ranked_activity(limit=limit,
                                        interval=interval,
                                        namespace=1)

    def get_bounding_rev_ids(self, page_id, namespace, start_date_str):
        params = {'page_id': page_id,
                  'namespace': namespace,
                  'start_date': start_date_str}
        res = self._select(self._bounding_revids_query, params)[0]
        return {'old': res['earliest_rev_id'], 'new': res['newest_rev_id']}

    def get_full_summary(self, interval=None, main_limit=20, talk_limit=5,
                         new_limit=10, with_extracts=False):
        ret = {}
        interval = self._interval2timedelta(interval)
        fi = ret['fetch_info'] = {}
        start_time = time.time()
        current_dt = datetime.utcnow()
        start_dt = current_dt - interval
        fi['start_date'] = start_dt.isoformat()
        fi['end_date'] = current_dt.isoformat()
        ret['stats'] = self.get_activity_summary(interval=interval)
        ret['talk_stats'] = self.get_activity_summary(interval=interval,
                                                      namespace=1)
        ret['mainspace'] = self.get_mainspace_activity(interval=interval,
                                                       limit=main_limit)
        ret['talkspace'] = self.get_talkspace_activity(interval=interval,
                                                       limit=talk_limit)
        granp = self.get_ranked_activity_new_pages
        ret['new_articles'] = granp(interval=interval, limit=new_limit)
        fi['lang'] = self.lang
        fi['duration'] = time.time() - start_time
        #if with_extracts:
        #    titles = [i['title'] for i in ret['mainspace']]
        #    ret['extracts'] = extracts(self.lang, titles, 3)
        return ret


def extracts(lang, titles, limit):
    wc = WapitiClient('stephen.laporte@gmail.com',
                      api_url='https://' + lang + '.wikipedia.org/w/api.php')
    if limit > len(titles):
        limit = len(titles)
    ret = {}
    for i in range(limit):
        title = titles[i]
        res = wc.get_page_extract(title)
        if res:
            ret[title] = {'title': title, 'extract': res[0].extract}
    return ret


if __name__ == '__main__':
    import pdb;pdb.set_trace()  # do your debugging here
