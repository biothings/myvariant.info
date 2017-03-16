# -*- coding: utf-8 -*-
from biothings.www.api.es.query_builder import ESQueryBuilder
import re

INTERVAL_PATTERN = re.compile(r'(?P<pre_query>.+(?P<pre_and>[Aa][Nn][Dd]))*(?P<interval>\s*chr(?P<chr>[1-9xXyYmM][0-9tT]?):(?P<gstart>[0-9,]+)-(?P<gend>[0-9,]+)\s*)(?P<post_query>(?P<post_and>[Aa][Nn][Dd]).+)*')
SNP_PATTERN = re.compile(r'(?P<pre_query>.+(?P<pre_and>[Aa][Nn][Dd]))*(?P<interval>\s*chr(?P<chr>[1-9xXyYmM][0-9tT]?):(?P<gend>(?P<gstart>[0-9,]+))\s*)(?P<post_query>(?P<post_and>[Aa][Nn][Dd]).+)*')
PATTERNS = [INTERVAL_PATTERN, SNP_PATTERN]

class ESQueryBuilder(ESQueryBuilder):
    # Implement app specific queries here
    def _parse_interval_query(self, q):
        for pattern in PATTERNS:
            m = re.search(pattern, q)
            if m:
                r = m.groupdict()
                if r['pre_query']:
                    r['query'] = r['pre_query'].rstrip(r['pre_and']).rstrip()
                    if r['post_query']:
                        r['query'] += ' ' + r['post_query']
                elif r['post_query']:
                    r['query'] = r['post_query'].lstrip(r['post_and']).lstrip()
                else:
                    r['query'] = None
                return r
        return False

    def _interval_query(self, query_match):
        # already guaranteed to be an interval query - query_match is re match-like object
        _query = {
            "query": {
                "bool": {
                    "filter": {
                        "bool": {
                            "must": [
                                        {
                                            "term": {"chrom": query_match['chr']}    
                                        },
                                        {
                                            "range": {self.options.assembly + ".start": {"lte": query_match['gend']}}
                                        },
                                        {
                                            "range": {self.options.assembly + ".end": {"gte": query_match['gstart']}}
                                        }
                                    ]
                        }
                    }
                }
            }
        }
        if query_match['query']:
            _query["query"]["bool"]["must"] = {"query_string": {"query": query_match['query']}}
        return self.queries.raw_query(_query)

    def _extra_query_types(self, q):
        interval_match = self._parse_interval_query(q) 
        if interval_match:
            return self._interval_query(interval_match)
        # Can add more automatic queries here...should always return something falsy if no match
        # as this triggers the default query
        return {}
