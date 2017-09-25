import requests
import json
import time
from utils.hgvs import get_hgvs_from_vcf
from biothings.utils.dataload import unlist, dict_sweep


# max internal variant id from civic, currently set to 2000, could change in the future
MAX_VARIANT_NUMBER = 2000

def load_data():
    # number of civic ids with ref, alt, chrom
    no_case1 = 0
    # number of civic ids with chrom, ref, but no alt
    no_case2 = 0
    # number of civic ids with chrom, alt, but no ref
    no_case3 = 0
    # number of civic ids with no alt and ref
    no_case4 = 0
    for variant_id in range(MAX_VARIANT_NUMBER):
        if variant_id % 200 == 0:
            print("scanned {} variants".format(variant_id))
        civic_url = 'https://civic.genome.wustl.edu/api/variants/'
        url = civic_url + str(variant_id)
        doc = requests.get(url).json()
        # time delay for 0.5s
        time.sleep(0.5)
        if set(['error', 'status']) != set(doc.keys()):
            [chrom, pos, ref, alt] = [doc['coordinates'][x] for x in ['chromosome', 'start', 'reference_bases', 'variant_bases']]
            doc.pop("id")
            new_doc = {}
            doc['variant_id'] = variant_id
            if chrom and ref and alt:
                no_case1 += 1
                try:
                  new_doc['_id'] = get_hgvs_from_vcf(chrom, pos, ref, alt)
                except ValueError:
                  print("id has ref,alt, but coudn't be converted to hgvs id: {}".format(variant_id))
                  continue
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
            for _evidence in doc['evidence_items']:
                if 'disease' in _evidence and 'doid' in _evidence['disease'] and _evidence['disease']['doid']:
                    _evidence['disease']['doid'] = 'DOID:' + _evidence['disease']['doid']
            new_doc['civic'] = doc
            yield dict_sweep(unlist(new_doc),['','null', 'N/A', None, [], {}])
            # change doid into its formal representation, which should be sth like DOID:1
        else:
            continue
    print("number of ids with ref, alt, chrom: {}".format(no_case1))
    print("number of ids with chrom, ref but no alt: {}".format(no_case2))
    print("number of ids with chrom, alt but no ref: {}".format(no_case3))
    print("number of ids with no ref and alt: {}".format(no_case4))

