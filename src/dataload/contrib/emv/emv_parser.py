# -*- coding: utf-8 -*-
#import os
import glob
import csv
from itertools import imap, groupby
import pymongo
import os


## merge EMV file with genomic ID file
#def file_merge(emv_file, id_file):
#    os.system("cut -f3 genomic_id.txt > genomic_id3.txt")
#    os.system("paste -d"," genomic_id3.txt EmVClass.2014-3.csv > emv.csv")

VALID_COLUMN_NO = 11

# remove keys whos values are ""
# and remove empty dictionaries
def dict_sweep(d):
    for key, val in d.items():
        if val == " " or \
           val is None:
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
    
def id_strip(id_list):
    id_list = id_list.split("|")
    ids = []
    for id in id_list:
        ids.append(id.rstrip().lstrip())
    return ids
        
# convert one snp to json
def _map_line_to_json(fields):  
    HGVS = fields[0]
    
    # load as json data
    if HGVS is None:
        return

    one_snp_json = {

        "_id": HGVS,
        "emv":
            {
                "gene": fields[2],
                "variant_id": fields[3],
                "exon": fields[4],
                "egl_variant": fields[5],
                "egl_protein": fields[6],
                "egl_classification": fields[7],
                "egl_classification_date": fields[8],
                "variant_aka_list": id_strip(fields[9]),
                "clinvar_rcv": fields[10],
            }
        }

    return dict_sweep(value_convert(one_snp_json))
    
    
def merge_duplicate_rows(rows):
    rows = list(rows)
    first_row = rows[0]
    other_rows = rows[1:]
    for row in other_rows:
        for i in first_row['emv']:
            if i in row['emv']:
                if row['emv'][i] != first_row['emv'][i]:
                    aa = first_row['emv'][i]
                    if not isinstance(aa, list):
                        aa = [aa]
                    aa.append(row['emv'][i])
                    first_row['emv'][i] = aa
            else:
                continue
    return first_row
    
    
# open file, parse, pass to json mapper
def data_generator(input_file):
    #with open(input_file) as open_file:
    os.system("sort -t$'\t' -k1 -n %s > %s_sorted.csv" % (input_file, input_file))
    open_file = open("%s_sorted.csv" % (input_file))    
    emv = csv.reader(open_file, delimiter=",")
    # Skip header
    emv.next()
    json_rows = imap(_map_line_to_json, emv)
    row_groups = (it for (key, it) in groupby(json_rows, lambda row: row["_id"]))
    for one_snp_json in imap(merge_duplicate_rows, row_groups):
        yield one_snp_json
    open_file.close()
        
            
# load path and find files, pass to data_generator
def load_data(path):
    for input_file in sorted(glob.glob(path)):
        print input_file
        data = data_generator(input_file)
        for one_snp_json in data:
            yield one_snp_json
    

def load_collection(database, input_file_list, collection_name):
    """
    : param database: mongodb url
    : param input_file_list: variant docs, path to file
    : param collection_name: annotation source name
    """
    conn = pymongo.MongoClient(database)
    db = conn.variantdoc
    posts = db[collection_name]
    for doc in load_data(input_file_list):
        posts.insert(doc, manipulate=False, check_keys=False, w=0)
    print "successfully loaded %s into mongodb" % collection_name
    