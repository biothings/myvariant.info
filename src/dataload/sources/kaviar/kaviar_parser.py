import vcf
from biothings.utils.dataload import unlist
from biothings.utils.dataload import value_convert_to_number
from utils.hgvs import get_hgvs_from_vcf

VALID_COLUMN_NO = 8

'''this parser is for Kaviar version 160204-Public(All variants, annotated with data sources) downloaded from
http://db.systemsbiology.net/kaviar/Kaviar.downloads.html'''


# convert one snp to json
def _map_line_to_json(item):
    chrom = item.CHROM
    chromStart = item.POS
    ref = item.REF
    info = item.INFO

    try:
        af = info['AF']
    except:
        af = None
    try:
        ac = info['AC']
    except:
        ac = None
    try:
        an = info['AN']
    except:
        ac = None
    try:
        ds = info['DS']
    except:
        ds = None

    # convert vcf object to string
    item.ALT = [str(alt) for alt in item.ALT]



    # if multiallelic, put all variants as a list in multi-allelic field
    hgvs_list = None
    if len(item.ALT) > 1:
        hgvs_list = [get_hgvs_from_vcf(chrom, chromStart, ref, alt, mutant_type=False) for alt in item.ALT]

    for i, alt in enumerate(item.ALT):
        (HGVS, var_type) = get_hgvs_from_vcf(chrom, chromStart, ref, alt, mutant_type=True)
        if HGVS is None:
            return

        assert len(item.ALT) == len(info['AC']), "Expecting length of item.ALT= length of info.AC, but not for %s" % (
        HGVS)
        assert len(item.ALT) == len(info['AF']), "Expecting length of item.ALT= length of info.AF, but not for %s" % (
        HGVS)
        if ds:
            assert len(item.ALT) == len(
                info['DS']), "Expecting length of item.ALT= length of info.DS, but not for %s" % (
                HGVS)

        # load as json data
        one_snp_json = {
            "_id": HGVS,
            "kaviar": {
                "multi-allelic": hgvs_list,
                "ref": ref,
                "alt": alt,
                "af": info['AF'][i],
                "ac": info['AC'][i],
                "an": an,
                "ds": info['DS'][i].split("|") if ds else None,
            }
        }
        obj = (dict_sweep(unlist(value_convert_to_number(one_snp_json)), [None,]))
        yield obj


# open file, parse, pass to json mapper
def load_data(input_file):
    vcf_reader = vcf.Reader(open(input_file, 'r'), strict_whitespace=True)
    for record in vcf_reader:
        for record_mapped in _map_line_to_json(record):
            yield record_mapped



def dict_sweep(d, vals=[".", "-", "", "NA", "none", " ", "Not Available", "unknown"]):
    """
    @param d: a dictionary
    @param vals: a string or list of strings to sweep
    """
    for key, val in list(d.items()):
        if val in vals:
            del d[key]
        elif isinstance(val, list):
            val = [v for v in val if v not in vals]
            for item in val:
                if isinstance(item, dict):
                    dict_sweep(item, vals)
            if len(val) == 0:
                del d[key]
            else:
                d[key] = val
        elif isinstance(val, dict):
            dict_sweep(val, vals)
            if len(val) == 0:
                del d[key]
    return d