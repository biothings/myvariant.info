from tornado.web import StaticFileHandler, RedirectHandler

from biothings.web.launcher import main


if __name__ == "__main__":
    main([
        # override default frontpage
        (r"/", RedirectHandler, {"url": "/standalone", "permanent": False}),
        (r"/demo/?()", StaticFileHandler,
         {"path": "docs/demo", "default_filename": "index.html"}),
        (r"/standalone/?()", StaticFileHandler,
         {"path": "docs/standalone", "default_filename": "index.html"}),
    ])
