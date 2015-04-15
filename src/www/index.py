'''
A thin python layer for accessing MyVariant ElasticSearch host.

Currently available URLs:

    /v1/query?q=rs58991260            variant query service
    /v1/variant/<variant_id>    variant annotation service

'''
import sys
import os.path
#import subprocess
#import json

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.escape
from tornado.options import define, options

src_path = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
if src_path not in sys.path:
    sys.path.append(src_path)
#from config import INCLUDE_DOCS
#from utils.es import ESQuery

from www.helper import add_apps, BaseHandler
from www.api.handlers import APP_LIST as api_app_list
from www.beacon.handlers import APP_LIST as beacon_app_list

__USE_WSGI__ = False
#DOCS_STATIC_PATH = os.path.join(src_path, 'docs/_build/html')
#if INCLUDE_DOCS and not os.path.exists(DOCS_STATIC_PATH):
#    raise IOError('Run "make html" to generate sphinx docs first.')
STATIC_PATH = os.path.join(src_path, 'www/static')

define("port", default=8000, help="run on the given port", type=int)
define("address", default="127.0.0.1", help="run on localhost")
define("debug", default=False, type=bool, help="run in debug mode")
tornado.options.parse_command_line()
if options.debug:
    import tornado.autoreload
    import logging
    logging.getLogger().setLevel(logging.DEBUG)
    options.address = '0.0.0.0'


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        #if INCLUDE_DOCS:
            self.render(os.path.join(STATIC_PATH, 'index.html'))

class MetaDataHandler(BaseHandler):
    disable_caching = True

    def get(self):
        # For now, just return a hardcoded object, later we'll actually query the ES db for this information
        self.return_json({
            "stats": {
                'total': 286219908,
                'evs': 1977300,
                'cadd': 163690986,
                'wellderly': 21240519,
                'dbnsfp': 78045379,
                'snpedia': 5907,
                'clinvar': 85789,
                'docm': 1119,
                'mutdb': 420221,
                'cosmic': 1024498,
                'dbsnp': 110234210,
                'emv': 12066,
                'gwassnps': 15243
            }
        })


APP_LIST = [
    (r"/", MainHandler),
    (r"/metadata", MetaDataHandler),
    (r"/v1/metadata", MetaDataHandler),
]

APP_LIST += add_apps('api', api_app_list)
APP_LIST += add_apps('v1', api_app_list)
APP_LIST += add_apps('beacon', beacon_app_list)


settings = {}
if options.debug:
    # from config import STATIC_PATH
    settings.update({
        "static_path": STATIC_PATH,
    })
    # from config import auth_settings
    # settings.update(auth_settings)

def main():
    application = tornado.web.Application(APP_LIST, **settings)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port, address=options.address)
    loop = tornado.ioloop.IOLoop.instance()
    if options.debug:
        tornado.autoreload.start(loop)
        tornado.autoreload.watch(os.path.join(STATIC_PATH, 'index.html'))
        logging.info('Server is running on "%s:%s"...' % (options.address, options.port))

    loop.start()


if __name__ == "__main__":
    main()
