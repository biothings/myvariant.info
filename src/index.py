from tornado.web import StaticFileHandler, RedirectHandler

from biothings.web.launcher import main
from web.beacon.handlers import BeaconHandler, BeaconInfoHandler

if __name__ == "__main__":
    main([
        # override default frontpage
        (r"/", RedirectHandler, {"url": "/standalone", "permanent": False}),
        (r"/demo/?()", StaticFileHandler,
         {"path": "docs/demo", "default_filename": "index.html"}),
        (r"/standalone/?()", StaticFileHandler,
         {"path": "docs/standalone", "default_filename": "index.html"}),
        (r"/beacon/query?", BeaconHandler),
        (r"/beacon/info", BeaconInfoHandler),
    ])
