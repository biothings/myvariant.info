# -*- coding: utf-8 -*-
from biothings.www.api.handlers import MetaDataHandler, BiothingHandler, QueryHandler, StatusHandler, FieldsHandler
from biothings.settings import BiothingSettings
from www.api.es import ESQuery
import config

biothing_settings = BiothingSettings()

class VariantHandler(BiothingHandler):
    ''' This class is for the /variant endpoint. '''
    esq = ESQuery()

class QueryHandler(QueryHandler):
    ''' This class is for the /query endpoint. '''
    esq = ESQuery()

class StatusHandler(StatusHandler):
    ''' This class is for the /status endpoint. '''
    esq = ESQuery()

class FieldsHandler(FieldsHandler):
    ''' This class is for the /metadata/fields endpoint. '''
    esq = ESQuery()

class MetaDataHandler(MetaDataHandler):
    ''' This class is for the /metadata endpoint. '''
    esq = ESQuery()


def return_applist():
    ret = [
        (r"/status", StatusHandler),
        (r"/metadata", MetaDataHandler),
        (r"/metadata/fields", FieldsHandler),
    ]
    if biothing_settings._api_version:
        ret += [
            (r"/" + biothing_settings._api_version + "/metadata", MetaDataHandler),
            (r"/" + biothing_settings._api_version + "/metadata/fields", FieldsHandler),
            (r"/" + biothing_settings._api_version + "/variant/(.+)/?", VariantHandler),
            (r"/" + biothing_settings._api_version + "/variant/?$", VariantHandler),
            (r"/" + biothing_settings._api_version + "/query/?", QueryHandler),
        ]
    else:
        ret += [
            (r"/variant/(.+)/?", VariantHandler),
            (r"/variant/?$", VariantHandler),
            (r"/query/?", QueryHandler),
        ]
    return ret