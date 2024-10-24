import json
import glob
import os
import logging
from biothings.utils.dataload import unlist, dict_sweep


def merge_dicts(d1, d2):
    merged = d1.copy()
    for key, value in d2.items():
        if key in merged:
            if isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = merge_dicts(merged[key], value)
            elif isinstance(merged[key], list) and isinstance(value, list):
                merged[key] = merged[key] + value  # Concatenate lists
            else:
                merged[key] = value  # Overwrite value
        else:
            merged[key] = value
    return merged


def remove_nodes_and_edges(obj):
    if not obj or type(obj) in [str, bool, int, float]:
        return obj

    if isinstance(obj, list):
        return [remove_nodes_and_edges(item) for item in obj]

    if 'edges' in obj:
        return [remove_nodes_and_edges(edge['node']) for edge in obj['edges']]

    if 'nodes' in obj:
        return [remove_nodes_and_edges(node) for node in obj['nodes']]
    return {
        key: remove_nodes_and_edges(value)
        for key, value in obj.items()
        if key != 'node'
    }


def get_id(doc):
    try:
        if "myVariantInfo" in doc and "myVariantInfoId" in doc["myVariantInfo"]:
            _id = doc["myVariantInfo"]["myVariantInfoId"]
            return _id
        elif "hgvsDescriptions" in doc:
            hgvs_description = doc["hgvsDescriptions"]
            hgvs_nc_item = hgvs_description[0].split(":")
            nc_id = hgvs_nc_item[0].replace("NC_", "").split(".")[0].lstrip('0')
            _id = nc_id + hgvs_nc_item[1]
            return _id
        else:
            _id = 'CIVIC_VARIANT:' + str(doc["id"])
            return _id
    except Exception as e:
        logging.error(e)
        _id = 'CIVIC_VARIANT:' + str(doc["id"])
        return _id


def load_data(data_folder):
    # number of civic ids with ref, alt, chrom
    no_case1 = 0
    # number of civic ids with chrom, ref, but no alt
    no_case2 = 0
    # number of civic ids with chrom, alt, but no ref
    no_case3 = 0
    # number of civic ids with no alt and ref
    no_case4 = 0
    # for infile in glob.glob(os.path.join(data_folder,"variant_*.json")):
    # print(glob.glob(os.path.join(data_folder,"variant_*.json")))
    for infile in glob.glob(os.path.join(data_folder,"variant_*.json")):
        # logging.info(infile)
        variant_data = json.load(open(infile))

        doc = {}
        doc = merge_dicts(doc, variant_data["ContributorAvatars"]["data"])
        doc = merge_dicts(doc, variant_data["GeneVariant"]["data"]["variant"])
        doc = merge_dicts(doc, variant_data["VariantDetail"]["data"]["variant"])
        doc = merge_dicts(doc, variant_data["VariantSummary"]["data"]["variant"])

        new_doc = {}
        new_doc["_id"] = get_id(doc=doc)
        new_doc["civic"] = doc
        if "myVariantInfo" in new_doc["civic"]:
            new_doc["civic"].pop("myVariantInfo")
        new_doc = remove_nodes_and_edges(new_doc)
        new_doc["civic"]["molecularProfiles"] = new_doc["civic"]["molecularProfiles"]["nodes"]
        yield dict_sweep(unlist(new_doc), ['', 'null', 'N/A', None, [], {}])

    logging.info("number of ids with ref, alt, chrom: {}".format(no_case1))
    logging.info("number of ids with chrom, ref but no alt: {}".format(no_case2))
    logging.info("number of ids with chrom, alt but no ref: {}".format(no_case3))
    logging.info("number of ids with no ref and alt: {}".format(no_case4))
