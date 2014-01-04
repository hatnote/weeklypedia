
import os
from datetime import datetime, timedelta

import oursql

from clastic import Application, render_json, render_json_dev
from clastic.render import AshesRenderFactory
from clastic.meta import MetaApplication
from wapiti import WapitiClient


DB_PATH = os.path.expanduser('~/replica.my.cnf')
DATE_FORMAT = '%Y%m%d%H%M%S'
_CUR_PATH = os.path.dirname(os.path.abspath(__file__))

def parse_date_str(date_str):
    return datetime.strptime(date_str, DATE_FORMAT)

def predate(date, days):
    pdate = date - timedelta(days)
    return pdate.strftime(DATE_FORMAT)


class RecentChanges(object):
    def __init__(self, lang='en', days=7):
        db_title = lang + 'wiki_p'
        db_host = lang + 'wiki.labsdb'
        self.lang = lang
        self.db = oursql.connect(db=db_title,
                                 host=db_host,
                                 read_default_file=DB_PATH,
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
            WHERE rc_namespace = 1
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

    def all(self):
        stats = self.stats()
        mainspace = self.mainspace()
        talkspace = self.talkspace()
        titles = [i['title'] for i in mainspace]
        return {
            'stats': stats,
            'articles': mainspace,
            #'extracts': extracts(self.lang, titles, 3),
            'talks': talkspace,
            'lang': self.lang
        }

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

def fetch_rc(lang='en'):
    changes = RecentChanges(lang=lang)
    return changes.all()


def create_app():
    routes = [('/', fetch_rc, render_json),
              ('/meta', MetaApplication),
              ('/_dump_environ', lambda request: request.environ, render_json_dev),
              ('/fetch/', fetch_rc, 'template.html'),
              ('/fetch/<lang>', fetch_rc, 'template.html')]
    ashes_render = AshesRenderFactory(_CUR_PATH)
    return Application(routes, [], ashes_render)


wsgi_app = create_app()


if __name__ == '__main__':
    import pdb;pdb.set_trace()  # do your debugging here
