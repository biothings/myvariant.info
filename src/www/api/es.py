import re
import json
from utils.common import dotdict, is_str, is_seq
from utils.es import get_es
from elasticsearch import NotFoundError, RequestError
import config

# a query to get variants with most of fields:
# _exists_:dbnsfp AND _exists_:dbsnp AND _exists_:mutdb AND _exists_:cosmic AND _exists_:clinvar AND _exists_:gwassnps


class MVQueryError(Exception):
    pass


class MVScrollSetupError(Exception):
    pass


class ESQuery():
    def __init__(self, index=None, doc_type=None, es_host=None):
        self._es = get_es(es_host)
        self._index = index or config.ES_INDEX_NAME
        self._doc_type = doc_type or config.ES_DOC_TYPE
        self._allowed_options = ['_source', 'start', 'from_', 'size',
                                 'sort', 'explain', 'version', 'facets', 'fetch_all', 'jsonld', 'host']
        self._scroll_time = '1m'
        self._total_scroll_size = 1000   # Total number of hits to return per scroll batch
        if self._total_scroll_size % self.get_number_of_shards() == 0:
            # Total hits per shard per scroll batch
            self._scroll_size = int(self._total_scroll_size / self.get_number_of_shards())
        else:
            raise MVScrollSetupError("_total_scroll_size of {} can't be ".format(self._total_scroll_size) +
                                     "divided evenly among {} shards.".format(self.get_number_of_shards()))

    def _use_hg38(self):
        self._index = config.ES_INDEX_NAME_HG38

    def _get_variantdoc(self, hit):
        doc = hit.get('_source', hit.get('fields', {}))
        doc.setdefault('_id', hit['_id'])
        for attr in ['_score', '_version']:
            if attr in hit:
                doc.setdefault(attr, hit[attr])

        if hit.get('found', None) is False:
            # if found is false, pass that to the doc
            doc['found'] = hit['found']
        # add cadd license info
        if 'cadd' in doc:
            doc['cadd']['_license'] = 'http://goo.gl/bkpNhq'
        return doc

    def _cleaned_res(self, res, empty=[], error={'error': True}, single_hit=False):
        '''res is the dictionary returned from a query.
           do some reformating of raw ES results before returning.

           This method is used for self.mget_variants2 and self.get_variant2 method.
        '''
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

    def _clean_res2(self, res):
        '''res is the dictionary returned from a query.
           do some reformating of raw ES results before returning.

           This method is used for self.query method.
        '''
        _res = res['hits']
        for attr in ['took', 'facets', 'aggregations', '_scroll_id']:
            if attr in res:
                _res[attr] = res[attr]
        _res['hits'] = [self._get_variantdoc(hit) for hit in _res['hits']]
        return _res

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

    def _parse_sort_option(self, options):
        sort = options.get('sort', None)
        if sort:
            _sort_array = []
            for field in sort.split(','):
                field = field.strip()
                # if field == 'name' or field[1:] == 'name':
                #     # sorting on "name" field is ignored, as it is a multi-text field.
                #     continue
                if field.startswith('-'):
                    _f = "%s:desc" % field[1:]
                else:
                    _f = "%s:asc" % field
                _sort_array.append(_f)
            options["sort"] = ','.join(_sort_array)
        return options

    def _get_cleaned_query_options(self, kwargs):
        """common helper for processing fields, kwargs and other options passed to ESQueryBuilder."""
        options = dotdict()
        options.raw = kwargs.pop('raw', False)
        options.rawquery = kwargs.pop('rawquery', False)
        options.fetch_all = kwargs.pop('fetch_all', False)
        options.jsonld = kwargs.pop('jsonld', False)
        options.host = kwargs.pop('host', 'myvariant.info')
        scopes = kwargs.pop('scopes', None)
        if scopes:
            options.scopes = self._cleaned_scopes(scopes)
        fields = kwargs.pop('fields', None)
        if fields:
            fields = self._cleaned_fields(fields)
            if fields:
                kwargs["_source"] = fields
        kwargs = self._parse_sort_option(kwargs)
        for key in set(kwargs) - set(self._allowed_options):
            del kwargs[key]
        options.kwargs = kwargs
        return options

    def get_number_of_shards(self):
        r = self._es.indices.get_settings(self._index)
        n_shards = r[list(r.keys())[0]]['settings']['index']['number_of_shards']
        n_shards = int(n_shards)
        return n_shards

    def exists(self, vid):
        """return True/False if a variant id exists or not."""
        try:
            doc = self.get_variant(vid, fields=None)
            return doc['found']
        except NotFoundError:
            return False

    def get_variant(self, vid, **kwargs):
        '''unknown vid return None'''
        options = self._get_cleaned_query_options(kwargs)
        kwargs = {"_source": options.kwargs["_source"]} if "_source" in options.kwargs else {}
        try:
            res = self._es.get(index=self._index, id=vid, doc_type=self._doc_type, **kwargs)
        except NotFoundError:
            return

        if options.raw:
            return res

        res = self._get_variantdoc(res)
        if options.jsonld:
            res['@context'] = 'http://' + options.host + '/context/variant.jsonld'
        return res

    def mget_variants(self, vid_list, **kwargs):
        options = self._get_cleaned_query_options(kwargs)
        kwargs = {"_source": options.kwargs["_source"]} if "_source" in options.kwargs else {}
        res = self._es.mget(body={'ids': vid_list}, index=self._index, doc_type=self._doc_type, **kwargs)
        return res if options.raw else [self._get_variantdoc(doc) for doc in res['docs']]

    def get_variant2(self, vid, **kwargs):
        options = self._get_cleaned_query_options(kwargs)
        qbdr = ESQueryBuilder(**options.kwargs)
        _q = qbdr.build_id_query(vid, options.scopes)
        if options.rawquery:
            return _q
        res = self._es.search(body=_q, index=self._index, doc_type=self._doc_type)
        if not options.raw:
            res = self._cleaned_res(res, empty=None, single_hit=True)
        return res

    def mget_variants2(self, vid_list, **kwargs):
        '''for /query post request'''
        options = self._get_cleaned_query_options(kwargs)
        qbdr = ESQueryBuilder(**options.kwargs)
        try:
            _q = qbdr.build_multiple_id_query(vid_list, scopes=options.scopes)
        except MVQueryError as err:
            return {'success': False,
                    'error': err.message}
        if options.rawquery:
            return _q
        res = self._es.msearch(body=_q, index=self._index, doc_type=self._doc_type)['responses']
        if options.raw:
            return res

        assert len(res) == len(vid_list)
        _res = []

        for i in range(len(res)):
            hits = res[i]
            qterm = vid_list[i]
            hits = self._cleaned_res(hits, empty=[], single_hit=False)
            if len(hits) == 0:
                _res.append({u'query': qterm,
                             u'notfound': True})
            elif 'error' in hits:
                _res.append({u'query': qterm,
                             u'error': True})
            else:
                for hit in hits:
                    hit[u'query'] = qterm
                    if options.jsonld:
                        hit['@context'] = 'http://' + options.host + '/context/variant.jsonld'
                    _res.append(hit)
        return _res

    def query(self, q, **kwargs):
        # Check if special interval query pattern exists
        interval_query = self._parse_interval_query(q)
        facets = self._parse_facets_option(kwargs)
        options = self._get_cleaned_query_options(kwargs)
        scroll_options = {}
        if options.fetch_all:
            scroll_options.update({'search_type': 'scan', 'size': self._scroll_size, 'scroll': self._scroll_time})
        options['kwargs'].update(scroll_options)
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
            try:
                res = self._es.search(index=self._index, doc_type=self._doc_type, body=_query, **options.kwargs)
            except RequestError:
                return {"error": "invalid query term.", "success": False}

        # if options.fetch_all:
        #     return res

        if not options.raw:
            res = self._clean_res2(res)
        return res

    def scroll(self, scroll_id, **kwargs):
        '''return the results from a scroll ID, recognizes options.raw'''
        options = self._get_cleaned_query_options(kwargs)
        r = self._es.scroll(scroll_id, scroll=self._scroll_time)
        scroll_id = r.get('_scroll_id')
        if scroll_id is None or not r['hits']['hits']:
            return {'success': False, 'error': 'No results to return.'}
        else:
            if not options.raw:
                res = self._clean_res2(r)
            # res.update({'_scroll_id': scroll_id})
            if r['_shards']['failed']:
                res.update({'_warning': 'Scroll request has failed on {} shards out of {}.'.format(r['_shards']['failed'], r['_shards']['total'])})
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
        # _query = {
        #     "query": {
        #         "bool": {
        #             "should": [
        #                 {
        #                     "bool": {
        #                         "must": [
        #                             {
        #                                 "term": {"chrom": chr.lower()}
        #                             },
        #                             {
        #                                 "range": {"chromStart": {"lte": gend}}
        #                             },
        #                             {
        #                                 "range": {"chromEnd": {"gte": gstart}}
        #                             }
        #                         ]
        #                     }
        #                 },
        #                 {
        #                     "bool": {
        #                         "must": [
        #                             {
        #                                 "term": {"chrom": chr.lower()}
        #                             },
        #                             {
        #                                 "range": {"dbnsfp.hg19.start": {"lte": gend}}
        #                             },
        #                             {
        #                                 "range": {"dbnsfp.hg19.end": {"gte": gstart}}
        #                             }
        #                         ]
        #                     }
        #                 }
        #             ]
        #         }
        #     }
        # }
        _query = {
            "query": {
                "bool": {
                    "should": []
                }
            }
        }
        hg19_interval_fields = ['dbnsfp.hg19', 'dbsnp.hg19', 'evs.hg19', 'mutdb.hg19', 'docm.hg19']
        for field in hg19_interval_fields:
            _q = {
                "bool": {
                    "must": [
                        {
                            "term": {"chrom": chr.lower()}
                        },
                        {
                            "range": {field + ".start": {"lte": gend}}
                        },
                        {
                            "range": {field + ".end": {"gte": gstart}}
                        }
                    ]
                }
            }
            _query["query"]["bool"]["should"].append(_q)
        return self._es.search(index=self._index, doc_type=self._doc_type, body=_query, **kwargs)

    def query_fields(self, **kwargs):
        # query the metadata to get the available fields for a variant object
        r = self._es.indices.get(index=self._index)
        return r[list(r.keys())[0]]['mappings']['variant']['properties']


