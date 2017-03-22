import biothings.dataindex.indexer as indexer


class VariantIndexer(indexer.Indexer):

    def get_mapping(self, enable_timestamp=True):
        mapping = super(VariantIndexer,self).get_mapping(enable_timestamp=enable_timestamp)
        # enrich with myvariant specific stuff
        mapping["dynamic"] = False
        mapping["include_in_all"] = False
        mapping["properties"]["chrom"] = {
            'analyzer': 'string_lowercase',
            'include_in_all': False,
            'type': 'string'}
        mapping["properties"]["observed"] = {
            "type": "boolean",
            'include_in_all': False}

        return mapping

    def get_index_creation_settings(self):
        return {"codec" : "best_compression"}
