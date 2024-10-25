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


def remove_nodes_and_edges(data):
    if "civic" in data and "molecularProfiles" in data["civic"]:
        molecular_profiles = data["civic"]["molecularProfiles"]["nodes"]
        for profile in molecular_profiles:
            if "evidenceItems" in profile and "edges" in profile["evidenceItems"]:
                profile["evidenceItems"] = [edge["node"] for edge in profile["evidenceItems"]["edges"]]
        data["civic"]["molecularProfiles"] = molecular_profiles
    return data


# number of civic ids from MyVariantInfo
no_case1 = 0
# number of civic ids from CivicDB.org
no_case2 = 0
# number of civic ids not found
no_case3 = 0
# number of civic ids created by exception
no_case4 = 0


def get_id(doc):
    global no_case1
    global no_case2
    global no_case3
    global no_case4
    try:
        if "myVariantInfo" in doc and "myVariantInfoId" in doc["myVariantInfo"]:
            _id = doc["myVariantInfo"]["myVariantInfoId"]
            no_case1 = no_case1 + 1
            return _id
        elif "hgvsDescriptions" in doc:
            hgvs_description = doc["hgvsDescriptions"]
            hgvs_nc_item = hgvs_description[0].split(":")
            nc_id = hgvs_nc_item[0].replace("NC_", "").split(".")[0].lstrip('0')
            _id = nc_id + hgvs_nc_item[1]
            no_case2 = no_case2 + 1
            return _id
        else:
            _id = 'CIVIC_VARIANT:' + str(doc["id"])
            no_case3 = no_case3 + 1
            return _id
    except Exception as e:
        logging.error(e)
        _id = 'CIVIC_VARIANT:' + str(doc["id"])
        no_case4 = no_case4 + 1
        return _id


def load_data(data_folder):
    for infile in glob.glob(os.path.join(data_folder,"variant_*.json")):
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
        # new_doc["civic"]["molecularProfiles"] = new_doc["civic"]["molecularProfiles"]["nodes"]
        yield dict_sweep(unlist(new_doc), ['', 'null', 'N/A', None, [], {}])

    logging.info("number of civic ids from MyVariantInfo: {}".format(no_case1))
    logging.info("number of civic ids from CivicDB.org: {}".format(no_case2))
    logging.info("number of civic ids not found: {}".format(no_case3))
    logging.info("number of civic ids created by exception: {}".format(no_case4))
