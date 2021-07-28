import re
from typing import Dict, Optional

from elasticsearch_dsl import Search
from biothings.web.query import ESQueryBuilder, AsyncESQueryBackend


INTERVAL_PATTERN = re.compile(
    r"""
    (?P<pre_query>
        (?P<pre_query_string>.+)  # query string before the interval
        \s+AND\s+  # whitespace and string literal AND and whitespace
    )?  # pre_query is optional
    \s*  # zero or more whitespace, if there is a pre_query, they get consumed by that one
    (?P<interval>
        chr  # string literal chr   
        (?P<chr>[1-9]|1[0-9]|2[0-2]|X|Y|MT)  # chromasomes 1-22, X, Y, and MT
        :  # literal colon sign
        (
            # captures an interval
            (?P<gstart>[\d,]+)-(?P<gend>[\d,]+)  # range, we only allow comma as sep.
            |  # or one position
            (?P<gpos>[\d,]+)
        )
    )
    \s*? # zero or more whitespace, non-greedy
         #  so that post query can consume whitespaces, while extra spaces are also fine
    (?P<post_query>
        \s+AND\s+  # when post_query exists, at least one whitespace is consumed
        (?P<post_query_string>.+)  # query string after the interval
    )?  # optional
    """,
    flags=re.ASCII | re.IGNORECASE | re.VERBOSE
)


class MVQueryBuilder(ESQueryBuilder):
    @staticmethod
    def _parse_interval_query(q: str) -> Optional[Dict[str, str]]:
        """
        Parse query string and construct interval query parameters

        Args:
            q: query string

        Returns:
            None or dictionary with following key/values populated:
              query - elasticsearch string query, may be empty string
              chr - chromosome, can be numbers 1-22, X, Y, or MT
              gstart - starting point of genomic range
              gend - ending point of genomic range
            gstart and gend may contain thousands separator and such separators
             may be in the wrong place
        """

        # don't even bother when we don't see chr
        if q.find('chr') < 0:
            return None
        match = re.search(INTERVAL_PATTERN, q)
        if match:
            md = match.groupdict()
            r = {}
            # copy chr
            r['chr'] = md['chr']
            # copy start/end
            if md['gpos']:
                r['gstart'] = r['gend'] = md['gpos']
            else:
                r['gstart'] = md['gstart']
                r['gend'] = md['gend']
            # construct query
            r['query'] = ' AND '.join(
                filter(lambda q: q != '',
                       map(str.strip, filter(
                           None, (
                               md['pre_query_string'],
                               md['post_query_string'],
                           )
                       )))
            )
            return r
        else:
            return None

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