class ESQueryBuilder:
    def __init__(self, **query_options):
        self._query_options = query_options

    def build_id_query(self, vid, scopes=None):
        # _default_scopes = [
        #     '_id',
        #     'rsid', "dbnsfp.rsid", "dbsnp.rsid", "evs.rsid", "mutdb.rsid"  # for rsid
        #     "dbsnp.gene.symbol", 'evs.gene.symbol', 'clinvar.gene.symbol',
        #     'dbnsfp.genename', "cadd.gene.genename", "docm.genename",      # for gene symbols
        # ]
        _default_scopes = '_id'
        scopes = scopes or _default_scopes
        if is_str(scopes):
            _query = {
                "match": {
                    scopes: {
                        "query": "{}".format(vid),
                        "operator": "and"
                    }
                }
            }
        elif is_seq(scopes):
            _query = {
                "multi_match": {
                    "query": "{}".format(vid),
                    "fields": scopes,
                    "operator": "and"
                }
            }
        else:
            raise ValueError('"scopes" cannot be "%s" type'.format(type(scopes)))
        _q = {"query": _query}
        self._query_options.pop("query", None)    # avoid "query" be overwritten by self.query_options
        _q.update(self._query_options)
        return _q

    def build_multiple_id_query(self, vid_list, scopes=None):
        """make a query body for msearch query."""
        _q = []
        for id in vid_list:
            _q.extend(['{}', json.dumps(self.build_id_query(id, scopes))])
        _q.append('')
        return '\n'.join(_q)
