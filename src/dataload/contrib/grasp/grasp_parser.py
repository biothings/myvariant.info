# -*- coding: utf-8 -*-
import csv
import glob
from itertools import islice, groupby, imap
import pymongo
import time
from utils.common import timesofar


VALID_COLUMN_NO = 70


# split "," separated fields into comma separated lists, strip.
def list_split(d):
    for key, val in d.items():
        if isinstance(val, dict):
            list_split(val)
        try:
            if len(val.split(",")) > 1:
                d[key] = val.split(",")
        except (AttributeError):
            pass
    return d
    
    
# remove keys whos values are "."
# and remove empty dictionaries
def dict_sweep(d):
    for key, val in d.items():
        if val == " ":
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
    

# convert one snp to json
def _map_line_to_json(fields):
    chrom = fields[5]
    chromStart = fields[6]
    #allele1 = fields[2]
    #allele2 = fields[4]
    #HGVS = "chr%s:g.%d%s>%s" % (chrom, chromStart, allele1, allele2)
    HGVS = "chr%s:g.%s" % (chrom, chromStart)

    # load as json data
    if HGVS is None:
        return

    one_snp_json = {

        "_id": HGVS,
        "grasp":
            {    'hg19':
                     {
                         'chr': fields[5],
                         'pos': fields[6]
                     },
                 'nhlbi_key': fields[0],
                 'hupfield': fields[1],
                 'last_curation_date': fields[2],
                 'creation_date': fields[3],
                 'snpid_dbsnp134': fields[4],
                 'publication':
                     {
                         'pmid': fields[7],
                         'snpid_in_paper': fields[8],
                         'location_within_paper': fields[9],
                         'p_value': fields[10],
                         'phenotype': fields[11],
                         'paper_phenotype_description': fields[12],
                         'paper_phenotype_categories': fields[13],
                         'date_pub': fields[14]
                     },
                 'in_nhgri_cat': fields[15],
                 'journal': fields[16],
                 'title': fields[17],
                 'includes_male_female_only_analyses': fields[18],
                 'exclusively_male_female': fields[19],
                 'initial_sample_description': fields[20],
                 'replication_sample_description': fields[21],
                 'platform_snps_passing_qc': fields[22],
                 'gwas_ancestry_description': fields[23],
                 'discovery': 
                     {
                         'total_samples': fields[25],
                         'european': fields[26],
                         'african': fields[27],
                         'east_asian': fields[28],
                         'indian_south_asian': fields[29],
                         'hispanic': fields[30],
                         'native': fields[31],
                         'micronesian': fields[32],
                         'arab_me': fields[33],
                         'mixed': fields[34],
                         'unspecified': fields[35],
                         'filipino': fields[36],
                         'indonesian': fields[37]
                     },
                 'replication':
                     {
                         'total_samples': fields[38],
                         'european': fields[39],
                         'african': fields[40],
                         'east_asian': fields[41],
                         'indian_south_asian': fields[42],
                         'hispanic': fields[43],
                         'native': fields[44],
                         'micronesian': fields[45],
                         'arab_me': fields[46],
                         'mixed': fields[47],
                         'unspecified': fields[48],
                         'filipino': fields[49],
                         'indonesian': fields[50]
                     },
                 'in_gene': fields[51],
                 'nearest_gene': fields[52],
                 'in_lincrna': fields[53],
                 'in_mirna': fields[54],
                 'in_mirna_bs': fields[55],
                 'dbsnp':
                     {
                         'fxn': fields[56],
                         'maf': fields[57],
                         'alleles_het_se': fields[58],
                         'validation': fields[59],
                         'clin_status': fields[60],
                     },
                 'oreg_anno': fields[61],
                 'conserv_pred_tfbs': fields[62],
                 'human_enhancer': fields[63],
                 'rna_edit': fields[64],
                 'polyphen2': fields[65],
                 'sift': fields[66],
                 'ls_snp': fields[67],
                 'uniprot': fields[68],
                 'eqtl_meth_metab_study': fields[69]
            }
        }
    return list_split(dict_sweep(unlist(value_convert(one_snp_json))))


def merge_duplicate_rows(rows):
    rows = list(rows)
    first_row = rows[0]
    other_rows = rows[1:]
    for row in other_rows:
        for i in first_row['grasp']:
            if i in row['grasp']:
                if row['grasp'][i] != first_row['grasp'][i]:
                    aa = first_row['grasp'][i]
                    if not isinstance(aa, list):
                        aa = [aa]
                    aa.append(row['grasp'][i])
                    first_row['grasp'][i] = aa             
    return first_row


# open file, parse, pass to json mapper
def load_data(input_file):
    with open(input_file) as open_file:
        grasp = csv.reader(open_file, delimiter="\t")
        # Skip first 8 meta lines
        grasp = islice(grasp, 8, None)
        grasp = (row for row in grasp if len(row) == VALID_COLUMN_NO)
        json_rows = imap(_map_line_to_json, grasp)
        row_groups = (it for (key, it) in groupby(json_rows, lambda row: row["_id"]))
        for one_snp_json in imap(merge_duplicate_rows, row_groups):
            yield one_snp_json


# open file, parse, pass to json mapper
def load_data(input_file):
    for file in sorted(glob.glob(input_file)):
        print file
        open_file = open(input_file)
        grasp = csv.reader(open_file, delimiter="\t")
        grasp.next()  # skip header
        bad_rows = []
        for row in grasp:
            #assert len(row) == VALID_COLUMN_NO
            try:
                one_snp_json = _map_line_to_json(row)
            #if one_snp_json:
                yield one_snp_json
            except:
                diff_rows = enumerate(row)
                wrong = [(i, row) for (i, row) in diff_rows]
                #print wrong[-1]
                 
        open_file.close()
        
        
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
    return db
    
i = load_data("/Users/Amark/Documents/Su_Lab/myvariant.info/grasp/graspmini.tsv")
out=list(i)
print len(out)
id_list=[]
for id in out:
    id_list.append(id['_id'])
myset = set(id_list)
print len(myset)
