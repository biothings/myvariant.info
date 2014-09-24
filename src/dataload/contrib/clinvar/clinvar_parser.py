# -*- coding: utf-8 -*-
import csv
import re
import glob


VALID_COLUMN_NO = 25


# remove keys whos values are "."
# and remove empty dictionaries
def dict_sweep(d):
    for key, val in d.items():
        if val == "-":
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


# if dict value is a list of length 1, unlist
def unlist(d):
    for key, val in d.items():
            if isinstance(val, list):
                if len(val) == 1:
                    d[key] = val[0]
            elif isinstance(val, dict):
                unlist(val)
    return d


def phen_id(phenotype_ids):
    try:
        p = phenotype_ids.strip(";").replace(";",",").split(",")
        phen_id = {}
        for id in p:
            key, value = id.split(":")
            if key in phen_id:
                if not isinstance(phen_id[key], list):
                    phen_id[key] = [phen_id[key]]
                phen_id[key].append(value)
            else:
                phen_id[key] = value
        return phen_id
    except:
        return phenotype_ids


# convert one snp to json
def _map_line_to_json(fields):
    chrom = fields[13]
    chromStart = fields[14]
    chromEnd = fields[15]

    HGVS = None
    cds = fields[18].split(":")
    cds = cds[1]
    #print fields[1]
    #print cds
    
    seq = re.findall(r'[ATCGMNHYR]+|[0-9]+', cds)[-1]
    replace = re.findall(r'[ATCGMNYR=]+', cds)
    sub = re.search(r'[ATCGMNHYR]+>[ATCGMNHYR]+', cds)
    ins = re.search(r'ins[ATCGMNHYR]+|ins[0-9]+', cds)
    delete = fields[1] == 'deletion'
    indel = fields[1] == 'indel'
    dup = re.search(r'dup', cds)
    inv = re.search(r'inv|inv[0-9]+|inv[ATCGMNHYR]+', cds)
    if ins:
        delete = None
        indel = None
    elif delete:
        ins = None
        indel = None
    if sub:
        HGVS = "chr%s:g.%s%s" % (chrom, chromStart, sub.group())
    elif ins:
        HGVS = "chr%s:g.%s_%s%s" % (chrom, chromStart, chromEnd, ins.group())
    elif delete:
        HGVS = "chr%s:g.%s_%sdel" % (chrom, chromStart, chromEnd)
    elif indel:
        HGVS = "chr%s:g.%s_%sdelins%s" % (chrom, chromStart, chromEnd, seq)
    elif dup:
        HGVS = "chr%s:g.%s_%sdup%s" % (chrom, chromStart, chromEnd, seq)
    elif inv:
        HGVS = "chr%s:g.%s_%sinv%s" % (chrom, chromStart, chromEnd, inv.group())
    elif replace:
        HGVS = "chr%s:g.%s_%s%s" % (chrom, chromStart, chromEnd, replace)
    else:
        print 'ERROR:', fields[1], cds

    # load as json data
    if HGVS is None:
        return

    one_snp_json = {

        "_id": HGVS,
        "clinvar":
            {
                "allele_id": fields[0],
                "genome":
                    {
                        "assembly": fields[12],
                        "chr": fields[13],
                        "start": fields[14],
                        "end": fields[15]                    
                    },
                "type": fields[1],
                "name": fields[2],
                "gene":
                    {
                        "id": fields[3],
                        "symbol": fields[4]
                    },
                "clinical_significance": fields[5].split(";"),
                "rs_dbsnp": fields[6],
                "nsv_dbvar": fields[7],
                "rcv_accession": fields[8].split(";"),
                "tested_in_gtr": fields[9],
                "phenotype_id": phen_id(fields[10]),
                "origin": fields[11],
                "cytogenic": fields[16],
                "review_status": fields[17],
                "hgvs": 
                    {
                        "coding": fields[18],
                        "protein": fields[19]
                    },
                "number_submitters": fields[20],
                "last_evaluated": fields[21],
                "guidelines": fields[22],
                "other_ids": fields[23],
                "variant_id": fields[24]
            }
        }
    return dict_sweep(unlist(value_convert(one_snp_json)))


# open file, parse, pass to json mapper
def load_data(input_file):
    for file in sorted(glob.glob(input_file)):
        print file
        open_file = open(input_file)
        cosmic = csv.reader(open_file, delimiter="\t")
        cosmic.next()  # skip header
        for row in cosmic:
            assert len(row) == VALID_COLUMN_NO
            if row[12] == "GRCh37" or \
               row[13] == "-"  or \
               row[18] == "-"  or \
               re.search(r'p.', row[18]):
                continue  # skip variant
            one_snp_json = _map_line_to_json(row)
            if one_snp_json:
                yield one_snp_json
        open_file.close()
    
i = load_data("/Users/Amark/Documents/Su_Lab/myvariant.info/clinvar/variant_summary.txt")
out=list(i)