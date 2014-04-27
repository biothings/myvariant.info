import re
from elasticsearch import Elasticsearch


es = Elasticsearch()
es_host = 'localhost:9200'
index_name = 'myvariant_all'
doc_type = 'variant'

class ESQuery():
    def get_variant(self, vid, **kwargs):
        return es.get(index=index_name, id=vid, doc_type=doc_type, **kwargs)

    def mget_variants(self, vid_list, **kwargs):
        return es.mget(body=vid_list, index=index_name, doc_type=doc_type, **kwargs)

    def query(self, q, **kwargs):
        # Check if special interval query pattern exists
        interval_query = self._parse_interval_query(q)
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
            return es.search(index_name, doc_type, body=_query, **kwargs)

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
        #if chr.lower().startswith('chr'):
        #    chr = chr[3:]
        _query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "term": {"dbsnp.chrom": chr.lower()}
                        },
                        {
                            "range": {"dbsnp.chromStart": {"lte": gend}}
                        },
                        {
                            "range": {"dbsnp.chromEnd": {"gte": gstart}}
                        }
                    ]
                }
            }
        }

        return es.search(index_name, doc_type, body=_query, **kwargs)

