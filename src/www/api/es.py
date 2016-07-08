# -*- coding: utf-8 -*-
import re
import json
from biothings.www.api.es import ESQuery, ESQueryBuilder
from biothings.utils.common import dotdict
from settings import MyVariantSettings

myvariant_settings = MyVariantSettings()

class ESQuery(ESQuery):
    def index_name(self, assembly):
        ''' Return the variant index name given the assembly.  Assumes indices are named:  Index1_assembly1, Index1_assembly2, etc.'''
        return '_'.join([myvariant_settings.es_index_base, assembly])

    def _parse_interval_query(self, q):
        interval_pattern = r'(?P<pre_query>.+(?P<pre_and>[Aa][Nn][Dd]))*(?P<interval>\s*chr(?P<chr>[1-9xXyYmM][0-9tT]?):(?P<gstart>[0-9,]+)-(?P<gend>[0-9,]+)\s*)(?P<post_query>(?P<post_and>[Aa][Nn][Dd]).+)*'
        single_pattern = r'(?P<pre_query>.+(?P<pre_and>[Aa][Nn][Dd]))*(?P<interval>\s*chr(?P<chr>[1-9xXyYmM][0-9tT]?):(?P<gend>(?P<gstart>[0-9,]+))\s*)(?P<post_query>(?P<post_and>[Aa][Nn][Dd]).+)*'
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

    def _modify_biothingdoc(self, doc, options):
        if 'cadd' in doc:
            doc['cadd']['_license'] = 'http://goo.gl/bkpNhq'
        return doc

    def _get_options(self, options, kwargs):
        this_assembly = kwargs.pop('assembly', myvariant_settings.default_assembly).lower()
        options.assembly = this_assembly if this_assembly in myvariant_settings.supported_assemblies else myvariant_settings.default_assembly
        return options

    def _get_cleaned_metadata_options(self, kwargs):
        options = dotdict()
        this_assembly = kwargs.pop('assembly', myvariant_settings.default_assembly).lower()
        options.assembly = this_assembly if this_assembly in myvariant_settings.supported_assemblies else myvariant_settings.default_assembly
        options.chromosome = kwargs.pop('chromosome', False)
        for key in set(kwargs.keys()):
            del(kwargs[key])
        kwargs = {}
        return options

    def _get(self, **kwargs):
        options = kwargs.pop('options', {})
        kwargs['index'] = self.index_name(options.assembly)
        return self._es.get(**kwargs)

    def _msearch(self, **kwargs):
        options = kwargs.pop('options', {})
        kwargs['index'] = self.index_name(options.assembly)
        return self._es.msearch(**kwargs)['responses']

    def _search(self, q, **kwargs):
        # For /query GET
        options = kwargs.pop('options', {})
        return self._es.search(index=self.index_name(options.assembly), 
                doc_type=self._doc_type, body=q, **kwargs)

    def get_chromosome_aggs(self, **kwargs):
        kwargs.update({"body": {"query": {"match_all": {}}, "aggs": {"chromosomes": {"terms": {"field": "chrom", "size": 50}}}}})
        r = self._es.search(**kwargs)
        return r.get('aggregations', {})

    def get_mapping_meta(self, **kwargs):
        ''' get metadata, overridden from biothings to add chromosome aggs.'''
        options = self._get_cleaned_metadata_options(kwargs)
        m = self._es.indices.get_mapping(index=self.index_name(options.assembly), doc_type=self._doc_type,
                **kwargs)
        m = m[list(m.keys())[0]]['mappings'][self._doc_type]
        r = m.get('_meta', {})
        if options.chromosome:
            r.update(self.get_chromosome_aggs(index=self.index_name(options.assembly), doc_type=self._doc_type))
        return r

    def _get_fields(self, **kwargs):
        # for /metadata/fields
        options = kwargs.pop('options', {})
        kwargs['index'] = self.index_name(options.assembly)
        return self._es.indices.get(**kwargs)

    def _build_query(self, q, **kwargs):
        # overriding to implement interval query
        esqb = ESQueryBuilder(**kwargs)
        interval_query = self._parse_interval_query(q)
        if interval_query:
            return esqb.build_interval_query(chr=interval_query["chr"],
                                              gstart=interval_query["gstart"],
                                              gend=interval_query["gend"],
                                              rquery=interval_query["query"])
        return esqb.default_query(q)
    
class ESQueryBuilder(ESQueryBuilder):
    def build_interval_query(self, chr, gstart, gend, rquery):
        """ Build an interval query - called by the ESQuery.query method. """
        options = self._query_options.get('options', {})
        if chr.lower().startswith('chr'):
            chr = chr[3:]
        _query = {
            "query": {
                "bool": {
                    "filter": {
                        "bool": {
                            "must": [
                                        {
                                            "term": {"chrom": chr.lower()}    
                                        },
                                        {
                                            "range": {options.assembly + ".start": {"lte": gend}}
                                        },
                                        {
                                            "range": {options.assembly + ".end": {"gte": gstart}}
                                        }
                                    ]
                        }
                    }
                }
            }
        }
        if rquery:
            _query["query"]["bool"]["must"] = {"query_string": {"query": rquery}}
        return _query
