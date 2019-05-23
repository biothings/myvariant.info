import os
import requests
from collections import defaultdict

from biothings.utils.dataload import dict_sweep, value_convert_to_number, unlist, open_anyfile


class DictQuery(dict):
    """Parse nested dictionary
    """
    def get(self, path, default=None):
        """Extract value from dictionary based on path
        """
        keys = path.split("/")
        val = None

        for key in keys:
            if val:
                if isinstance(val, list):
                    val = [v.get(key, default) if v else None for v in val]
                else:
                    val = val.get(key, default)
            else:
                val = dict.get(self, key, default)

            if not val:
                break
        return val


def batch_query_myvariant_id_from_clingen(hgvs_ids, assembly):
    """Query ClinGen to get myvariant IDs for all input non genomic hgvs IDs

    Keyword arguments:
    hgvs_ids -- list of non genomic hgvs IDs
    assembly -- genomic assembly, either hg19 or hg38
    """
    def parse_myvariant_ids(doc, assembly):
        """Parse the results from clingen to retrieve myvariant id

        Keyword arguments:
        doc -- doc retrieved from clingen
        """
        ASSEMBLY_MAPPING = {
            "hg19": "MyVariantInfo_hg19",
            "hg38": "MyVariantInfo_hg38"
        }
        extract_path = 'externalRecords/' + ASSEMBLY_MAPPING[assembly]
        res = DictQuery(doc).get(extract_path)
        if res:
            return [_doc['id'] for _doc in res if _doc]
        else:
            return []

    hgvs_dict = {}
    hgvs_ids = list(set(hgvs_ids))
    print('total hgvs ids to process is: {}'.format(len(hgvs_ids)))
    for i in range(0, len(hgvs_ids), 1000):
        print('currently processing {}th variant'.format(i))
        if i + 1000 <= len(hgvs_ids):
            batch = hgvs_ids[i: i + 1000]
        else:
            batch = hgvs_ids[i:]
        data = '\n'.join(batch)
        res = requests.post('http://reg.genome.network/alleles?file=hgvs',
                            data=data,
                            headers={'content-type': "text/plain"}).json()
        # loop through clingen results and input hgvs id in parallel
        # construct a mapping dictionary with key as input hgvs id
        # and value as myvariant hgvs id
        for _doc, _id in zip(res, batch):
            hgvs_dict[_id] = parse_myvariant_ids(_doc, assembly)
    return hgvs_dict


def _map_line_to_json(fields):
    """Mapping each lines in csv file into JSON doc
    """
    one_snp_json = {
        "gene": fields[1],
        "variant_id": fields[2],
        "exon": fields[3],
        "egl_variant": fields[4],
        "egl_protein": fields[5],
        "egl_classification": fields[6],
        "egl_classification_date": fields[7],
        "hgvs": fields[8].split(" | ")
    }

    return unlist(dict_sweep(value_convert_to_number(one_snp_json), vals=[""]))


def load_data(data_folder, assembly="hg19"):
    """Load data from EMV csv file into list of JSON docs
    """
    input_file = os.path.join(data_folder, "EmVClass.2018-Q2.csv")
    assert os.path.exists(input_file), "Can't find input file '%s'" % input_file
    with open_anyfile(input_file) as in_f:
        lines = set(list(in_f))
        lines = [_doc.strip().split(',') for _doc in lines]
        results = defaultdict(list)
        # mapping non genomic hgvs ids to genomic hgvs ids used in MyVariant
        hgvs_ids = [_item[4] for _item in lines]
        hgvs_mapping_dict = batch_query_myvariant_id_from_clingen(hgvs_ids, assembly)
        # loop through csv doc to convert into json docs
        for row in lines:
            # structure the content of emv docs
            variant = _map_line_to_json(row)
            # fetch corresponding genomic hgvs ids
            mapped_ids = hgvs_mapping_dict[row[4]]
            # could be one non-genomic hgvs id mapping to mulitple genomic ones
            if mapped_ids:
                for _id in mapped_ids:
                    results[_id].append(variant)
        for k, v in results.items():
            if len(v) == 1:
                doc = {'_id': k, 'emv': v[0]}
            else:
                doc = {'_id': k, 'emv': [_doc for _doc in v]}
            yield doc
