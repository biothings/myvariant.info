import re
from typing import Dict, Optional

from elasticsearch_dsl import Search
from biothings.web.query import ESQueryBuilder, AsyncESQueryBackend


INTERVAL_PATTERN = re.compile(
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
    def _parse_interval_query(q: str) -> Optional[Dict[str, str]]:
        """
        Parse query string and extract appropriate genome interval query

        If the query string includes a valid genome interval/position query,
        such information is extracted, along with other parts of the string
        query. Using [] to denote optional parts and <> for required parts,
        such queries looks like this:
            [query string AND ] chr<Chromosome>:<start>-<end> [AND query string]
            [query string AND ] chr<Chromosome>:<position> [AND query string]

        If the query string is not of this format, None is returned. If a
        valid interval query is found, a dictionary is returned with the keys
        'chr', 'gstart', 'gend', and 'query'.

        Args:
            q: input query string
        Returns:
            None: if input query string is not a valid interval query
            Dict[str, str]: with the following keys
                'chr': Chromosome identifier: 1-22, X, Y, MT
                'gstart': start position of gene
                'gend': end position of gene
                'query': other parts of the query string, concatenated with AND
        """
        # don't even bother when we don't see chr
        # even with improved regex, this is a few times faster
        start_pos = q.find('chr')  # find first occurrence of 'chr'
        # might not be what we're looking for, but usually discards enough
        # so the regex engine runs less
        if start_pos < 0:
            return None
        m = re.search(INTERVAL_PATTERN, q[start_pos:])
        if not m:
            return None
        start_pos += m.start()  # add real offset
        pre_query = q[:start_pos].strip()
        query = []
        if pre_query != '':
            # pre_query non empty and does not end in AND\s+
            if not q[start_pos - 1].isspace():
                return None
            if pre_query[-3:].upper() != 'AND':
                return None
            query.append(f'({pre_query[:-3]})')  # strip the AND, add parenthesis
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
        if md['post_query_string']:
            query.append(f"({md['post_query_string']})")
        r['query'] = ' AND '.join(query)
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
