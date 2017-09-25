from biothings.web.settings import BiothingESWebSettings

class MyVariantWebSettings(BiothingESWebSettings):
    # Add app-specific settings functions here
    def _source_metadata_object(self):
        _meta = {}
        for assembly in self.SUPPORTED_ASSEMBLIES:
            try:
                _m = self.es_client.indices.get_mapping(index=self.ES_INDEX_BASE + '_' + assembly, doc_type=self.ES_DOC_TYPE)
                _meta[assembly] = _m[list(_m.keys())[0]]['mappings'][self.ES_DOC_TYPE]['_meta']['src']
            except:
                _meta[assembly] = {}
        return _meta
