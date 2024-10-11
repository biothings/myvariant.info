import requests
import json
import time
import glob
import os
import logging
# from utils.hgvs import get_hgvs_from_vcf
from biothings.utils.dataload import unlist, dict_sweep, to_int

# data_folder = "/Users/v/dev/scripps/myvariant.info-copy/src/hub/dataload/sources/civic"

def load_data(data_folder):
    print("##########")
    # number of civic ids with ref, alt, chrom
    no_case1 = 0
    # number of civic ids with chrom, ref, but no alt
    no_case2 = 0
    # number of civic ids with chrom, alt, but no ref
    no_case3 = 0
    # number of civic ids with no alt and ref
    no_case4 = 0
    # for infile in glob.glob(os.path.join(data_folder,"variant_*.json")):
    print(glob.glob(os.path.join(data_folder,"variant_*.json")))
    for infile in glob.glob(os.path.join(data_folder,"variant_*.json")):
        logging.info(infile)
        doc = json.load(open(infile))
        if set(['error', 'status']) != set(doc.keys()):
            [chrom, pos, ref, alt] = [doc['coordinates'][x] for x in ['chromosome', 'start', 'referenceBases', 'variantBases']]
            variant_id = doc.pop("id")
            new_doc = {}
            doc['variant_id'] = variant_id
            if chrom and ref and alt:
                no_case1 += 1
                # try:
                #   new_doc['_id'] = get_hgvs_from_vcf(chrom, pos, ref, alt)
                # except ValueError:
                #   logging.warning("id has ref,alt, but coudn't be converted to hgvs id: {}".format(variant_id))
                #   continue
            # handle cases of deletions where only ref info is provided
            elif chrom and ref and not alt:
                no_case2 += 1
                start = int(pos)
                end = int(pos) + len(ref) - 1
                if start == end:
                    new_doc['_id'] = 'chr{0}:g.{1}del'.format(chrom, start)
                else:
                    new_doc['_id'] = 'chr{0}:g.{1}_{2}del'.format(chrom, start, end)
            # handle cases of insertions where only alt info is provided
            elif chrom and alt and not ref:
                no_case3 += 1
                new_doc['_id'] = 'chr{0}:g.{1}_{2}ins{3}'.format(chrom, start, end, alt)
            # handle cases where no ref or alt info provided,
            # in this case, use CIVIC internal ID as the primary id for MyVariant.info, e.g. CIVIC_VARIANT:1
            else:
                no_case4 += 1
                new_doc['_id'] = 'CIVIC_VARIANT:' + str(variant_id)
            # for _evidence in doc['evidence_items']:
            # print(doc)
            for _molecularProfiles in doc['molecularProfiles']['nodes']:
                # print(_molecularProfiles)
                for _evidence in _molecularProfiles['evidenceItems']['edges']:
                    print(_evidence['node'])
                    if 'disease' in _evidence['node'] and 'doid' in (_evidence['node']['disease'] or {}) and _evidence['node']['disease']['doid']:
                        _evidence['node']['disease']['doid'] = 'DOID:' + _evidence['node']['disease']['doid']
                #     if 'source' in _evidence and 'citation_id' in _evidence['source']:
                #         if _evidence['source']['source_type'] == "PubMed":
                #             _evidence['source']['pubmed'] = to_int(_evidence['source']['citation_id'])
                #             _evidence['source'].pop('source_type')
                #             _evidence['source'].pop('citation_id')
                #         elif _evidence['source']['source_type'] == "ASCO":
                #             _evidence['source']['asco'] = to_int(_evidence['source']['citation_id'])
                #             _evidence['source'].pop('source_type')
                #             _evidence['source'].pop('citation_id')
                #         else:
                #             raise ValueError("The value of source_type is not one of PubMed or ASCO, it's {}, need to restructure parser".format(_evidence['source']['source_type']))
            new_doc['civic'] = doc
            yield dict_sweep(unlist(new_doc), ['', 'null', 'N/A', None, [], {}])
            # change doid into its formal representation, which should be sth like DOID:1
        else:
            continue
    logging.info("number of ids with ref, alt, chrom: {}".format(no_case1))
    logging.info("number of ids with chrom, ref but no alt: {}".format(no_case2))
    logging.info("number of ids with chrom, alt but no ref: {}".format(no_case3))
    logging.info("number of ids with no ref and alt: {}".format(no_case4))
