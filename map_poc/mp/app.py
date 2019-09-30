# WSGI module for use with Apache mod_wsgi or gunicorn

# # uncomment the following lines for logging
# # create a log.ini with `mapproxy-util create -t log-ini`
# from logging.config import fileConfig
# import os.path
# fileConfig(r'/mapproxy/log.ini', {'here': os.path.dirname(__file__)})

from mapproxy.multiapp import make_wsgi_app
application = make_wsgi_app(r'/mapproxy/', allow_listing=True)

class SecurityInjector(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        environ['QUERY_STRING'] += "&user=pietje"
        environ['REQUEST_URI'] += "&user=pietje"
        print(environ)
        return self.app(environ, start_response)

application = SecurityInjector(application)