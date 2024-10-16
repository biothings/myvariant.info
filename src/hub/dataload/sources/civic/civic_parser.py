import requests
import json
import time
import glob
import os
import logging
from utils.hgvs import get_hgvs_from_vcf
from biothings.utils.dataload import unlist, dict_sweep, to_int


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
            _id = 'CIVIC_VARIANT:' + str(doc["variant_id"])
            return _id
    except Exception as e:
        logging.error(e)
        _id = 'CIVIC_VARIANT:' + str(doc["variant_id"])
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

        # if set(['error', 'status']) != set(doc.keys()):
        #     print("### doc")
        #     print(doc)
        #     [chrom, pos, ref, alt] = [doc['coordinates'][x] for x in ['chromosome', 'start', 'referenceBases', 'variantBases']]
        #     variant_id = doc.pop("id")
        #     new_doc = {}
        #     doc['variant_id'] = variant_id
        #     if chrom and ref and alt:
        #         no_case1 += 1
        #         try:
        #             new_doc['_id'] = get_hgvs_from_vcf(chrom, pos, ref, alt)
        #         except ValueError:
        #             logging.warning("id has ref,alt, but coudn't be converted to hgvs id: {}".format(variant_id))
        #             continue
        #     # handle cases of deletions where only ref info is provided
        #     elif chrom and ref and not alt:
        #         no_case2 += 1
        #         start = int(pos)
        #         end = int(pos) + len(ref) - 1
        #         if start == end:
        #             new_doc['_id'] = 'chr{0}:g.{1}del'.format(chrom, start)
        #         else:
        #             new_doc['_id'] = 'chr{0}:g.{1}_{2}del'.format(chrom, start, end)
        #     # handle cases of insertions where only alt info is provided
        #     elif chrom and alt and not ref:
        #         no_case3 += 1
        #         new_doc['_id'] = 'chr{0}:g.{1}_{2}ins{3}'.format(chrom, start, end, alt)
        #     # handle cases where no ref or alt info provided,
        #     # in this case, use CIVIC internal ID as the primary id for MyVariant.info, e.g. CIVIC_VARIANT:1
        #     else:
        #         no_case4 += 1
        #         new_doc['_id'] = 'CIVIC_VARIANT:' + str(variant_id)
        #     # for _evidence in doc['evidence_items']:
        #     # print(doc)

        for _molecularProfiles in doc['molecularProfiles']['nodes']:
            # print(_molecularProfiles)
            for _evidence in _molecularProfiles['evidenceItems']['edges']:
                # print(_evidence['node'])
                if 'disease' in _evidence['node'] and 'doid' in (_evidence['node']['disease'] or {}) and _evidence['node']['disease']['doid']:
                    _evidence['node']['disease']['doid'] = 'DOID:' + _evidence['node']['disease']['doid']
                if 'source' in _evidence['node'] and 'citationId' in _evidence['node']['source']:
                    if _evidence['node']['source']['sourceType'].lower() == "pubmed":
                        _evidence['node']['source']['pubmed'] = to_int(_evidence['node']['source']['citationId'])
                        _evidence['node']['source'].pop('sourceType')
                        _evidence['node']['source'].pop('citationId')
                    elif _evidence['node']['source']['sourceType'].lower() == "asco":
                        _evidence['node']['source']['asco'] = to_int(_evidence['node']['source']['citationId'])
                        _evidence['node']['source'].pop('sourceType')
                        _evidence['node']['source'].pop('citationId')
                    else:
                        raise ValueError("The value of source_type is not one of PubMed or ASCO, it's {}, need to restructure parser".format(_evidence['node']['source']['sourceType']))
        new_doc["civic"] = doc
        new_doc["civic"].pop("myVariantInfo")
        print("### new_doc")
        print(new_doc)
        yield dict_sweep(unlist(new_doc), ['', 'null', 'N/A', None, [], {}])

        # change doid into its formal representation, which should be sth like DOID:1
        # else:
        #     continue
    logging.info("number of ids with ref, alt, chrom: {}".format(no_case1))
    logging.info("number of ids with chrom, ref but no alt: {}".format(no_case2))
    logging.info("number of ids with chrom, alt but no ref: {}".format(no_case3))
    logging.info("number of ids with no ref and alt: {}".format(no_case4))
