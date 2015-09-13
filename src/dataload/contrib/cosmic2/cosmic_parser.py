# -*- coding: utf-8 -*-
import csv
import re
from itertools import imap, groupby, ifilter
import operator
from utils.dataload import dict_sweep, value_convert, merge_duplicate_rows


VALID_COLUMN_NO = 29 + 1


# convert one snp to json
def _map_line_to_json(fields):
    assert len(fields) == VALID_COLUMN_NO
    chr_info = re.findall(r"[\w']+", fields[17])
    chrom = chr_info[0]  # Mutation GRCh37 genome position
    chromStart = chr_info[1]
    chromEnd = chr_info[2]

    HGVS = None
    cds = fields[13]
    sub = re.search(r'[ATCGMNHKRY]+>[ATCGMNHKRY]+', cds)
    ins = re.search(r'ins[ATCGMN]+|ins[0-9]+', cds)
    delete = cds.find('del') != -1
    del_ins = re.search(r'[0-9]+>[ATCGMN]+', cds)
    comp = re.search(r'[ATCGMN]+', cds)

    if sub:
        HGVS = "chr%s:g.%s%s" % (chrom, chromStart, sub.group())
    elif ins:
        HGVS = "chr%s:g.%s_%s%s" % (chrom, chromStart, chromEnd, ins.group())
    elif delete:
        HGVS = "chr%s:g.%s_%sdel" % (chrom, chromStart, chromEnd)
    elif del_ins:
        HGVS = "chr%s:g.%s_%sdelins%s" % (chrom, chromStart, chromEnd, comp.group())
    # elif comp:
    #    HGVS = "chr%s:g.%s_%s%s" % (chrom, chromStart, chromEnd, comp.group())
    else:
        HGVS = fields[12]
        print "Error2:", fields[15], cds, fields[17]

    # load as json data
    if HGVS is None:
        return

    one_snp_json = {
        "sorter": fields[17] + fields[13],
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
                        "id": "COSM" + fields[12],  # Mutation ID
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
    return dict_sweep(value_convert(one_snp_json), vals=[""])


# open file, parse, pass to json mapper
def load_data(input_file):
    # os.system("sort -t$'\t' -k18 -k14 %s > %s_sorted.tsv" % (input_file, input_file))
    # open_file = open("%s_sorted.tsv" % (input_file))
    open_file = open(input_file)
    open_file = csv.reader(open_file, delimiter="\t")
    cosmic = []
    for row in open_file:
        try:
            c = row[13].split(".")[1]
        except:
            c = ""
        row.append(row[17].split("-")[0] + "." + c)
        cosmic.append(row)
        if row[-1] != "":
            print row[-1]
    cosmic = sorted(cosmic, key=operator.itemgetter(17), reverse=True)
    cosmic = ifilter(lambda row:
                     row[17] != "" and
                     row[13] != "", cosmic)
    json_rows = imap(_map_line_to_json, cosmic)
    json_rows = (row for row in json_rows if row)
    row_groups = (it for (key, it) in groupby(json_rows, lambda row: row["_id"]))
    return (merge_duplicate_rows(rg, "cosmic") for rg in row_groups)
