
def update_stats(idxer,assembly):
    stats = compute_stats(idxer,assembly)
    # now update _meta.stats
    m = idxer.get_mapping_meta()
    m["_meta"].get("stats",{}).update(stats)
    idxer.update_mapping_meta(m)
    return m["_meta"]["stats"]


def compute_stats(idxer,assembly):
    stats = {}
    stats["total"] = idxer.count()
    for k in [assembly,"observed","vcf"]:
        stats[k] = count_field(idxer,k)
    return stats


def count_field(idxer,field):
    q = {"query":{"exists":{"field":field}}}
    return idxer._es.count(idxer._index,idxer._doc_type,q)["count"]

