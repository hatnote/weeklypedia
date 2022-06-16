# -*- coding: utf-8 -*-

from dal import RecentChangesSummarizer

from clastic import Application, render_json, render_basic
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
              ('/v2', fetch_rc, render_basic),
              ('/v2/fetch/', fetch_rc, render_basic),
              ('/v2/fetch/<lang>', fetch_rc, render_basic),
              ('/meta', MetaApplication()),
              ('/_dump_environ', lambda request: request.environ, render_basic)]
    return Application(routes, debug=True)


wsgi_app = create_app()


if __name__ == '__main__':
    wsgi_app.serve()
