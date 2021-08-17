import re
from typing import Dict, Optional

from elasticsearch_dsl import Search
from biothings.web.query import ESQueryBuilder, AsyncESQueryBackend


INTERVAL_PATTERN_INT_ONLY = re.compile(
    r"""
    chr  # string literal chr   
        (?P<chr>[1-9]|1[0-9]|2[0-2]|X|Y|MT)  # chromasomes 1-22, X, Y, and MT
        :  # literal colon sign
        (
            # captures an interval
            (?P<gstart>[\d,]+)-(?P<gend>[\d,]+)  # range, we only allow comma as sep.
            |  # or one position
            (?P<gpos>[\d,]+)
        )
    (
        \s+AND\s+  # take a hitch on the regex engine and prepare the post_query
        (?P<post_query_string>\S.+)  # match a non-whitespace followed by anything
    )?
    """,
    flags=re.ASCII | re.IGNORECASE | re.VERBOSE
)


class MVQueryBuilder(ESQueryBuilder):
    @staticmethod
    def _parse_interval_query(q: str):
        # don't even bother when we don't see chr
        # even with improved regex, this is a few times faster
        start_pos = q.find('chr')
        if start_pos < 0:
            return None
        pre_query = q[:start_pos].strip()
        if pre_query != '':
            # pre_query non empty and does not end in AND\s+
            if not q[start_pos - 1].isspace():
                return None
            if pre_query[-3:].upper() != 'AND':
                return None
            pre_query = pre_query[:-3]  # strip the AND
        else:
            pre_query = None
        m = re.match(INTERVAL_PATTERN_INT_ONLY, q[start_pos:])
        if not m:
            return None
        md = m.groupdict()
        r = {}
        # copy chr
        r['chr'] = md['chr']
        # copy start/end
        if md['gpos']:
            r['gstart'] = r['gend'] = md['gpos']
        else:
            r['gstart'] = md['gstart']
            r['gend'] = md['gend']
        r['query'] = ' AND '.join(filter(
                       None, (
                           pre_query,
                           md['post_query_string'],
                       )))
        return r

    def default_string_query(self, q, options):

        match = self._parse_interval_query(q)
        if match:  # interval query
            search = Search()
            if match['query'] != '':
                search = search.query("query_string", query=match['query'])
            search = search.filter('match', chrom=match['chr'])
            assembly = 'hg38' if options.assembly == 'hg38' else 'hg19'
            search = search.filter('range', **{assembly + ".start": {"lte": match['gend']}})
            search = search.filter('range', **{assembly + ".end": {"gte": match['gstart']}})

        else:  # default query
            search = super().default_string_query(q, options)

        return search


class MVQueryBackend(AsyncESQueryBackend):

    def execute(self, query, **options):

        # override index to query
        if options.get('assembly') == 'hg38':
            options['biothing_type'] = 'hg38'

        return super().execute(query, **options)
