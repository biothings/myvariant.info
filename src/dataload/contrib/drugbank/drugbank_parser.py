# -*- coding: utf-8 -*-
from itertools import imap, groupby
from utils.dataload import dict_sweep, merge_duplicate_rows
import csv


VALID_CO_NUMBER = 8


def _map_line_to_json(fields):
    assert len(fields) == VALID_CO_NUMBER

    HGVS = fields[1]
    if HGVS is None:
        return
    one_snp_json = {
        "_id": HGVS,
        'drugbank':
            {
                'drug': fields[2],
                'interacting_gene_or_enzyme': fields[3],
                'snp_rs_id': fields[0],
                'allele_name': fields[4],
                'defining_change': fields[5],
                'adverse_reaction': fields[6],
                'references': fields[7]
            }
    }
    return dict_sweep(one_snp_json, ['Not Available'])


def load_data(input_file):
    """
    write_file output and csv.reader input_file
    '/opt/myvariant.info/load_archive/drugbank/drugbank.csv'
    """
    open_file = open(input_file)
    drugbank = csv.reader(open_file, delimiter=',')
    drugbank.next()
    json_rows = imap(_map_line_to_json, drugbank)
    row_groups = (it for (key, it) in groupby(json_rows, lambda row: row['_id']))
    return (merge_duplicate_rows(rg, 'drugbank') for rg in row_groups)
