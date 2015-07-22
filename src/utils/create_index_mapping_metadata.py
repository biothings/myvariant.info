''' This program will create a JSON object from the elasticsearch index
metadata. '''
import argparse
import os
import sys
from elasticsearch import Elasticsearch
import json

EXAMPLES = {'evs': '"chr5:g.126147533G>A"',
            'cadd': '"chr5:g.126141367T>A"',
            'wellderly': '"chr2:g.208133534G>C"',
            'dbnsfp': '"chr5:g.126141367T>A"',
            'snpedia': '"chr7:g.117199646->CTT"',
            'clinvar': '"chr19:g.36332612C>T"',
            'docm': '"chr10:g.89692991A>T"',
            'mutdb': '"chr13:g.88329134G>T"',
            'cosmic': '"chr13:g.24167556C>T"',
            'dbsnp': '"chr5:g.126147533G>A"',
            'emv': '"chr2:g.179634392A>T"',
            'gwassnps': '"chr1:g.117038287T>C"'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-host", "--hostaddress", required=True, help="Elasticsearch host address, e.g., localhost:9200")
    parser.add_argument("-o", "--output", required=True, help="Path for JSON output")
    args = parser.parse_args()

    es = Elasticsearch(args.hostaddress)
    r = es.indices.get(index='myvariant_current')
    mapping_dict = r[list(r.keys())[0]]['mappings']['variant']['properties']

    def get_indexed_properties_in_dict(d, prefix):
        r = {}
        for (k, v) in d.items():
            if type(v) is dict:
                if 'type' in v:
                    r[prefix + '.' + k] = {}
                    r[prefix + '.' + k]['type'] = v['type']
                    if ('index' not in v) or ('index' in v and v['index'] != 'no'):
                        r[prefix + '.' + k]['indexed'] = True
                        r[prefix + '.' + k]['example'] = 'q=_exists_:' + prefix.lstrip('.') + '.' + k + '&fields=' + prefix.lstrip('.') + '.' + k
                    else:
                        r[prefix + '.' + k]['indexed'] = False
                        db_type = prefix.lstrip('.').split('.')[0]
                        r[prefix + '.' + k]['example'] = 'q=_id:' + EXAMPLES[db_type] + '&fields=' + prefix.lstrip('.') + '.' + k
                elif 'properties' in v:
                        r.update(get_indexed_properties_in_dict(v['properties'], prefix + '.' + k))
        return r

    # get the dictionary, strip the leading . from the key names, and write the output
    r = get_indexed_properties_in_dict(mapping_dict, '')
    r = dict([(k.lstrip('.'), v) for (k, v) in r.items()])
    print(r)
    with open(os.path.abspath(args.output), 'w') as outfile:
        json.dump(r, outfile)

    return 0


if __name__ == "__main__":
    sys.exit(main())
