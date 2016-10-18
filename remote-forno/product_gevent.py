from gevent.wsgi import WSGIServer
from principal import app

http_server = WSGIServer(('', 5002), app)
http_server.serve_forever()
