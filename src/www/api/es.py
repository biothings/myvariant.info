import re
from utils.common import dotdict, is_str, is_seq
from elasticsearch import Elasticsearch, NotFoundError
import config

es_host = config.ES_HOST
es = Elasticsearch(es_host)
index_name = config.ES_INDEX_NAME
doc_type = config.ES_DOC_TYPE

class ESQuery():
    def _get_variantdoc(self, hit):
        doc = hit.get('_source', hit.get('fields', {}))
        doc.setdefault('_id', hit['_id'])
        if '_version' in hit:
            doc.setdefault('_version', hit['_version'])
        return doc

    def _cleaned_res(self, res, empty=[], error={'error': True}, single_hit=False):
        '''res is the dictionary returned from a query.'''
        if 'error' in res:
            return error

        hits = res['hits']
        total = hits['total']
        if total == 0:
            return empty
        elif total == 1 and single_hit:
            return self._get_variantdoc(hits['hits'][0])
        else:
            return [self._get_variantdoc(hit) for hit in hits['hits']]

    def _cleaned_scopes(self, scopes):
        '''return a cleaned scopes parameter.
            should be either a string or a list of scope fields.
        '''
        if scopes:
            if is_str(scopes):
                scopes = [x.strip() for x in scopes.split(',')]
            if is_seq(scopes):
                scopes = [x for x in scopes if x]
                if len(scopes) == 1:
                    scopes = scopes[0]
            else:
                scopes = None
        else:
            scopes = None
        return scopes

    def _cleaned_fields(self, fields):
        '''return a cleaned fields parameter.
            should be either None (return all fields) or a list fields.
        '''
        if fields:
            if is_str(fields):
                if fields.lower() == 'all':
                    fields = None     # all fields will be returned.
                else:
                    fields = [x.strip() for x in fields.split(',')]
        else:
            fields = self._default_fields
        return fields

    def _get_cleaned_query_options(self, kwargs):
        """common helper for processing fields, kwargs and other options passed to ESQueryBuilder."""
        options = dotdict()
        options.raw = kwargs.pop('raw', False)
        options.rawquery = kwargs.pop('rawquery', False)
        scopes = kwargs.pop('scopes', None)
        if scopes:
            options.scopes = self._cleaned_scopes(scopes)
        fields = kwargs.pop('fields', None)
        if fields:
            kwargs["_source"] = self._cleaned_fields(fields)
        options.kwargs = kwargs
        return options

    def get_variant(self, vid, **kwargs):
        options = self._get_cleaned_query_options(kwargs)
        res = es.get(index=index_name, id=vid, doc_type=doc_type, **options.kwargs)
        return res if options.raw else self._get_variantdoc(res)

    def exists(self, vid):
        """return True/False if a variant id exists or not."""
        try:
            doc = self.get_variant(vid, fields=None)
            return doc['found']
        except NotFoundError:
            return False

    def mget_variants(self, vid_list, **kwargs):
        options = self._get_cleaned_query_options(kwargs)
        res = es.mget(body={'ids': vid_list}, index=index_name, doc_type=doc_type, **options.kwargs)
        return res if options.raw else [self._get_variantdoc(doc) for doc in res]

    def query(self, q, **kwargs):
        # Check if special interval query pattern exists
        interval_query = self._parse_interval_query(q)
        facets = self._parse_facets_option(kwargs)
        options = self._get_cleaned_query_options(kwargs)
        if interval_query:
            options['kwargs'].update(interval_query)
            res = self.query_interval(**options.kwargs)
        else:
            _query = {
                "query": {
                    "query_string": {
                        #"default_field" : "content",
                        "query": q
                    }
                }
            }
            if facets:
                _query['facets'] = facets
            res = es.search(index_name, doc_type, body=_query, **options.kwargs)

        if not options.raw:
            _res = res['hits']
            _res['took'] = res['took']
            if "facets" in res:
                _res['facets'] = res['facets']
            for v in _res['hits']:
                del v['_type']
                del v['_index']
                for attr in ['fields', '_source']:
                    if attr in v:
                        v.update(v[attr])
                        del v[attr]
                        break
            res = _res
        return res

    def _parse_facets_option(self, kwargs):
        facets = kwargs.pop('facets', None)
        if facets:
            _facets = {}
            for field in facets.split(','):
                _facets[field] = {"terms": {"field": field}}
            return _facets

    def _parse_interval_query(self, query):
        '''Check if the input query string matches interval search regex,
           if yes, return a dictionary with three key-value pairs:
              chr
              gstart
              gend
            , otherwise, return None.
        '''
        pattern = r'chr(?P<chr>\w+):(?P<gstart>[0-9,]+)-(?P<gend>[0-9,]+)'
        if query:
            mat = re.search(pattern, query)
            if mat:
                return mat.groupdict()

    def query_interval(self, chr, gstart, gend, **kwargs):
        #gstart = safe_genome_pos(gstart)
        #gend = safe_genome_pos(gend)
        if chr.lower().startswith('chr'):
            chr = chr[3:]
        _query = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "bool": {
                                "must": [
                                    {
                                        "term": {"chrom": chr.lower()}
                                    },
                                    {
                                        "range": {"chromStart": {"lte": gend}}
                                    },
                                    {
                                        "range": {"chromEnd": {"gte": gstart}}
                                    }
                                ]
                            }
                        },
                        {
                            "bool": {
                                "must": [
                                    {
                                        "term": {"chrom": chr.lower()}
                                    },
                                    {
                                        "range": {"dbnsfp.hg19.start": {"lte": gend}}
                                    },
                                    {
                                        "range": {"dbnsfp.hg19.end": {"gte": gstart}}
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        }

        return es.search(index_name, doc_type, body=_query, **kwargs)
