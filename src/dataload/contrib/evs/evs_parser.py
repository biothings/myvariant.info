import csv
import glob
from itertools import islice, groupby
try:
    import itertools.imap as map
except ImportError:
    pass
from utils.dataload import dict_sweep, value_convert, merge_duplicate_rows
from utils.hgvs import get_hgvs_from_vcf
from utils.hgvs import get_pos_start_end

VALID_COLUMN_NO = 31


def polyphen(field):
    if field.find(":") == 0:
        return field.split(":")
    else:
        return field


def count_dict(field):
    count_list = field.split("/")
    counts = dict(item.split("=") for item in count_list)
    return counts


def get_dbsnp(field):
    try:
        return field.split("_")[1]
    except:
        return "none"


# convert one snp to json
def _map_line_to_json(fields):
    chrInfo = fields[0].split(":")  # grch37
    chrom = chrInfo[0]
    chromStart = int(chrInfo[1])

    ma_fin_percent = fields[7].split("/")

    if fields[3]:
        mutation = fields[3].split(">")
        ref = mutation[0]
        alt = mutation[1]
        HGVS = get_hgvs_from_vcf(chrom, chromStart, ref, alt)
        hg19 = get_pos_start_end(chrom, chromStart, ref, alt)
        hg38 = get_pos_start_end(chrom, int(fields[30].split(":")[1]), ref, alt)

    # load as json data
    if HGVS is None:
        return

    one_snp_json = {
        "_id": HGVS,
        "evs":
            {
                "chrom": chrom,
                "hg19":
                    {
                        "start": hg19[0],
                        "end": hg19[1]
                    },
                "hg38":
                    {
                        "start": hg38[0],
                        "end": hg38[1]
                    },
                "rsid": fields[1],
                "dbsnp_version": get_dbsnp(fields[2]),
                "ref": ref,
                "alt": alt,
                "allele_count":
                    {
                        "european_american": count_dict(fields[4]),
                        "african_american": count_dict(fields[5]),
                        "all": count_dict(fields[6])
                    },
                "ma_fin_percent":
                    {
                        "european_american": ma_fin_percent[0],
                        "african_american": ma_fin_percent[1],
                        "all": ma_fin_percent[2]
                    },
                "genotype_count":
                    {
                        "european_american": count_dict(fields[8]),
                        "african_american": count_dict(fields[9]),
                        "all_genotype": count_dict(fields[10])
                    },
                "avg_sample_read": fields[11],
                "gene":
                    {
                        "symbol": fields[12],
                        "accession": fields[13]
                    },
                "function_gvs": fields[14],
                "hgvs":
                    {
                        "coding": fields[16],
                        "protein": fields[15]
                    },
                "coding_dna_size": fields[17],
                "conservation":
                    {
                        "phast_cons": fields[18],
                        "gerp": fields[19]
                    },
                "grantham_score": fields[20],
                "polyphen2":
                    {
                        "class": polyphen(fields[21])[0],
                        "score": polyphen(fields[21])[1]
                    },
                "ref_base_ncbi": fields[22],
                "chimp_allele": fields[23],
                "clinical_info": fields[24],
                "filter_status": fields[25],
                "on_illumina_human_exome_chip": fields[26],
                "gwas_pubmed_info": fields[27],
                "estimated_age_kyrs":
                    {
                        "ea": fields[28],
                        "aa": fields[29]
                    }
            }
        }
    return dict_sweep(value_convert(one_snp_json), vals=["NA", "none", "unknown"])


# open file, parse, pass to json mapper
def data_generator(input_file):
    open_file = open(input_file)
    evs = csv.reader(open_file, delimiter=" ")
    # Skip first 8 meta lines
    evs = islice(evs, 8, None)
    evs = (row for row in evs if ":" in row[30] and
           len(row) == VALID_COLUMN_NO)
    # skip rows with multiple mutations
    evs = (row for row in evs if len(row[3].split(";")) == 1)
    json_rows = map(_map_line_to_json, evs)
    row_groups = (it for (key, it) in groupby(json_rows, lambda row: row["_id"]))
    return (merge_duplicate_rows(rg, "evs") for rg in row_groups)


# load path and find files, pass to data_generator
def load_data(path):
    for input_file in sorted(glob.glob(path)):
        print(input_file)
        data = data_generator(input_file)
        for one_snp_json in data:
            yield one_snp_json
