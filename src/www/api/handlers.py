import re
import json

from tornado.web import HTTPError
from www.helper import BaseHandler
from .es import ESQuery
from utils.common import split_ids


class VariantHandler(BaseHandler):
    esq = ESQuery()

    def get(self, vid=None):
        '''
        /variant/<variantid>
            varintid can be HGVS name.
        /variant/chr1:g.160145907G>T
        /variant/chr1:g.160145907G>T?fields=dbsnp
        /variant/chr1:g.160145907G>T?fields=dbnsfp.genename,dbnsfp.cadd

        parameters:
            fields
            callback
            email
        '''
        if vid:
            kwargs = self.get_query_params()
            variant = self.esq.get_variant(vid, **kwargs)
            if variant:
                self.return_json(variant)
            else:
                raise HTTPError(404)
        else:
            raise HTTPError(404)

    def post(self, ids=None):
        '''
           This is essentially the same as post request in QueryHandler, with different defaults.

           parameters:
            ids
            fields
            email
        '''
        kwargs = self.get_query_params()
        ids = kwargs.pop('ids', None)
        if ids:
            ids = re.split('[\s\r\n+|,]+', ids)
            #scopes = 'entrezgene,ensemblgene,retired'
            res = self.esq.mget_variants2(ids, **kwargs)
        else:
            res = {'success': False, 'error': "Missing required parameters."}

        self.return_json(res)


class QueryHandler(BaseHandler):
    esq = ESQuery()

    def get(self):
        '''
        parameters:
            q
            fields
            from
            size
            sort
            facets
            callback
            email

            explain
            raw
        '''
        kwargs = self.get_query_params()
        q = kwargs.pop('q', None)
        _has_error = False
        if q:
            explain = self.get_argument('explain', None)
            if explain and explain.lower() == 'true':
                kwargs['explain'] = True
            for arg in ['from', 'size', 'mode']:
                value = kwargs.get(arg, None)
                if value:
                    try:
                        kwargs[arg] = int(value)
                    except ValueError:
                        res = {'success': False, 'error': 'Parameter "{}" must be an integer.'.format(arg)}
                        _has_error = True
            if not _has_error:
                res = self.esq.query(q, **kwargs)
        else:
            res = {'success': False, 'error': "Missing required parameters."}

        self.return_json(res)

    def post(self):
        '''
        parameters:
            q
            scopes
            fields
            email

            jsoninput   if true, input "q" is a json string, must be decoded as a list.
        '''
        kwargs = self.get_query_params()
        q = kwargs.pop('q', None)
        jsoninput = kwargs.pop('jsoninput', None) in ('1', 'true')
        if q:
            # ids = re.split('[\s\r\n+|,]+', q)
            try:
                ids = json.loads(q) if jsoninput else split_ids(q)
                if not isinstance(ids, list):
                    raise ValueError
            except ValueError:
                ids = None
                res = {'success': False, 'error': 'Invalid input for "q" parameter.'}
            if ids:
                scopes = kwargs.pop('scopes', None)
                fields = kwargs.pop('fields', None)
                res = self.esq.mget_variant2(ids, fields=fields, scopes=scopes, **kwargs)
        else:
            res = {'success': False, 'error': "Missing required parameters."}

        self.return_json(res)


APP_LIST = [
    (r"/variant/(.+)/?", VariantHandler),   # for gene get request
    (r"/variant/?$", VariantHandler),              # for gene post request
    (r"/query/?", QueryHandler),
]
