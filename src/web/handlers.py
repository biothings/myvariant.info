from tornado.web import RequestHandler

from biothings.web.handlers import (
    MetadataFieldHandler,
    MetadataSourceHandler)


class AssemblyAwareMixin(RequestHandler):

    def prepare(self):
        super().prepare()
        self.biothing_type = self.args.assembly


class MVMetadataFieldHandler(AssemblyAwareMixin, MetadataFieldHandler):
    pass


class MVMetadataSourceHandler(AssemblyAwareMixin, MetadataSourceHandler):
    pass
