from tornado.web import StaticFileHandler, RedirectHandler

from biothings.web.index_base import main
from web.beacon.handlers import BeaconHandler, BeaconInfoHandler

if __name__ == "__main__":
    main([
        (r"/", RedirectHandler, {"url": "/standalone"}), # override default frontpage
        (r"/demo/?()", StaticFileHandler, {"path": "docs/demo", "default_filename": "index.html"}),
        (r"/standalone/?()", StaticFileHandler, {"path": "docs/standalone", "default_filename": "index.html"}),
        (r"/beacon/query?", BeaconHandler),
        (r"/beacon/info", BeaconInfoHandler),
    ])
