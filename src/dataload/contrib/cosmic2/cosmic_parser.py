# -*- coding: utf-8 -*-
import csv
import re
import time
import pymongo
from itertools import imap, groupby
#from utils.common import timesofar


VALID_COLUMN_NO = 29


# remove keys whos values are "."
# and remove empty dictionaries
def dict_sweep(d):
    for key, val in d.items():
        if val == "":
            del d[key]
        elif isinstance(val, dict):
            dict_sweep(val)
            if len(val) == 0:
                del d[key]
    return d


# convert string numbers into integers or floats
def value_convert(d):
    for key, val in d.items():
        try:
            d[key] = int(val)
        except (ValueError, TypeError):
            try:
                d[key] = float(val)
            except (ValueError, TypeError):
                pass
        if isinstance(val, dict):
            value_convert(val)
    return d


# convert one snp to json
def _map_line_to_json(fields):
    assert len(fields) == VALID_COLUMN_NO
    chr_info = re.findall(r"[\w']+", fields[17])
    chrom = chr_info[0]  # Mutation GRCh37 genome position
    chromStart = int(chr_info[1])
    chromEnd = int(chr_info[2])

    HGVS = None
    cds = fields[13]
    sub = re.search(r'[ATCG]+>[ATCGMN]+', cds)
    ins = re.search(r'ins[ATCGMN]+|ins[0-9]+', cds)
    delete = cds.find('del') == 0
    del_ins = re.search(r'[0-9]+>[ATCGMN]+', cds)
    comp = re.search(r'[ATCGMN]+', cds)

    if sub:
        HGVS = "chr%s:g.%d%s" % (chrom, chromStart, sub.group())
    elif ins:
        HGVS = "chr%s:g.%d_%d%s" % (chrom, chromStart, chromEnd, ins.group())
    elif delete:
        HGVS = "chr%s:g.%d_%ddel" % (chrom, chromStart, chromEnd)
    elif del_ins:
        HGVS = "chr%s:g.%d_%ddelins%s" % (chrom, chromStart, chromEnd, comp.group())
    else:
        print 'Error2:', fields[15], cds

    # load as json data
    if HGVS is None:
        return

    one_snp_json = {

        "_id": HGVS,
        "cosmic":
            {
                "gene":
                    {
                        "symbol": fields[0],  # Gene name
                        "id": fields[3],  # HGNC ID
                        "cds_length": fields[2]
                    },
                "transcript": fields[1],  # Accession Number
                "sample":
                    {
                        "name": fields[4],  # Sample name
                        "id": fields[5]  # ID_sample
                    },
                "tumour":
                    {
                        "id": fields[6],  # ID_tumour
                        "primary_site": fields[7],  # Primary site
                        "site_subtype": fields[8],  # Site subtype
                        "primary_histology": fields[9],  # Primary histology
                        "histology_subtype": fields[10],  # Histology subtype
                        "origin": fields[1]
                    },
                "mutation":
                    {
                        "id": fields[12],  # Mutation ID
                        "cds": cds,  # Mutation CDS
                        "aa": fields[14],  # Mutation AA
                        "description": fields[15],  # Mutation Description
                        "zygosity": fields[16],  # Mutation zygosity
                        "somatic_status": fields[21]  # Mutation somatic status
                    },
                "chrom": chrom,
                "hg19":
                   {
                        "start": chromStart,
                        "end": chromEnd
                    },
                "pubmed": fields[22]  # Pubmed_PMID
            }
        }
    return dict_sweep(value_convert(one_snp_json))


def merge_duplicate_rows(rows):
    rows = list(rows)
    first_row = rows[0]
    other_rows = rows[1:]
    for row in other_rows:
        for i in first_row['cosmic']:
            if i in row['cosmic']:
                if row['cosmic'][i] != first_row['cosmic'][i]:
                    aa = first_row['cosmic'][i]
                    if not isinstance(aa, list):
                        aa = [aa]
                    aa.append(row['cosmic'][i])
                    first_row['cosmic'][i] = aa             
    return first_row


# open file, parse, pass to json mapper
def load_data(input_file):
    with open(input_file) as open_file:
        cosmic = csv.reader(open_file, delimiter="\t")
        cosmic.next()  # skip header
        cosmic = (row for row in cosmic
                    if row[13].find('?') != -1 and
                    row[16] != "" and
                    row[13] != "")
        cnt = 0
        cds = []
        for row in cosmic:
            if row[17] != "" and row[13] != "":
            #if row[13].find('?') == -1:
                cnt = cnt +1
                cds.append(row[17])
        json_rows = imap(_map_line_to_json, cosmic)
        row_groups = (it for (key, it) in groupby(json_rows, lambda row: row["_id"]))
        for one_snp_json in imap(merge_duplicate_rows, row_groups):
            yield one_snp_json
    

def timesofar(t0, clock=0, t1=None):
    '''return the string(eg.'3m3.42s') for the passed real time/CPU time so far
       from given t0 (return from t0=time.time() for real time/
       t0=time.clock() for CPU time).'''
    t1 = t1 or time.clock() if clock else time.time()
    t = t1 - t0
    h = int(t / 3600)
    m = int((t % 3600) / 60)
    s = round((t % 3600) % 60, 2)
    t_str = ''
    if h != 0:
        t_str += '%sh' % h
    if m != 0:
        t_str += '%sm' % m
    t_str += '%ss' % s
    return t_str
    
    
# load collection into mongodb
def load_collection(database, input_file_list, collection_name):
    """
    : param database: mongodb url
    : param input_file_list: variant docs, path to file
    : param collection_name: annotation source name
    """
    conn = pymongo.MongoClient(database)
    db = conn.variantdoc
    posts = db[collection_name]
    t1 = time.time()
    cnt = 0
    for doc in load_data(input_file_list):
        posts.insert(doc, manipulate=False, check_keys=False, w=0)
        cnt += 1
        if cnt % 1000 == 0:
            print cnt, timesofar(t1)
    print "successfully loaded %s into mongodb" % collection_name 

#i=load_data('/Users/Amark/Documents/Su_Lab/myvariant.info/cosmic/cosmicmini.tsv')
i=load_data('/Users/Amark/Documents/Su_Lab/myvariant.info/cosmic/CosmicCompleteExport_v70_100814.tsv')
out = list(i)
print len(out)
id_list=[]
for id in out:
    id_list.append(id['_id'])
myset = set(id_list)
print len(myset)
#load_collection('mongodb://myvariant_user:Qag1H6V%0vEG@su08.scripps.edu:27017/variantdoc', 
#                    '/Users/Amark/Documents/Su_Lab/myvariant.info/cosmic/CosmicCompleteExport_v70_100814.tsv',
#                    'cosmic')