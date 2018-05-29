import unicodedata
from collections import defaultdict

from csv import DictReader
from biothings.utils.dataload import dict_sweep, open_anyfile


def load_data(input_file):

    with open_anyfile(input_file) as in_f:
        for line in in_f:
            _id,caid = line.strip().split()
            yield {
                '_id': _id,
                'clingen' : {"caid" : caid},
            }
