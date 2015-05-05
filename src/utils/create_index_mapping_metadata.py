''' This program will create a JSON object from the elasticsearch index
metadata. '''
import argparse
import os
import sys
from elasticsearch import Elasticsearch
import json


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
                if 'type' in v and ('index' not in v or ('index' in v and v['index'] != 'no')):
                    r[prefix + '.' + k] = v['type']
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
