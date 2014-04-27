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
        _query = {
            "query": {
                "query_string" : {
                    #"default_field" : "content",
                    "query" : q
                }
            }
        }

        return es.search(index_name, doc_type, body=_query, **kwargs)

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

