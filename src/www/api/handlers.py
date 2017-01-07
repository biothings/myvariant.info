# -*- coding: utf-8 -*-
from biothings.www.api.es.handlers import BiothingHandler
from biothings.www.api.es.handlers import MetadataHandler
from biothings.www.api.es.handlers import QueryHandler
from biothings.www.api.es.handlers import StatusHandler

class VariantHandler(BiothingHandler):
    ''' This class is for the /variant endpoint. '''
    pass

class QueryHandler(QueryHandler):
    ''' This class is for the /query endpoint. '''
    pass

class StatusHandler(StatusHandler):
    ''' This class is for the /status endpoint. '''
    pass

class MetadataHandler(MetadataHandler):
    ''' This class is for the /metadata endpoint. '''
    pass
