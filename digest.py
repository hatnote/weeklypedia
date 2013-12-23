import oursql
import os
from flup.server.fcgi import WSGIServer
from clastic import Application, render_json, render_json_dev
from clastic.meta import MetaApplication
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
        self.db = oursql.connect(db=db_title,
                                 host=db_host,
                                 read_default_file=DB_PATH,
                                 charset=None,
                                 use_unicode=False)
        self.earliest = predate(datetime.now(), days)

    def weekly(self):
        cursor = self.db.cursor(oursql.DictCursor)
        cursor.execute('''
            SELECT rc_title, COUNT(*), COUNT(DISTINCT rc_user)
            FROM recentchanges
            WHERE rc_namespace = 0
            AND rc_type = 0
            AND rc_timestamp > ?
            GROUP BY rc_title
            ORDER BY COUNT(*)
            DESC
            LIMIT 25
        ''', (self.earliest,))
        return cursor.fetchall()

    def stats(self):
        cursor = self.db.cursor(oursql.DictCursor)
        cursor.execute('''
            SELECT COUNT(*), COUNT(DISTINCT rc_title)
            FROM recentchanges
            WHERE rc_namespace = 0
            AND rc_type = 0
            AND rc_timestamp > ?;
        ''', (self.earliest,))
        return cursor.fetchall()

def fetch_rc(lang='en'):
    ko = RecentChanges(lang=lang)
    import pdb;pdb.set_trace()
    total_edits = ko.stats()
    top_mainspace = ko.weekly()
    ret = {
        'edits': total_edits[0]['COUNT(*)'], 
        'titles': total_edits[0]['COUNT(DISTINCT rc_title)'], 
        'top': [(i['rc_title'], i['COUNT(*)'], i['COUNT(DISTINCT rc_user)']) for i in top_mainspace],
        }
    return ret

if __name__ == '__main__':
    routes = [('/', fetch_rc, render_json),
              ('/meta', MetaApplication),
              ('/_dump_environ', lambda request: request.environ, render_json_dev),
              ('/<lang>', fetch_rc, render_json)]
    app = Application(routes)
    WSGIServer(app).run()

