from biothings.utils.es import ESIndexer


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
