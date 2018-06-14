# -*- coding: utf-8 -*-
from biothings.web.api.es.transform import ESResultTransformer
import logging

class ESResultTransformer(ESResultTransformer):
    # Add app specific result transformations
    def _modify_doc(self, doc):
        for source, val in self.source_metadata[self.options.assembly].items():
            if source in doc:
                if isinstance(doc[source], dict):
                    try:
                        doc[source]['_license'] = val.get('license_url_short') if val.get('license_url_short', False) else val.get('license_url', '')
                    except:
                        pass
                elif isinstance(doc[source], list):
                    for d in doc[source]:
                        try:
                            d['_license'] = val.get('license_url_short') if val.get('license_url_short', False) else val.get('license_url', '')
                        except:
                            pass                            
        #if 'cadd' in doc:
        #    doc['cadd']['_license'] = 'http://goo.gl/bkpNhq'
        #if 'dbnsfp' in doc:
        #    if 'polyphen2' in doc['dbnsfp']:
        #        doc['dbnsfp']['polyphen2']['_license'] = 'http://goo.gl/6Cz4Ae'
        #    if 'vest3' in doc['dbnsfp']:
        #        doc['dbnsfp']['vest3']['_license'] = 'http://goo.gl/jTko4F'
        #    if 'dann' in doc['dbnsfp']:
        #        doc['dbnsfp']['dann']['_license'] = 'https://goo.gl/IeLhCq'
        return doc
