

from __future__ import print_function
import re

from bitarray import bitarray

import utils.common
import utils.mongo
from config import HG19_DATAFILE

# encode nucleotide into bit form


def nuc_to_bit(sequence):
    code = {'A': bitarray('001'),
            'C': bitarray('010'),
            'G': bitarray('011'),
            'T': bitarray('100'),
            'g': bitarray('011'),
            't': bitarray('100'),
            'a': bitarray('001'),
            'c': bitarray('010'),
            'N': bitarray('101'),
            'M': bitarray('110'),
            'R': bitarray('111')}
    seq_bit = bitarray()
    seq_bit.encode(code, sequence)
    return(seq_bit)

# encode bit form to nucleotide


def bit_to_nuc(sequence):
    if sequence == bitarray('001'):
        nuc = 'A'
    elif sequence == bitarray('010'):
        nuc = 'C'
    elif sequence == bitarray('011'):
        nuc = 'G'
    elif sequence == bitarray('100'):
        nuc = 'T'
    return nuc

'''parse variant name, print the variant name and
    return chromosome number, nucleotide position
    and nucleotide name
    '''


def parse(str):
    pat = 'chr(\w+):g\.(\d+)(\w)\>(\w)'
    mat = re.match(pat, str)
    if mat:
        r = mat.groups()
        return (r[0], r[1], r[2])


class VariantValidator:
    def __init__(self):
        self.data = None

    # validate single hgvs variant name  document
    def validate_hgvs(self, hgvs_id):
        r = parse(hgvs_id)
        if r:
            # get the chromosome sequence in bit form
            if self.data is None:
                self.data = utils.common.loadobj(HG19_DATAFILE)
            chr_bit = bitarray()
            if r[0] == 'M':
                chr = 'MT'
            else:
                chr = r[0]
            chr_bit = self.data[str(chr)]

            # get the nucleotide in chromsome sequence in bit form
            nuc_chr_bit = bitarray()
            nuc_chr_bit = chr_bit[int(r[1])*3-3:int(r[1])*3]
            nuc_chr = bit_to_nuc(nuc_chr_bit)

            # compare HGVS id with genome
            return r[2] == nuc_chr
        else:
            return None

    # validate multiple hgvs variant name
    def validate_many(self, *args):
        for item in args:
            print(self.validate_hgvs(item))

    def validate_src(self, collection, return_False=False,
                     return_None=False, return_True=False):
        return_dic = {False: return_False, True: return_True,
                      None: return_None}

        # read in the collection from mongodb
        src = utils.mongo.get_src_db()
        cursor = utils.mongo.doc_feeder(src[collection], step=10000)

        print_only = not (return_False or return_None or return_True)
        if not print_only:
            # output dictionary, three keys: 'false','true','none'
            out = {}
            for k in return_dic:
                if return_dic[k]:
                    out[k] = []

        # initialize the count
        cnt_d = {True: 0, False: 0, None: 0}    # cnt_d
        # validate each item in the cursor
        for item in cursor:
            _id = item['_id']
            valid = self.validate_hgvs(_id)
            print(_id, valid)
            cnt_d[valid] += 1
            if return_dic[valid]:
                out[valid].append(_id)

        # print out counts
        print("The number of False HGVS IDs in the collection \
is : {0}".format(cnt_d[False]))
        print("The number of True HGVS IDs in the collection \
is : {0}".format(cnt_d[True]))
        print("The number of HGVS IDs that could not be identified by \
parser in the collection is : {0}".format(cnt_d[None]))

        # print out the HGVS IDs as user defined
        if not print_only:
            return out
