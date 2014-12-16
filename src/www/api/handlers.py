import re
import json

from tornado.web import HTTPError
from elasticsearch import NotFoundError

from www.helper import BaseHandler
from .es import ESQuery
from utils.common import split_ids


class VariantHandler(BaseHandler):
    esq = ESQuery()

    def get(self, vid=None):
        '''/gene/<geneid>
           geneid can be entrezgene, ensemblgene, retired entrezgene ids.
           /gene/1017
           /gene/1017?fields=symbol,name
           /gene/1017?fields=symbol,name,reporter.HG-U133_Plus_2
        '''
        if vid:
            kwargs = self.get_query_params()
            #kwargs.setdefault('scopes', 'entrezgene,ensemblgene,retired')
            #kwargs.setdefault('species', 'all')
            try:
                variant = self.esq.get_variant(vid, **kwargs)
            except NotFoundError:
                raise HTTPError(404)

            self.return_json(variant)
        else:
            raise HTTPError(404)

    def post(self, ids=None):
        '''
           This is essentially the same as post request in QueryHandler, with different defaults.

           parameters:
            ids
            fields
            species
        '''
        kwargs = self.get_query_params()
        ids = kwargs.pop('ids', None)
        if ids:
            ids = re.split('[\s\r\n+|,]+', ids)
            #scopes = 'entrezgene,ensemblgene,retired'
            #fields = kwargs.pop('fields', None)
            #kwargs.setdefault('species', 'all')
            res = self.esq.mget_variants(ids, **kwargs)
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
            species

            explain
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
                res = self.esq.mget_gene2(ids, fields=fields, scopes=scopes, **kwargs)
        else:
            res = {'success': False, 'error': "Missing required parameters."}

        self.return_json(res)


APP_LIST = [
    (r"/variant/(.+)/?", VariantHandler),   # for gene get request
    (r"/variant/?$", VariantHandler),              # for gene post request
    (r"/query/?", QueryHandler),
]
