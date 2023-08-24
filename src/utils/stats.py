from biothings.utils.es import ESIndexer
from elasticsearch import Elasticsearch


def update_stats(idxer: ESIndexer, assembly):
    # compute stats
    stats = dict()
    stats["total"] = idxer.count()
    for k in [assembly, "observed", "vcf"]:
        q = {"query": {"exists": {"field": k}}}
        stats[k] = idxer._es.count(index=idxer._index, doc_type=idxer._doc_type, body=q)["count"]

    # now update _meta.stats
    m = idxer.get_mapping_meta()
    m["_meta"].get("stats", {}).update(stats)
    idxer.update_mapping_meta(m)
    return m["_meta"]["stats"]


class ESReleaseException(Exception):
    pass


class ESMappingMetaStatsService:
    REQUIRED_MIN_RELEASE = 7

    def __init__(self, client: Elasticsearch, index_name: str):
        self.client = client
        self.index_name = index_name

        self._check_release(client, self.REQUIRED_MIN_RELEASE)

    @classmethod
    def _check_release(cls, client: Elasticsearch, required_min_release):
        """
        Check if the current ES version is equal to or above the required minimum release.
        E.g. if major release 8 is required, ES version "7.13.4" does not satisfy.
        In this example, "7" is the actual major release, "13" the minor release, and "4" the maintenance release.
        """
        version = client.info()['version']['number']  # a string like "7.13.4"
        release = int(version.split('.')[0])  # an int like 7
        if release < required_min_release:
            raise ESReleaseException(f"Required ES minimum release is {required_min_release}, found version {version} installed.")

    def update_mapping_meta_stats(self, assembly):
        """
        Update the "stats" entry inside the "_meta" field of the index's mapping. Return the updated "meta._stats" field of the mapping.

        Args:
            assembly (str): a string of "hg19" or "hg38"
        """

        """
        With ES7, self.client.indices.get_mapping(index_name) will return a dict like

            {
                "<index_name>": {
                    "mappings": {
                        "_meta": {
                            "build_date": "2021-08-29T15:43:59.554260-07:00",
                            "biothing_type": "variant",
                            "stats": {
                                "total": ...
                                "vcf": ...
                                "observed": ...
                                "<assembly>": ...
                            },
                            "src": {...},
                            "build_version": "20210829"
                        },
                        "properties": {...}
                    }
                }
            }

        The goal here is to update the "stats" field inside.
        """

        stats = dict()
        stats["total"] = self.client.count(index=self.index_name)["count"]
        for field in [assembly, "observed", "vcf"]:
            body = {"query": {"exists": {"field": field}}}
            stats[field] = self.client.count(index=self.index_name, body=body)["count"]

        mapping = self.client.indices.get_mapping(index=self.index_name)
        meta = mapping[self.index_name]["mappings"]["_meta"]  # Get the current meta field from mapping
        meta.get("stats", {}).update(stats)  # Update the meta content
        self.client.indices.put_mapping(body={"_meta": meta}, index=self.index_name)  # Write the modified meta to ES mapping

        return meta["stats"]


class BuildDocMetaStatsService:
    def __init__(self, src_build, build_name: str, logger=None):
        self.src_build = src_build
        self.build_name = build_name
        self.logger = logger

    def update_build_meta_stats(self, meta_stats):
        """
        Update the "stats" entry inside the "_meta" field of the build doc. Return the updated "meta._stats" field of the build_doc.
        """
        build_doc = self.src_build.find_one({"_id": self.build_name})

        if self.logger:
            self.logger.info(f"_meta.stats of document {self.build_name} is {build_doc['_meta']['stats']} in collection {self.src_build.full_name} "
                             f"before post-index")

        build_doc["_meta"].get("stats", {}).update(meta_stats)

        result = self.src_build.replace_one({"_id": self.build_name}, build_doc)
        if result.matched_count != 1:
            raise ValueError(f"cannot find document {self.build_name} in collection {self.src_build.full_name}")
        if result.modified_count != 1:
            raise ValueError(f"failed to update _meta.stats in document {self.build_name} in collection {self.src_build.full_name}")

        if self.logger:
            self.logger.info(f"_meta.stats of document {self.build_name} is updated to {meta_stats} in collection {self.src_build.full_name} "
                             f"during post-index")

        return build_doc["_meta"]["stats"]
