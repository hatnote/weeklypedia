import os
from datetime import datetime, timedelta
import oursql

from wapiti import WapitiClient

from utils import translate_named_param_query


DB_CONFIG_PATH = os.path.expanduser('~/replica.my.cnf')
DATE_FORMAT = '%Y%m%d%H%M%S'


def parse_date_str(date_str):
    return datetime.strptime(date_str, DATE_FORMAT)


def predate(date, days):
    pdate = date - timedelta(days)
    return pdate.strftime(DATE_FORMAT)


class RecentChangesSummarizer(object):
    _ranked_activity_query = '''
            SELECT rc_cur_id AS page_id,
                   rc_title AS title,
                   COUNT(*) AS edits,
                   COUNT(DISTINCT rc_user) AS users
            FROM recentchanges
            WHERE rc_namespace = :namespace
            AND rc_type = 0
            AND rc_timestamp > :start_date
            GROUP BY page_id
            ORDER BY edits
            DESC
            LIMIT :limit'''

    _ranked_activity_new_pages_query = '''
            SELECT rc_cur_id AS page_id,
                   rc_title AS title,
                   COUNT(*) AS edits,
                   COUNT(DISTINCT rc_user) AS users
            FROM recentchanges
            WHERE rc_namespace = :namespace
            AND rc_type = 0
            AND rc_timestamp > :start_date
            AND page_id IN (SELECT rc_cur_id
                            FROM recentchanges
                            WHERE rc_timestamp > :start_date
                            AND rc_namespace=:namespace
                            AND rc_new=:is_new)
            GROUP BY page_id
            ORDER BY edits
            DESC
            LIMIT :limit'''

    _bounding_revids_query = '''
           SELECT rc_title as title,
                  min(rc_last_oldid) as earliest_rev_id,
                  max(rc_this_oldid) as newest_rev_id
           FROM (SELECT rc_title,
                        rc_this_oldid,
                        rc_last_oldid
                 FROM recentchanges
                 WHERE rc_namespace = :namespace
                   AND rc_cur_id = :page_id
                   AND rc_timestamp > :start_date) PageRevs;'''

    _activity_query = '''
           SELECT COUNT(*) AS edits,
                  COUNT(DISTINCT rc_title) AS titles,
                  COUNT(DISTINCT rc_user) AS users
           FROM recentchanges
           WHERE rc_namespace = :namespace
           AND rc_type = 0
           AND rc_timestamp > :start_date;'''

    def __init__(self, lang='en'):
        self.lang = lang
        self.db_title = lang + 'wiki_p'
        self.db_host = lang + 'wiki.labsdb'
        self.connection = oursql.connect(db=self.db_title,
                                         host=self.db_host,
                                         read_default_file=DB_CONFIG_PATH,
                                         charset=None)

    def _get_cursor(self):
        return self.connection.cursor(oursql.DictCursor)

    def _select(self, query, params=None):
        if params is None:
            params = []
        elif isinstance(params, dict):
            old_query, old_params = query, params
            query, params = translate_named_param_query(query, params)
        cursor = self._get_cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    def get_activity_summary(self, interval=None, namespace=None,
                             end_date=None):
        if interval is None:
            interval = timedelta(days=7)
        namespace = namespace or 0
        end_date = end_date or datetime.now()
        start_date = end_date - interval
        start_date_str = start_date.strftime(DATE_FORMAT)
        params = {'namespace': namespace, 'start_date': start_date_str}
        results = self._select(self._activity_query, params)
        return results

    def get_ranked_activity(self, limit=20, interval=None, namespace=None,
                            end_date=None):
        if interval is None:
            interval = timedelta(days=7)
        namespace = namespace or 0  # support multiple? (for talk pages)

        end_date = end_date or datetime.now()
        start_date = end_date - interval
        start_date_str = start_date.strftime(DATE_FORMAT)
        params = {'namespace': namespace,
                  'start_date': start_date_str,
                  'limit': limit}
        results = self._select(self._ranked_activity_query, params)
        for edit in results:
            edit['title'] = edit['title'].decode('utf-8')
            edit['title_s'] = edit['title'].replace('_', ' ')
        return results

    def get_ranked_activity_new_pages(self):
        query = self._ranked_activity_new_pages_query

    def get_mainspace_activity(self, limit=None, interval=None):
        return self.get_ranked_activity(limit=limit,
                                        interval=interval,
                                        namespace=0)

    def get_talkspace_activity(self, limit=None, interval=None):
        return self.get_ranked_activity(limit=limit,
                                        interval=interval,
                                        namespace=1)

    def get_bounding_rev_ids(self, page_id):
        query = self._bounding_revids_query


class RecentChanges(object):
    def __init__(self, lang='en', days=7):
        db_title = lang + 'wiki_p'
        db_host = lang + 'wiki.labsdb'
        self.lang = lang
        self.db = oursql.connect(db=db_title,
                                 host=db_host,
                                 read_default_file=DB_CONFIG_PATH,
                                 charset=None)
        self.earliest = predate(datetime.now(), days)
        self.main_limit = 20
        self.talk_limit = 5

    def mainspace(self):
        cursor = self.db.cursor(oursql.DictCursor)
        cursor.execute('''
            SELECT rc_title AS title,
                   COUNT(*) AS edits,
                   COUNT(DISTINCT rc_user) AS users
            FROM recentchanges
            WHERE rc_namespace = 0
            AND rc_type = 0
            AND rc_timestamp > ?
            GROUP BY rc_title
            ORDER BY COUNT(*)
            DESC
            LIMIT ?
        ''', (self.earliest, self.main_limit))
        ret = cursor.fetchall()
        for edit in ret:
            edit['title'] = edit['title'].decode('utf-8')
            edit['title_s'] = edit['title'].replace('_', ' ')
        return ret

    def talkspace(self):
        cursor = self.db.cursor(oursql.DictCursor)
        cursor.execute('''
            SELECT rc_title AS title,
                   COUNT(*) AS edits,
                   COUNT(DISTINCT rc_user) AS users
            FROM recentchanges
            WHERE rc_namespace = 1
            AND rc_type = 0
            AND rc_timestamp > ?
            GROUP BY rc_title
            ORDER BY COUNT(*)
            DESC
            LIMIT ?
        ''', (self.earliest, self.talk_limit))
        ret = cursor.fetchall()
        for edit in ret:
            edit['title'] = edit['title'].decode('utf-8')
            edit['title_s'] = edit['title'].replace('_', ' ')
        return ret

    def stats(self):
        cursor = self.db.cursor(oursql.DictCursor)
        cursor.execute('''
            SELECT COUNT(*) AS edits,
                   COUNT(DISTINCT rc_title) AS titles,
                   COUNT(DISTINCT rc_user) AS users
            FROM recentchanges
            WHERE rc_namespace = 0
            AND rc_type = 0
            AND rc_timestamp > ?;
        ''', (self.earliest,))
        ret = cursor.fetchall()[0]
        return ret

    def all(self, with_extracts=False):
        ret = {}
        ret['stats'] = self.stats()
        ret['mainspace'] = self.mainspace()
        ret['talkspace'] = self.talkspace()
        if with_extracts:
            titles = [i['title'] for i in ret['mainspace']]
            ret['extracts'] = extracts(self.lang, titles, 3)
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
