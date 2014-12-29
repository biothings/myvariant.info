# -*- coding: utf-8 -*-
from utils.common import timesofar
import pymongo
import time
"""
Utility functions for parsing flatfiles, 
mapping to JSON, cleaning.
"""
        
# remove keys whos values are ".", "-", "", "NA", "none", " "
# and remove empty dictionaries
def dict_sweep(d, vals=[".", "-", "", "NA", "none", " "]): 
    """
    @param d: a dictionary
    @param vals: a string or list of strings to sweep
    """
    for key, val in d.items():
        if val in vals:
            del d[key]
        elif isinstance(val, list):
            for item in val:
                if item in vals:
                    del item
                elif isinstance(item, dict):
                    dict_sweep(item, vals)
            if len(val) == 0:
                del d[key]
        elif isinstance(val, dict):
            dict_sweep(val, vals)
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
        elif isinstance(val, list):
            try:
                d[key] = [int(x) for x in val]
            except (ValueError, TypeError):
                try:
                    d[key] = [float(x) for x in val]
                except (ValueError, TypeError):
                    pass
    return d


# if dict value is a list of length 1, unlist
def unlist(d):
    for key, val in d.items():
            if isinstance(val, list):
                if len(val) == 1:
                    d[key] = val[0]
            elif isinstance(val, dict):
                unlist(val)
    return d
    
# split fields by sep into comma separated lists, strip.
def list_split(d, sep):
    for key, val in d.items():
        if isinstance(val, dict):
            list_split(val, sep)
        try:
            if len(val.split(sep)) > 1:
                d[key] = val.rstrip().rstrip(sep).split(sep)
        except (AttributeError):
            pass
    return d

def id_strip(id_list):
    id_list = id_list.split("|")
    ids = []
    for id in id_list:
        ids.append(id.rstrip().lstrip())
    return ids

def merge_duplicate_rows(rows, db):
    """
    @param rows: rows to be grouped by
    @param db: database name, string
    """
    rows = list(rows)
    first_row = rows[0]
    other_rows = rows[1:]
    for row in other_rows:
        for i in first_row[db]:
            if i in row[db]:
                if row[db][i] != first_row[db][i]:
                    aa = first_row[db][i]
                    if not isinstance(aa, list):
                        aa = [aa]
                    aa.append(row[db][i])
                    first_row[db][i] = aa
            else:
                continue
    return first_row
    
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
        if cnt % 100000 == 0:
            print cnt, timesofar(t1)
    print "successfully loaded %s into mongodb" % collection_name 

def unique_ids(input_file):
    i = load_data(input_file)
    out = list(i)
    id_list = [a['_id'] for a in out if a]
    myset = set(id_list)
    print len(out), "documents produced" 
    print len(myset), "Unique IDs"
    return out
