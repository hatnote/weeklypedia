import oursql
import os
from flup.server.fcgi import WSGIServer
from clastic import Application, render_json, render_json_dev
from clastic.meta import MetaApplication
from wapiti import WapitiClient
from datetime import datetime, timedelta

DB_PATH = os.path.expanduser('~/replica.my.cnf')
DATE_FORMAT = '%Y%m%d%H%M%S'

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
        self.main_limit = 25
        self.talk_limit = 5

    def mainspace(self):
        cursor = self.db.cursor(oursql.DictCursor)
        cursor.execute('''
            SELECT rc_title, COUNT(*), COUNT(DISTINCT rc_user)
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
        return [(i['rc_title'], i['COUNT(*)'], i['COUNT(DISTINCT rc_user)']) for i in ret]

    def talkspace(self):
        cursor = self.db.cursor(oursql.DictCursor)
        cursor.execute('''
            SELECT rc_title, COUNT(*), COUNT(DISTINCT rc_user)
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
        return [(i['rc_title'], i['COUNT(*)'], i['COUNT(DISTINCT rc_user)']) for i in ret]

    def stats(self):
        cursor = self.db.cursor(oursql.DictCursor)
        cursor.execute('''
            SELECT COUNT(*), COUNT(DISTINCT rc_title), COUNT(DISTINCT rc_user)
            FROM recentchanges
            WHERE rc_namespace = 0
            AND rc_type = 0
            AND rc_timestamp > ?;
        ''', (self.earliest,))
        ret = cursor.fetchall()[0]
        return {
            'edits': ret['COUNT(*)'], 
            'titles': ret['COUNT(DISTINCT rc_title)'], 
            'users': ret['COUNT(DISTINCT rc_user)']
        }

    def all(self):
        stats = self.stats()
        mainspace = self.mainspace()
        talkspace = self.talkspace()
        titles = [i[0].decode('utf-8') for i in mainspace]
        return {
            'stats': stats,
            'articles': mainspace,
            'extracts': extracts(self.lang, titles, 3),
            'talks': talkspace
        }

def extracts(lang, titles, limit):
    wc = WapitiClient('stephen.laporte@gmail.com',
                      api_url='https://' + lang + '.wikipedia.org/w/api.php')
    if limit > len(titles):
        limit = len(titles)
    ret = []
    for i in range(limit - 1):
        title = titles[i]
        res = wc.get_page_extract(title)
        ret.append((title, res[0].extract))
    return ret

def fetch_rc(lang='en'):
    changes = RecentChanges(lang=lang)
    return changes.all()

if __name__ == '__main__':
    routes = [('/', fetch_rc, render_json),
              ('/meta', MetaApplication),
              ('/_dump_environ', lambda request: request.environ, render_json_dev),
              ('/<lang>', fetch_rc, render_json)]
    app = Application(routes)
    WSGIServer(app).run()

