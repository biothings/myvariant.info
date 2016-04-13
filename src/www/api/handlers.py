# -*- coding: utf-8 -*-
import re
from biothings.www.api.handlers import MetaDataHandler, BiothingHandler, QueryHandler, StatusHandler, FieldsHandler
from settings import MyVariantSettings
from www.api.es import ESQuery
#import config

myvariant_settings = MyVariantSettings()

class VariantHandler(BiothingHandler):
    ''' This class is for the /variant endpoint. '''
    esq = ESQuery()

    def _examine_kwargs(self, action, kwargs):
        # subclassed to add redirection, assembly, etc
        if action == 'GET':
            m = re.search('chr.{1,2}(?P<delim>:[g\.]{0,2})\d+', self.request.uri)
            if m:
                de = m.group('delim')
                if de and de != ':g.':
                    self.redirect(':g.'.join(self.request.uri.split(de)), permanent=True)
        # default to hg19 assembly
        self.esq._use_hg19()
        if kwargs.pop('assembly', 'hg19').lower() == 'hg38':
            self.esq._use_hg38()
        return None


class QueryHandler(QueryHandler):
    ''' This class is for the /query endpoint. '''
    esq = ESQuery()

    def _examine_kwargs(self, action, kwargs):
        self.esq._use_hg19()
        if kwargs.pop('assembly', 'hg19').lower() == 'hg38':
            self.esq._use_hg38()
        return None    


class StatusHandler(StatusHandler):
    ''' This class is for the /status endpoint. '''
    esq = ESQuery()


class FieldsHandler(FieldsHandler):
    ''' This class is for the /metadata/fields endpoint. '''
    esq = ESQuery()


class MetaDataHandler(MetaDataHandler):
    ''' This class is for the /metadata endpoint. '''
    esq = ESQuery()
    disable_caching = True


def return_applist():
    ret = [
        (r"/status", StatusHandler),
        (r"/metadata", MetaDataHandler),
        (r"/metadata/fields", FieldsHandler),
    ]
    if myvariant_settings._api_version:
        ret += [
            (r"/" + myvariant_settings._api_version + "/metadata", MetaDataHandler),
            (r"/" + myvariant_settings._api_version + "/metadata/fields", FieldsHandler),
            (r"/" + myvariant_settings._api_version + "/variant/(.+)/?", VariantHandler),
            (r"/" + myvariant_settings._api_version + "/variant/?$", VariantHandler),
            (r"/" + myvariant_settings._api_version + "/query/?", QueryHandler),
        ]
    else:
        ret += [
            (r"/variant/(.+)/?", VariantHandler),
            (r"/variant/?$", VariantHandler),
            (r"/query/?", QueryHandler),
        ]
    return ret
