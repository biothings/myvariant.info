import csv
from biothings.utils.dataload import list_split, dict_sweep, unlist
from biothings.utils.dataload import value_convert_to_number
from biothings.utils.dataload import merge_duplicate_rows
from utils.hgvs import get_hgvs_from_vcf
from itertools import groupby

VALID_COLUMN_NO = 31

'''this parser is for denovo-db v1.5 downloaded from
http://denovo-db.gs.washington.edu/denovo-db/Download.jsp'''


def get_pos_start_end_from_hgvs(hgvs, var_type, position):
    '''get start,end tuple from hgvs name'''
    if var_type == "snp":
        start = position
        end = position
    else:
        start_end = hgvs.split("del")[0].split("ins")[0].split("g.")[1]
        start_end = start_end.split("_")
        if len(start_end) == 1:
            start = int(start_end[0])
            end = start
        elif len(start_end) == 2:
            start = int(start_end[0])
            end = int(start_end[1])
        else:
            raise ValueError("Cannot decide start/end from {}.".format((hgvs, var_type, position)))
    return start, end


# convert one snp to json
def _map_line_to_json(df):
    # specific variable treatment
    chrom = df["Chr"]
    if chrom == 'M':
        chrom = 'MT'
    position = int(df["Position"])
    ref, alt = df["Variant"].upper().split(">")
    HGVS, var_type = get_hgvs_from_vcf(chrom, position, ref, alt, mutant_type=True)
    chromStart, chromEnd = get_pos_start_end_from_hgvs(HGVS, var_type, position)

    sampleid = df["SampleID"]
    studyname = df["StudyName"]
    pubmedid = df["PubmedID"]
    numprobands = df["NumProbands"]
    numcontrols = df["NumControls"]
    sequencetype = df["SequenceType"]
    primaryphenotype = df["PrimaryPhenotype"]
    validation = df["Validation"]
    chrom = df["Chr"]
    position = df["Position"]
    variant = df["Variant"]
    rsid = df["rsID"]
    dbsnpbuild = df["DbsnpBuild"]
    ancestralallele = df["AncestralAllele"]
    kgenomecount = df["1000GenomeCount"]
    exacfreq = df["ExacFreq"]
    espaafreq = df["EspAaFreq"]
    espeafreq = df["EspEaFreq"]
    transcript = df["Transcript"]
    codingdnasize = df["codingDnaSize"]
    gene = df["Gene"]
    functionclass = df["FunctionClass"]
    cdnavariant = df["cDnaVariant"]
    proteinvariant = df["ProteinVariant"]
    exon_intron = df["Exon_Intron"]
    polyphen_hdiv = df["PolyPhen_HDiv"]
    polyphen_hvar = df["PolyPhen_HVar"]
    siftscore = df["SiftScore"]
    caddscore = df["CaddScore"]
    lofscore = df["LofScore"]
    lrtscore = df["LrtScore"]

# load as json data
    one_snp_json = {
        "_id": HGVS,
        "denovodb": {
            "chrom": chrom,
            "hg19": {
                "start": chromStart,
                "end": chromEnd
            },

            "ref": ref,
            "alt": alt,
            "sampleid": sampleid,
            "studyname": studyname,
            "pubmedid": pubmedid,
            "numprobands": numprobands,
            "numcontrols":  numcontrols,
            "sequencetype":  sequencetype,
            "primaryphenotype": primaryphenotype,
            "validation": validation,
            "chr": chrom,
            "position": position,
            "variant": variant,
            "rsid": rsid,
            "dbsnpbuild": dbsnpbuild,
            "ancestralallele": ancestralallele,
            "1000genomecount":  kgenomecount,
            "exacfreq":  exacfreq,
            "espaafreq":   espaafreq,
            "espeafreq":   espeafreq,
            "transcript":  transcript,
            "codingdnasize":  codingdnasize,
            "gene":    gene,
            "functionclass":  functionclass,
            "cdnavariant": cdnavariant,
            "proteinvariant":  proteinvariant,
            "exon_intron":   exon_intron,
            "polyphen(hdiv)": polyphen_hdiv,
            "polyphen(hvar)": polyphen_hvar,
            "siftscore":   siftscore,
            "caddscore": caddscore,
            "lofscore":  lofscore,
            "lrtscore":  lrtscore,
        }
    }

    one_snp_json = list_split(dict_sweep(unlist(value_convert_to_number(one_snp_json)), vals=[".", '-', None]), ";")
    one_snp_json["denovodb"]["chrom"] = str(one_snp_json["denovodb"]["chrom"])
    return one_snp_json


def clean_index(s):
    return s.replace("/", "_").replace("(", "_").replace(")", "").replace("#", "")


# open file, parse, pass to json mapper
def load_data(input_file, version='hg19'):
    open_file = open(input_file)
    db_denovodb = csv.reader(open_file, delimiter="\t")
    index = next(db_denovodb)
    while index[0].startswith("##"):
        index = next(db_denovodb)
    assert len(index) == VALID_COLUMN_NO, "Expecting %s columns, but got %s" % (VALID_COLUMN_NO, len(index))
    index = [clean_index(s) for s in index]
    denovodb = []
    for row in db_denovodb:
        df = dict(zip(index, row))
        denovodb.append(df)
    denovodb = filter(lambda row: row["Chr"] != "", denovodb)
    json_rows = map(_map_line_to_json, denovodb)
    json_rows = (row for row in json_rows if row)
    row_groups = (it for (key, it) in groupby(json_rows, lambda row: row["_id"]))
    return (merge_duplicate_rows(rg, "denovodb") for rg in row_groups)
