import os
import re
import csv
from itertools import groupby
try:
    import itertools.imap as map
except ImportError:
    pass
try:
    import itertools.ifilter as filter
except ImportError:
    pass

from utils.dataload import dict_sweep, value_convert, unlist, merge_duplicate_rows

#  merge EMV file with genomic ID file
# def file_merge(emv_file, id_file):
#    os.system("cut -f3 genomic_id.txt > genomic_id3.txt")
#    os.system("paste -d"," genomic_id3.txt EmVClass.2014-3.csv > emv.csv")

VALID_COLUMN_NO = 11


# convert one snp to json
def _map_line_to_json(fields):
    vid = fields[0].split(":")
    chrom = re.search(r'[1-9]+', vid[0]).group()

    if chrom == '23':
        chrom = chrom.replace('23', 'X')
    HGVS = "chr%s:%s" % (chrom, vid[1])
    # load as json data
    if HGVS is None:
        return

    one_snp_json = {
        "_id": HGVS,
        "emv": {
            "gene": fields[2],
            "variant_id": fields[3],
            "exon": fields[4],
            "egl_variant": fields[5],
            "egl_protein": fields[6],
            "egl_classification": fields[7],
            "egl_classification_date": fields[8],
            "hgvs": fields[9].split(" | "),
            "clinvar_rcv": fields[10],
        }
    }

    return unlist(dict_sweep(value_convert(one_snp_json), vals=[""]))


# open file, parse, pass to json mapper
def data_generator(input_file):
    # sort by the first column (hgvs id returned from Mutalyzer)
    os.system("sort -k1 -n %s > %s.sorted" % (input_file, input_file))
    open_file = open("%s.sorted" % (input_file))
    emv = csv.reader(open_file, delimiter=",")
    # Skip header
    emv.next()
    emv = filter(lambda x: x[0], emv)
    json_rows = map(_map_line_to_json, emv)
    row_groups = (it for (key, it) in groupby(json_rows, lambda row: row["_id"]))
    return (merge_duplicate_rows(rg, "emv") for rg in row_groups)


# load path and find files, pass to data_generator
def load_data(path):
    print(path)
    for one_snp_json in data_generator(path):
        yield one_snp_json
