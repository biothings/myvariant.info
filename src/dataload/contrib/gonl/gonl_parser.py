# -*- coding: utf-8 -*-
import pymongo
import time
from utils.common import timesofar


# split ";" separated fields into comma separated lists, strip.
def list_split(d):
    for key, val in d.items():
        if isinstance(val, dict):
            list_split(val)
        try:
            if len(val.split(";")) > 1:
                d[key] = val.rstrip().rstrip(';').split(";")
        except (AttributeError):
            pass
    return d


# remove keys whos values are "."
# and remove empty dictionaries
def dict_sweep(d):
    for key, val in d.items():
        if val == ".":
            del d[key]
        elif isinstance(val, list):
            d[key] = [dict_sweep(item) for item in val if isinstance(item, dict)]
            if len(val) == 0:
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


# convert one snp to json
def _map_line_to_json(fields):
    # specific variable treatment
    chrom = fields[0]
    chromStart = int(fields[1])
    allele1 = fields[3]
    allele2 = fields[4]
    HGVS = "chr%s:g.%d%s>%s" % (chrom, chromStart, allele1, allele2)
    chromEnd = chromStart + len(allele1)
    rsID = fields[2]
    QUAL = fields[5]
    FILTER = fields[6]
    info = fields[7].split(";")
    varType = "."
    AC = "."
    AF = "."
    AN = "."

    for i in info:
        i = i.strip()
        if i.startswith("AC"):
            AC = i.strip("AC=")
        elif i.startswith("AF="):
            AF = i.strip("AF=")
        elif i.startswith("AN="):
            AN = i.strip("AN=")
        elif i.startswith("set"):
            varType = i.strip("set=")

    # load as json data
    print "HGVS " + HGVS
    print chrom
    print chromStart
    print chromEnd
    print allele1
    print allele2
    print varType
    print rsID
    print AC
    print AF
    print AN

    one_snp_json = {

        "_id": HGVS,
        "gonl":
            {
                "chrom": chrom,
                "hg19":
                    {
                        "start": chromStart,
                        "end": chromEnd
                    },

                "allele1": allele1,
                "allele2": allele2,
                "varType": varType,
                "rsID": rsID,
                "QUAL": QUAL,
                "FILTER": FILTER,
                "AC": AC,
                "AF": AF,
                "AN": AN
            }
    }

    one_snp_json = list_split(dict_sweep(unlist(value_convert(one_snp_json))))
    one_snp_json["gonl"]["chrom"] = str(one_snp_json["gonl"]["chrom"])
    return one_snp_json


# open file, parse, pass to json mapper
def data_generator(input_file):
    open_file = open(input_file)
    # load vcf file
    line = open_file.readline()

    while line.strip() != "":
        if line.startswith("#"):
            print "HEADER LINE"
            line = open_file.readline()
        else:
            line = line.split("\t")
            line = open_file.readline()
    open_file.close()


# load path and find files, pass to data_generator
def load_data(path):
    input_file_list = getFileList()
    for input_file in input_file_list:
        print input_file
        data = data_generator(input_file)
        for one_snp_json in data:
            yield one_snp_json


def getFileList():
    input_file_list = []
    for i in range(1, 22):
        filename = "https://molgenis26.target.rug.nl/downloads/gonl_public/variants/release5/gonl.chr"+str(x)+".snps_indels.r5.vcf.gz"
        input_file_list.append(filename)
    return input_file_list


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
    input_file_list = getFileList()
    for doc in load_data(input_file_list):
        posts.insert(doc, manipulate=False, check_keys=False, w=0)
        cnt += 1
        if cnt % 100000 == 0:
            print cnt, timesofar(t1)
    print "successfully loaded %s into mongodb" % collection_name
