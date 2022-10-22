from elasticsearch import Elasticsearch


class ElasticsearchVersionException(Exception):
    def __init__(self, required: str, installed: str):
        self.required_version = required
        self.installed_version = installed

        message = f"Required Elasticsearch version {self.required_version}. Found version {self.installed_version} installed."
        super.__init__(message)


class ElasticsearchIndexingService:
    def __init__(self, client: Elasticsearch, index_name: str):
        self.client = client
        self.index_name = index_name

        version_str = self.client.info()['version']['number']  # a string like "7.13.4"
        version_num = int(version_str.split('.')[0])  # an int like 7
        if version_num < 7:
            raise ElasticsearchVersionException(required=">= 7", installed=version_str)

    def count_total(self):
        return self.client.count(index=self.index_name)["count"]

    def count_existing_field(self, field):
        body = {"query": {"exists": {"field": field}}}
        return self.client.count(index=self.index_name, body=body)["count"]

    def update_mapping_meta_stats(self, assembly):
        """
        Update the "stats" entry inside "_meta" of the index's mapping. Typically there are 4 fields inside the "stats" entry, and its structure is illustrated
        below.

        {
            "<index_name>": {
                "mappings": {
                    "_meta": {
                        "stats": {
                            "total": ...
                            "vcf": ...
                            "observed": ...
                            "<assembly>": ...
                        },
                    },
                    "properties": {...}
                }
            }
        }

        Args:
            assembly (str): a string of "hg19" or "hg38"
        """

        stats_dict = dict()
        stats_dict["total"] = self.count_total()

        fields = [assembly, "observed", "vcf"]
        for field in fields:
            stats_dict[field] = self.count_existing_field(field=field)

        meta_dict = self.get_mapping_meta()
        meta_dict.get("stats", {}).update(stats_dict)

        self.set_mapping_meta(meta=meta_dict)

        return meta_dict["stats"]

    def get_mapping(self) -> dict:
        """
        return the current index mapping

        With ES7, self.client.indices.get_mapping(index_name) will return a dict like

        {
            "<index_name>": {
                "mappings": {
                    "_meta": {
                        "build_date": "2021-08-29T15:43:59.554260-07:00",
                        "biothing_type": "variant",
                        "stats": {...},
                        "src": {...},
                        "build_version": "20210829"
                    },
                    "properties": {...}
                }
            }
        }

        With ES6, self.client.indices.get_mapping(index_name, doc_type, include_type_name=True) will return a dict like

        {
            "<index_name>": {
                "mappings": {
                    "<doc_type>": {
                        "_meta": {
                            "build_date": "2021-08-29T15:43:59.554260-07:00",
                            "biothing_type": "variant",
                            "stats": {...},
                            "src": {...},
                            "build_version": "20210829"
                        },
                        "properties": {...}
                    }
                }
            }
        }
        """
        mapping = self.client.indices.get_mapping(index=self.index_name)
        return mapping[self.index_name]["mappings"]

    def get_mapping_meta(self) -> dict:
        mapping_dict = self.get_mapping()
        return mapping_dict["_meta"]

    def set_mapping_meta(self, meta):
        body = {"_meta": meta}
        return self.client.indices.put_mapping(body=body, index=self.index_name)
