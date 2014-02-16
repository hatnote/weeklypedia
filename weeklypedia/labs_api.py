# -*- coding: utf-8 -*-

from dal import RecentChangesSummarizer

from clastic import Application, render_json, render_json_dev
from clastic.meta import MetaApplication
#from clastic.middleware import GetParamMiddleware

# TODO: make interval and limits parameterized


def fetch_rc(lang='en'):
    rcs = RecentChangesSummarizer(lang=lang)
    return rcs.get_full_summary()


def create_app():
    routes = [('/', fetch_rc, render_json),
              ('/fetch/', fetch_rc, render_json),
              ('/fetch/<lang>', fetch_rc, render_json),
              ('/meta', MetaApplication),
              ('/_dump_environ', lambda request: request.environ, render_json_dev)]
    return Application(routes)


wsgi_app = create_app()


if __name__ == '__main__':
    wsgi_app.serve()
