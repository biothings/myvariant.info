# -*- coding: utf-8 -*-
from biothings.www.api.es.handlers import BiothingHandler
from biothings.www.api.es.handlers import MetadataHandler
from biothings.www.api.es.handlers import QueryHandler
from biothings.www.api.es.handlers import StatusHandler
from tornado.web import RequestHandler
from re import search

class CommonHandlerMixin(object):
    def _sanitize_assembly(self, kwargs):
        if self._should_sanitize('assembly', kwargs):
            if kwargs['assembly'].lower() not in self.web_settings.SUPPORTED_ASSEMBLIES:
                kwargs['assembly'] = self.esqb_kwargs['assembly']['default']
            else:
                kwargs['assembly'] = kwargs['assembly'].lower()
        return kwargs
    
    def _get_es_index(self, options):
        return '_'.join([self.web_settings.ES_INDEX_BASE, options.esqb_kwargs.assembly])

class VariantHandler(CommonHandlerMixin, BiothingHandler):
    ''' This class is for the /variant endpoint. '''
    # overridden to sanitize assembly param
    def _sanitize_params(self, kwargs):
        kwargs = super(VariantHandler, self)._sanitize_params(kwargs)
        kwargs = self._sanitize_assembly(kwargs)
        return kwargs

    # redirect improperly formatted hgvs ids
    def _regex_redirect(self, bid):
        m = search('chr.{1,2}(?P<delim>:[g\.]{0,2})\d+', self.request.uri)
        if m:
            de = m.group('delim')
            if de and de != ':g.':
                self.redirect(':g.'.join(self.request.uri.split(de)), permanent=True)

class QueryHandler(CommonHandlerMixin, QueryHandler):
    ''' This class is for the /query endpoint. '''
    # overridden to sanitize assembly param
    def _sanitize_params(self, kwargs):
        kwargs = super(QueryHandler, self)._sanitize_params(kwargs)
        kwargs = self._sanitize_assembly(kwargs)
        return kwargs

class StatusHandler(StatusHandler):
    ''' This class is for the /status endpoint. '''
    pass

class MetadataHandler(CommonHandlerMixin, MetadataHandler):
    ''' This class is for the /metadata endpoint. '''
    # overridden to sanitize assembly param
    def _sanitize_params(self, kwargs):
        kwargs = super(MetadataHandler, self)._sanitize_params(kwargs)
        kwargs = self._sanitize_assembly(kwargs)
        return kwargs

class DemoHandler(RequestHandler):
    ''' For the /demo page. '''
    def get(self):
        with open('../../docs/demo/index.html', 'r') as demo_file:
            self.write(demo_file.read())
