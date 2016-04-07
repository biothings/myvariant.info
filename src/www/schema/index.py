import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import os.path
from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)


SCHEMA_PATH = os.path.split(os.path.abspath(__file__))[0]


class SchemaHandler(tornado.web.RequestHandler):
    cache_max_age = 604800  # 7days

    def get(self, ns, file_name):
        file_path = os.path.join(SCHEMA_PATH, ns, file_name)
        # if no file, raise 404 error
        file_path += '.json'
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.set_header("Cache-Control", "max-age={}, public".format(self.cache_max_age))
        if os.path.exists(file_path):
            with open(file_path, 'r') as json_context:
                self.write(json_context.read())
        else:
            raise tornado.web.HTTPError(404)


APP_LIST = [
    (r"/(.+)/(.+)", SchemaHandler)
]

def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application(APP_LIST)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
