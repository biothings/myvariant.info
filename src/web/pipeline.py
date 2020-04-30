import re

from biothings.utils.web.es_dsl import AsyncSearch
from biothings.web.pipeline import ESQueryBuilder, ESQueryBackend


INTERVAL_PATTERN = re.compile(r'(?P<pre_query>.+(?P<pre_and>[Aa][Nn][Dd]))*(?P<interval>\s*chr(?P<chr>[1-9xXyYmM][0-9tT]?):(?P<gstart>[0-9,]+)-(?P<gend>[0-9,]+)\s*)(?P<post_query>(?P<post_and>[Aa][Nn][Dd]).+)*')
SNP_PATTERN = re.compile(r'(?P<pre_query>.+(?P<pre_and>[Aa][Nn][Dd]))*(?P<interval>\s*chr(?P<chr>[1-9xXyYmM][0-9tT]?):(?P<gend>(?P<gstart>[0-9,]+))\s*)(?P<post_query>(?P<post_and>[Aa][Nn][Dd]).+)*')
PATTERNS = [INTERVAL_PATTERN, SNP_PATTERN]


class MVQueryBuilder(ESQueryBuilder):

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

    def default_string_query(self, q, options):

        match = self._parse_interval_query(q)
        if match:  # interval query
            search = AsyncSearch()
            if match['query']:
                search = search.query("query_string", query=match['query'])
            search = search.filter('match', chrom=match['chr'])
            assembly = 'hg38' if options.assembly == 'hg38' else 'hg19'
            search = search.filter('range', **{assembly + ".start": {"lte": match['gend']}})
            search = search.filter('range', **{assembly + ".end": {"gte": match['gstart']}})

        else:  # default query
            search = AsyncSearch().query("query_string", query=q)

        return search


class MVQueryBackend(ESQueryBackend):

    def execute(self, query, options):

        # override index to query
        if options.assembly == 'hg38':
            options.biothing_type = 'hg38'

        return super().execute(query, options)

