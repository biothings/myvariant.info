# -*- coding: utf-8 -*-
import re
import json
from biothings.www.api.es import ESQuery
from settings import MyVariantSettings

myvariant_settings = MyVariantSettings()

class ESQuery(ESQuery):
    def __init__(self):
        super( ESQuery, self ).__init__()
        self._hg38 = False

    def _get_genome_position_fields(self, hg38=False):
        if hg38:
            return myvariant_settings.hg38_fields
        else:
            return myvariant_settings.hg19_fields

    def _parse_interval_query(self, q):
        interval_pattern = r'(?P<pre_query>.+(?P<pre_and>[Aa][Nn][Dd]))*(?P<interval>\s*chr(?P<chr>\w+):(?P<gstart>[0-9,]+)-(?P<gend>[0-9,]+)\s*)(?P<post_query>(?P<post_and>[Aa][Nn][Dd]).+)*'
        single_pattern = r'(?P<pre_query>.+(?P<pre_and>[Aa][Nn][Dd]))*(?P<interval>\s*chr(?P<chr>\w+):(?P<gend>(?P<gstart>[0-9,]+))\s*)(?P<post_query>(?P<post_and>[Aa][Nn][Dd]).+)*'
        patterns = [interval_pattern, single_pattern]
        if q:
            for pattern in patterns:
                mat = re.search(pattern, q)
                if mat:
                    r = mat.groupdict()
                    if r['pre_query']:
                        r['query'] = r['pre_query'].rstrip(r['pre_and']).rstrip()
                        if r['post_query']:
                            r['query'] += ' ' + r['post_query']
                    elif r['post_query']:
                        r['query'] = r['post_query'].lstrip(r['post_and']).lstrip()
                    else:
                        r['query'] = None
                    return r

    def build_interval_query(self, chr, gstart, gend, rquery, hg38):
        """ Build an interval query - called by the ESQuery.query method. """
        if chr.lower().startswith('chr'):
            chr = chr[3:]
        _query = {
            "query": {
                "bool": {
                    "filter": {
                        "bool": {
                            "must": [{
                                "bool": {
                                    "should": [{
                                        "term": {field: chr.lower()}
                                    } for field in myvariant_settings.chrom_fields]
                                }
                            }, {
                                "bool": {
                                    "should": [{
                                        "bool": {
                                            "must": [
                                                {
                                                    "range": {field + ".start": {"lte": gend}}
                                                },
                                                {
                                                    "range": {field + ".end": {"gte": gstart}}
                                                }
                                            ]
                                        }
                                    } for field in self._get_genome_position_fields(hg38)]
                                }
                            }]
                        }
                    }
                }
            }
        }
        if rquery:
            _query["query"]["bool"]["must"] = {"query_string": {"query": rquery}}
        return _query

    def _modify_biothingdoc(self, doc, options):
        if 'cadd' in doc:
            doc['cadd']['_license'] = 'http://goo.gl/bkpNhq'
        return doc

    def _use_hg38(self):
        self._hg38 = True

    def _use_hg19(self):
        self._hg38 = False

    def _build_query(self, q, kwargs):
        # overriding to implement interval query
        interval_query = self._parse_interval_query(q)
        if interval_query:
            return self.build_interval_query(chr=interval_query["chr"],
                                              gstart=interval_query["gstart"],
                                              gend=interval_query["gend"],
                                              rquery=interval_query["query"],
                                              hg38=self._hg38)
        return {"query":{"query_string":{"query":q}}}
