import re
from elasticsearch import Elasticsearch, NotFoundError


es = Elasticsearch()
es_host = 'localhost:9200'
index_name = 'myvariant_all'
doc_type = 'variant'

class ESQuery():
    def get_variant(self, vid, **kwargs):
        return es.get(index=index_name, id=vid, doc_type=doc_type, **kwargs)

    def exists(self, vid):
        """return True/False if a variant id exists or not."""
        try:
            doc = self.get_variant(vid, fields=None)
            return doc['found']
        except NotFoundError, e:
            return False

    def mget_variants(self, vid_list, **kwargs):
        return es.mget(body=vid_list, index=index_name, doc_type=doc_type, **kwargs)

    def query(self, q, **kwargs):
        # Check if special interval query pattern exists
        interval_query = self._parse_interval_query(q)
        facets = self._parse_facets_option(kwargs)
        if interval_query:
            kwargs.update(interval_query)
            print kwargs
            return self.query_interval(**kwargs)
        else:
            _query = {
                "query": {
                    "query_string" : {
                        #"default_field" : "content",
                        "query" : q
                    }
                }
            }
            if facets:
                _query['facets'] = facets
            return es.search(index_name, doc_type, body=_query, **kwargs)

    def _parse_facets_option(self, options):
        facets = options.pop('facets', None)
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

    def query_interval(self, chr,  gstart, gend, **kwargs):
        #gstart = safe_genome_pos(gstart)
        #gend = safe_genome_pos(gend)
        if chr.lower().startswith('chr'):
            chr = chr[3:]
        _query = {
            "query": {
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
            }
        }

        return es.search(index_name, doc_type, body=_query, **kwargs)

