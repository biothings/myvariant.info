# -*- coding: utf-8 -*-
from biothings.www.api.es import ESQuery
from settings import MyVariantSettings

myvariant_settings = MyVariantSettings()

class ESQuery(ESQuery):
    def __init__(self):
        super( ESQuery, self ).__init__()
        self._jsonld = False    
        self._hg38 = False

    def _get_genome_position_fields(self, hg38=False):
        if hg38:
            return myvariant_settings.hg38_fields()
        else:
            return myvariant_settings.hg19_fields()

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

    def build_interval_query(self, chr, gstart, gend, rquery, hg38, **kwargs):
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

    def get_mapping_meta(self):
        """return the current _meta field."""
        m = self._es.indices.get_mapping(index=self._index, doc_type=self._doc_type)
        m = m[self._index]['mappings'][self._doc_type]
        return m.get('_meta', {})

    def _insert_jsonld(self, k):
        ''' Insert the jsonld links into this document.  Called by _get_variantdoc. '''
        # get the context
        context = self._context

        # set the root
        k.update(context['root'])

        for key in context:
            if key != 'root':
                keys = key.split('/')
                try:
                    doc = find_doc(k, keys)
                    if type(doc) == list:
                        for _d in doc:
                            _d.update(context[key])
                    elif type(doc) == dict:
                        doc.update(context[key])
                    else:
                        continue
                        #print('error')
                except:
                    continue
                    #print('keyerror')
        return k

    def _modify_biothingdoc(self, doc, options):
        if 'cadd' in doc:
            doc['cadd']['_license'] = 'http://goo.gl/bkpNhq'
        if self._jsonld:
            doc = self._insert_jsonld(doc)
        return doc

    def _use_hg38(self):
        self._hg38 = True

    def _use_hg19(self):
        self._hg38 = False

