
from flup.server.fcgi import WSGIServer
from weeklypedia.labs_api import wsgi_app


wsgi_server = WSGIServer(wsgi_app)


if __name__ == '__main__':
    wsgi_server.run()
