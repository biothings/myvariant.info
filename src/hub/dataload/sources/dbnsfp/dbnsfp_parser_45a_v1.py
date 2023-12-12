import re
import csv
from enum import Flag
from dataclasses import dataclass
from typing import Callable
from types import SimpleNamespace
from utils.table import TableColumn, create_tag_column_map
from utils.dotfield import parse_dot_fields
from biothings.utils.common import anyfile


# VALID_COLUMN_NO = 367  # for 4.1a
# VALID_COLUMN_NO = 642  # for 4.2a
# VALID_COLUMN_NO = 643  # for 4.3a
VALID_COLUMN_NO = 689  # for 4.4a

MUTPRED_TOP5FEATURES_PATTERN = re.compile(r" \(P = ([eE0-9.-]*)\)$")

# dbNSFP_variant use "." for missing values;
# other none values are borrowed from the `biothings.utils.dataload.dict_sweep` function and
#   from the default `na_values` argument of pandas.read_csv().
# see https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
NA_VALUES = frozenset({
    r'.', r'', r" ", r"-", r'#N/A', r'#N/A N/A', r'#NA', r'-1.#IND', r'-1.#QNAN', r'-NaN', r'-nan',
    r'1.#IND', r'1.#QNAN', r'<NA>', r'N/A', r'NA', r'NULL', r'NaN', r'n/a', r'nan', r'null', r'none',
    r"Not Available", r"unknown"
})

# A tag can be any of string value; columns with the same tag are looked-up as a group
COLUMN_TAG = SimpleNamespace()
COLUMN_TAG.HG38_POS = "hg38_pos"  # for "pos(1-based)"
COLUMN_TAG.HG19_POS = "hg19_pos"  # for "hg19_pos(1-based)"
COLUMN_TAG.HG38_CHROM = "hg38_chrom"  # for "#chr"
COLUMN_TAG.HG19_CHROM = "hg19_chrom"  # for "hg19_chr"
COLUMN_TAG.REF_ALLELE = "ref"
COLUMN_TAG.ALT_ALLELE = "alt"
COLUMN_TAG.GTEX_GENE = "gtex_gene"
COLUMN_TAG.GTEX_TISSUE = "gtex_tissue"
# Note that column "MutationTaster_converted_rankscore" is not tagged
COLUMN_TAG.MUTATION_TASTER_AAE = "MutationTaster_AAE"
COLUMN_TAG.MUTATION_TASTER_MODEL = "MutationTaster_model"
COLUMN_TAG.MUTATION_TASTER_PRED = "MutationTaster_pred"
COLUMN_TAG.MUTATION_TASTER_SCORE = "MutationTaster_score"
COLUMN_TAG.ALOFT_FRACTION_TRANSCRIPTS_AFFECTED = "Aloft_Fraction_transcripts_affected"
COLUMN_TAG.ALOFT_PROB_TOLERANT = "Aloft_prob_Tolerant"
COLUMN_TAG.ALOFT_PROB_RECESSIVE = "Aloft_prob_Recessive"
COLUMN_TAG.ALOFT_PROB_DOMINANT = "Aloft_prob_Dominant"
COLUMN_TAG.ALOFT_PRED = "Aloft_pred"
COLUMN_TAG.ALOFT_CONFIDENCE = "Aloft_Confidence"


def _check_length(lst: list):
    """
    If the input list is empty (i.e. length is 0), return None;
    if the input list has only 1 element (i.e. length is 1), return the element;
    otherwise return the list as-is.
    """
    if not lst:
        return None
    if len(lst) == 1:
        return lst[0]
    return lst


class Assembly(Flag):
    HG19 = 1  # indicates that a column belongs to hg19 docs
    HG38 = 2  # indicates that a column belongs to hg38 docs
    BOTH = HG19 | HG38  # (BOTH == 3) applies to both assemblies

    @classmethod
    def assembly_of(cls, name: str):
        # E.g. when member_name == "HG19", member is Assembly.HG19
        for member_name, member in cls.__members__.items():
            if name.upper() == member_name:
                return member
        else:
            raise ValueError(f"'{cls.__name__}' enum not found for '{name}'")


@dataclass
class Column(TableColumn):
    """
    Assembly-specific column configuration
    """
    assembly: str | Assembly = None  # which assembly or assemblies this column belongs to

    def __post_init__(self):
        super().__post_init__()

        if self.assembly is None:
            self.assembly = Assembly.BOTH
            return

        if isinstance(self.assembly, Assembly):
            return

        if isinstance(self.assembly, str):
            self.assembly = Assembly.assembly_of(self.assembly)
            return

        raise ValueError(f"Cannot recognize assembly {self.assembly}")

    def is_hg19(self):
        return bool(self.assembly & Assembly.HG19)  # true if self.assembly is HG19 or BOTH

    def is_hg38(self):
        return bool(self.assembly & Assembly.HG38)  # true if self.assembly is HG38 or BOTH


def split(sep: str, na_values: set = NA_VALUES, drop_na: bool = False):
    def _func_drop_na(value: str):
        result = [v for v in value.split(sep) if v not in na_values]
        return result

    def _func_keep_na(value: str):
        result = [v if v not in na_values else None for v in value.split(sep)]
        if all(v is None for v in result):  # we keep NA values in the result; however if every value in the result is None, we treat whole result as None
            return None
        return result

    return _func_drop_na if drop_na else _func_keep_na


def split_cast(sep: str, astype: Callable, na_values: set = NA_VALUES, drop_na: bool = False):
    def _func_drop_na(value: str):
        result = [astype(v) for v in value.split(sep) if v not in na_values]
        return result

    def _func_keep_na(value: str):
        result = [astype(v) if v not in na_values else None for v in value.split(sep)]
        if all(v is None for v in result):  # we keep NA values in the result; however if every value in the result is None, we treat whole result as None
            return None
        return result

    return _func_drop_na if drop_na else _func_keep_na


def compose(_split_func: Callable, _unlist_func: Callable):
    def _func(value):
        split_result = _split_func(value)
        if split_result is None:
            return None
        return _unlist_func(split_result)
    return _func


# Transforming functions for "protein" data sources
# We don't compose with _check_length because it would be easier to apply "zip" on the split results if all values are lists
split_str = split(";")
split_float = split_cast(";", float)
split_int = split_cast(";", int)

# Transforming functions for other common non-"protein" data sources
split_str_drop_na = compose(split(";", drop_na=True), _check_length)
split_float_drop_na = compose(split_cast(";", float, drop_na=True), _check_length)
split_int_drop_na = compose(split_cast(";", int, drop_na=True), _check_length)

# Transforming functions for specific data sources
split_clinvar = compose(split(r"|", drop_na=True), _check_length)
split_genotype = compose(split(r"/", drop_na=True), _check_length)  # for "AltaiNeandertal", "Denisova", "VindijiaNeandertal", and "ChagyrskayaNeandertal"


def normalize_chrom(chr: str):
    """
    In dbNSFP, chromosomes are marked 1-22, "X", "Y", and "M" (Mitochondrial).
    However, in MyVariant, we mark Mitochondrial chromosome "MT".
    """
    return "MT" if chr == "M" else chr


def make_zero_based(pos: str):
    """
    Convert a 1-based chromosomal position to a 0-based start-end pair.
    """
    _pos = int(pos)
    return {"start": _pos, "end": _pos}


def parse_mutpred_top5features(value):
    """
    `mutpred_mechanisms` is a string combined from 5 clauses, separated by semicolons.
    Each clause has the same pattern of "<mechanism> (P = <p_val>)".

    E.g. "Loss of helix (P = 0.0444);Gain of loop (P = 0.0502);Gain of catalytic residue at A444 (P = 0.1876);\
    Gain of solvent accessibility (P = 0.2291);Loss of disorder (P = 0.9475)"

    Here we apply regex to parse this string and get a list of 5 tuples like

        [('Loss of helix', '0.0444'), ('Gain of loop', '0.0502'), ('Gain of catalytic residue at A444', '0.1876'),
        ('Gain of solvent accessibility', '0.2291'), ('Loss of disorder', '0.9475')]

    Then construct a list of 5 dictionaries of <"mechanism": xxx, "p_val": xxx> and return
    """
    if value is None:
        return None

    mp_list = [tuple(e for e in MUTPRED_TOP5FEATURES_PATTERN.split(s) if e.strip()) for s in value.split(";")]
    result = [{"mechanism": mp[0], "p_val": float(mp[1])} for mp in mp_list if mp and len(mp) == 2]

    return _check_length(result)


def parse_siphy_29way_pi(value: str):
    """
    A "SiPhy_29way_pi" value, if not None, is a string separated by ":", representing an estimated stationary
    distribution of A, C, G and T at a variant site. E.g. "0.0:0.5259:0.0:0.4741".

    Here we split the string and convert it to a dict of {<nt>: <freq>}.
    """
    if value is None:
        return None

    freq = [float(v) for v in value.split(":")]
    pi_dict = {"a": freq[0], "c": freq[1], "g": freq[2], "t": freq[3]}
    return pi_dict


def split_zip(values: list[str], sep: str, na_values: set = NA_VALUES):
    """
    Split each string in values by sep into a list, and generate tuples from all the lists.

    E.g. with the following input,

        values = ["P54578-2;P54578-3;A6NJA2;P54578", "UBP14_HUMAN;UBP14_HUMAN;A6NJA2_HUMAN;UBP14_HUMAN"]

    the returned generator can make:

        [('P54578-2', 'UBP14_HUMAN'),
         ('P54578-3', 'UBP14_HUMAN'),
         ('A6NJA2', 'A6NJA2_HUMAN'),
         ('P54578', 'UBP14_HUMAN')]

    Reference implementation: https://docs.python.org/3.3/library/functions.html#zip
    """
    sentinel = object()
    iterators = [(v if v not in na_values else None for v in value.split(sep)) for value in values]

    while iterators:  # always true if iterators is not empty
        result = []
        for it in iterators:
            element = next(it, sentinel)
            if element is sentinel:  # terminate at once when a `it` is fully consumed
                return
            result.append(element)
        yield tuple(result)


COLUMNS = [
    Column("#chr", dest="chrom", transform=normalize_chrom, assembly="hg38", tag=COLUMN_TAG.HG38_CHROM),  # representing "chrom" only for assembly 'hg38'
    Column("pos(1-based)", dest="hg38", transform=make_zero_based, tag=COLUMN_TAG.HG38_POS),
    Column("ref", transform=str.upper, tag=COLUMN_TAG.REF_ALLELE),
    Column("alt", transform=str.upper, tag=COLUMN_TAG.ALT_ALLELE),
    Column("aaref", dest="aa.ref"),
    Column("aaalt", dest="aa.alt"),
    Column("rs_dbSNP", dest="rsid"),
    Column("hg19_chr", dest="chrom", transform=normalize_chrom, assembly="hg19", tag=COLUMN_TAG.HG19_CHROM),  # representing "chrom" only for assembly 'hg19'
    Column("hg19_pos(1-based)", dest="hg19", transform=make_zero_based, tag=COLUMN_TAG.HG19_POS),
    # Column("hg18_chr"),  # Not Used
    Column("hg18_pos(1-based)", dest="hg18", transform=make_zero_based),
    Column("aapos", dest="protein.aa.pos", transform=split_int),
    Column("genename", dest="protein.genename", transform=split_str),
    Column("Ensembl_geneid", dest="protein.geneid", transform=split_str),
    Column("Ensembl_transcriptid", dest="protein.transcriptid", transform=split_str),
    Column("Ensembl_proteinid", dest="protein.proteinid", transform=split_str),
    Column("Uniprot_acc", dest="protein.uniprot.acc", transform=split_str),
    Column("Uniprot_entry", dest="protein.uniprot.entry", transform=split_str),
    Column("HGVSc_ANNOVAR", dest="protein.hgvsc.annovar", transform=split_str),
    Column("HGVSp_ANNOVAR", dest="protein.hgvsp.annovar", transform=split_str),
    Column("HGVSc_snpEff", dest="protein.hgvsc.snpeff", transform=split_str),
    Column("HGVSp_snpEff", dest="protein.hgvsp.snpeff", transform=split_str),
    Column("HGVSc_VEP", dest="protein.hgvsc.vep", transform=split_str),
    Column("HGVSp_VEP", dest="protein.hgvsp.vep", transform=split_str),
    Column("APPRIS", dest="protein.appris", transform=split_str),
    Column("GENCODE_basic", dest="protein.gencode_basic", transform=split_str),
    Column("TSL", dest="protein.tsl", transform=split_int),
    Column("VEP_canonical", dest="protein.vep_canonical", transform=split_str),
    Column("cds_strand", dest="cds_strand", transform=split_str_drop_na),
    Column("refcodon", dest="protein.aa.refcodon", transform=split_str),
    Column("codonpos", dest="protein.aa.codonpos", transform=split_int),
    Column("codon_degeneracy", dest="protein.aa.codon_degeneracy", transform=split_int),
    Column("Ancestral_allele", dest="ancestral_allele", transform=split_str_drop_na),
    Column("AltaiNeandertal", dest="altai_neandertal", transform=split_genotype),
    Column("Denisova", transform=split_genotype),
    Column("VindijiaNeandertal", dest="vindijia_neandertal", transform=split_genotype),
    Column("ChagyrskayaNeandertal", dest="chagyrskaya_neandertal", transform=split_genotype),
    Column("SIFT_score", dest="protein.sift.score", transform=split_float),
    Column("SIFT_converted_rankscore", dest="sift.converted_rankscore", transform=split_float_drop_na),
    Column("SIFT_pred", dest="protein.sift.pred", transform=split_str),
    Column("SIFT4G_score", dest="protein.sift4g.score", transform=split_float),
    Column("SIFT4G_converted_rankscore", dest="sift4g.converted_rankscore", transform=split_float_drop_na),
    Column("SIFT4G_pred", dest="protein.sift4g.pred", transform=split_str),
    Column("Polyphen2_HDIV_score", dest="protein.polyphen2.hdiv.score", transform=split_float),
    Column("Polyphen2_HDIV_rankscore", transform=split_float_drop_na),
    Column("Polyphen2_HDIV_pred", dest="protein.polyphen2.hdiv.pred", transform=split_str),
    Column("Polyphen2_HVAR_score", dest="protein.polyphen2.hvar.score", transform=split_float),
    Column("Polyphen2_HVAR_rankscore", transform=split_float_drop_na),
    Column("Polyphen2_HVAR_pred", dest="protein.polyphen2.hvar.pred", transform=split_str),
    Column("LRT_score", transform=split_float_drop_na),
    Column("LRT_converted_rankscore", dest="lrt.converted_rankscore", transform=split_float_drop_na),
    Column("LRT_pred", transform=split_str_drop_na),
    Column("LRT_Omega", transform=split_float_drop_na),
    Column("MutationTaster_score", tag=COLUMN_TAG.MUTATION_TASTER_SCORE),
    Column("MutationTaster_converted_rankscore", dest="mutationtaster.converted_rankscore", transform=split_float_drop_na),
    Column("MutationTaster_pred", tag=COLUMN_TAG.MUTATION_TASTER_PRED),
    Column("MutationTaster_model", tag=COLUMN_TAG.MUTATION_TASTER_MODEL),
    Column("MutationTaster_AAE", tag=COLUMN_TAG.MUTATION_TASTER_AAE),
    Column("MutationAssessor_score", dest="protein.mutationassessor.score", transform=split_float),
    Column("MutationAssessor_rankscore", transform=split_float_drop_na),
    Column("MutationAssessor_pred", dest="protein.mutationassessor.pred", transform=split_str),
    Column("FATHMM_score", dest="protein.fathmm.score", transform=split_float),
    Column("FATHMM_converted_rankscore", dest="fathmm.converted_rankscore", transform=split_float_drop_na),
    Column("FATHMM_pred", dest="protein.fathmm.pred", transform=split_str),
    Column("PROVEAN_score", dest="protein.provean.score", transform=split_float),
    Column("PROVEAN_converted_rankscore", dest="provean.converted_rankscore", transform=split_float_drop_na),
    Column("PROVEAN_pred", dest="protein.provean.pred", transform=split_str),
    Column("VEST4_score", dest="protein.vest4.score", transform=split_float),
    Column("VEST4_rankscore", transform=split_float_drop_na),
    Column("MetaSVM_score", transform=split_float_drop_na),
    Column("MetaSVM_rankscore", transform=split_float_drop_na),
    Column("MetaSVM_pred", transform=split_str_drop_na),
    Column("MetaLR_score", transform=split_float_drop_na),
    Column("MetaLR_rankscore", transform=split_float_drop_na),
    Column("MetaLR_pred", transform=split_str_drop_na),
    Column("Reliability_index", dest="reliability_index", transform=int),
    Column("MetaRNN_score", transform=split_float_drop_na),
    Column("MetaRNN_rankscore", transform=split_float_drop_na),
    Column("MetaRNN_pred", transform=split_str_drop_na),
    Column("M-CAP_score", transform=split_float_drop_na),
    Column("M-CAP_rankscore", transform=split_float_drop_na),
    Column("M-CAP_pred", transform=split_str_drop_na),
    Column("REVEL_score", dest="protein.revel.score", transform=split_float),
    Column("REVEL_rankscore", transform=split_float_drop_na),
    Column("MutPred_score", transform=split_float_drop_na),
    Column("MutPred_rankscore", transform=split_float_drop_na),
    Column("MutPred_protID", dest="mutpred.accession", transform=split_str_drop_na),
    Column("MutPred_AAchange", dest="mutpred.aa_change", transform=split_str_drop_na),
    Column("MutPred_Top5features", dest="mutpred.pred", transform=parse_mutpred_top5features),
    Column("MVP_score", dest="protein.mvp.score", transform=split_float),
    Column("MVP_rankscore", transform=split_float_drop_na),
    Column("gMVP_score", dest="protein.gmvp.score", transform=split_float),  # new in 4.4.a
    Column("gMVP_rankscore", transform=split_float_drop_na),  # new in 4.4.a
    Column("MPC_score", dest="protein.mpc.score", transform=split_float),
    Column("MPC_rankscore", transform=split_float_drop_na),
    Column("PrimateAI_score", transform=split_float_drop_na),
    Column("PrimateAI_rankscore", transform=split_float_drop_na),
    Column("PrimateAI_pred", transform=split_str_drop_na),
    Column("DEOGEN2_score", transform=split_float_drop_na),
    Column("DEOGEN2_rankscore", transform=split_float_drop_na),
    Column("DEOGEN2_pred", transform=split_str_drop_na),
    Column("BayesDel_addAF_score", dest="bayesdel.add_af.score", transform=split_float_drop_na),
    Column("BayesDel_addAF_rankscore", dest="bayesdel.add_af.rankscore", transform=split_float_drop_na),
    Column("BayesDel_addAF_pred", dest="bayesdel.add_af.pred", transform=split_str_drop_na),
    Column("BayesDel_noAF_score", dest="bayesdel.no_af.score", transform=split_float_drop_na),
    Column("BayesDel_noAF_rankscore", dest="bayesdel.no_af.rankscore", transform=split_float_drop_na),
    Column("BayesDel_noAF_pred", dest="bayesdel.no_af.pred", transform=split_str_drop_na),
    Column("ClinPred_score", transform=split_float_drop_na),
    Column("ClinPred_rankscore", transform=split_float_drop_na),
    Column("ClinPred_pred", transform=split_str_drop_na),
    Column("LIST-S2_score", transform=split_float_drop_na),
    Column("LIST-S2_rankscore", transform=split_float_drop_na),
    Column("LIST-S2_pred", transform=split_str_drop_na),
    Column("VARITY_R_score", transform=split_float_drop_na),  # new in 4.4.a
    Column("VARITY_R_rankscore", transform=split_float_drop_na),
    Column("VARITY_ER_score", transform=split_float_drop_na),
    Column("VARITY_ER_rankscore", transform=split_float_drop_na),
    Column("VARITY_R_LOO_score", dest="varity.r_loo.score", transform=split_float_drop_na),
    Column("VARITY_R_LOO_rankscore", dest="varity.r_loo.rankscore", transform=split_float_drop_na),
    Column("VARITY_ER_LOO_score", dest="varity.er_loo.score", transform=split_float_drop_na),
    Column("VARITY_ER_LOO_rankscore", dest="varity.er_loo.rankscore", transform=split_float_drop_na),
    Column("ESM1b_score", dest="esm1b.score", transform=split_float),  # new in 4.5.a
    Column("ESM1b_rankscore", dest="esm1b.rankscore", transform=split_float_drop_na),  # new in 4.5.a
    Column("ESM1b_pred", dest="esm1b.pred", transform=split_float_drop_na),  # new in 4.5.a
    Column("EVE_score", dest="eve.score", transform=split_float),  # new in 4.5.a
    Column("EVE_rankscore", dest="eve.rankscore", transform=split_float_drop_na),  # new in 4.5.a
    Column("EVE_Class10_pred", dest="eve.class10.pred", transform=split_float_drop_na),  # new in 4.5.a
    Column("EVE_Class20_pred", dest="eve.class20.pred", transform=split_float_drop_na),  # new in 4.5.a
    Column("EVE_Class25_pred", dest="eve.class25.pred", transform=split_float_drop_na),  # new in 4.5.a
    Column("EVE_Class30_pred", dest="eve.class30.pred", transform=split_float_drop_na),  # new in 4.5.a
    Column("EVE_Class40_pred", dest="eve.class40.pred", transform=split_float_drop_na),  # new in 4.5.a
    Column("EVE_Class50_pred", dest="eve.class50.pred", transform=split_float_drop_na),  # new in 4.5.a
    Column("EVE_Class60_pred", dest="eve.class60.pred", transform=split_float_drop_na),  # new in 4.5.a
    Column("EVE_Class70_pred", dest="eve.class70.pred", transform=split_float_drop_na),  # new in 4.5.a
    Column("EVE_Class75_pred", dest="eve.class75.pred", transform=split_float_drop_na),  # new in 4.5.a
    Column("EVE_Class80_pred", dest="eve.class80.pred", transform=split_float_drop_na),  # new in 4.5.a
    Column("EVE_Class90_pred", dest="eve.class90.pred", transform=split_float_drop_na),  # new in 4.5.a
    Column("AlphaMissense_score", dest="alphamissense.score", transform=split_float),  # new in 4.5.a
    Column("AlphaMissense_rankscore", dest="alphamissense.rankscore", transform=split_float_drop_na),  # new in 4.5.a
    Column("AlphaMissense_pred", dest="alphamissense.pred", transform=split_float_drop_na),  # new in 4.5.a
    Column("Aloft_Fraction_transcripts_affected", dest="protein.aloft.fraction_transcripts_affected", transform=split_str, tag=COLUMN_TAG.ALOFT_FRACTION_TRANSCRIPTS_AFFECTED),
    Column("Aloft_prob_Tolerant", dest="protein.aloft.prob_tolerant", transform=split_str, tag=COLUMN_TAG.ALOFT_PROB_TOLERANT),
    Column("Aloft_prob_Recessive", dest="protein.aloft.prob_recessive", transform=split_str, tag=COLUMN_TAG.ALOFT_PROB_RECESSIVE),
    Column("Aloft_prob_Dominant", dest="protein.aloft.prob_dominant", transform=split_str, tag=COLUMN_TAG.ALOFT_PROB_DOMINANT),
    Column("Aloft_pred", dest="protein.aloft.pred", transform=split_str, tag=COLUMN_TAG.ALOFT_PRED),
    Column("Aloft_Confidence", dest="protein.aloft.confidence", transform=split_str, tag=COLUMN_TAG.ALOFT_CONFIDENCE),
    Column("CADD_raw", dest="cadd.raw_score", transform=split_float_drop_na, assembly="hg38"),  # TODO CADD will have hg38 next update. Deprecate these 3 field then.
    Column("CADD_raw_rankscore", dest="cadd.raw_rankscore", transform=split_float_drop_na, assembly="hg38"),
    Column("CADD_phred", transform=split_float_drop_na, assembly="hg38"),  # CADD phred-like scores, not as other predications of string type
    # Column("CADD_raw_hg19", assembly="hg19"),  # discarded because Myvariant.info already has a hg19-only datasource of CADD.
    # Column("CADD_raw_rankscore_hg19", assembly="hg19"),  # ditto
    # Column("CADD_phred_hg19", assembly="hg19"),  # ditto
    Column("DANN_score", transform=split_float_drop_na),
    Column("DANN_rankscore", transform=split_float_drop_na),
    Column("fathmm-MKL_coding_score", dest="fathmm-mkl.coding_score", transform=split_float_drop_na),
    Column("fathmm-MKL_coding_rankscore", dest="fathmm-mkl.coding_rankscore", transform=split_float_drop_na),
    Column("fathmm-MKL_coding_pred", dest="fathmm-mkl.coding_pred", transform=split_str_drop_na),
    Column("fathmm-MKL_coding_group", dest="fathmm-mkl.coding_group", transform=split_str_drop_na),
    Column("fathmm-XF_coding_score", dest="fathmm-xf.coding_score", transform=split_float_drop_na),
    Column("fathmm-XF_coding_rankscore", dest="fathmm-xf.coding_rankscore", transform=split_float_drop_na),
    Column("fathmm-XF_coding_pred", dest="fathmm-xf.coding_pred", transform=split_str_drop_na),
    Column("Eigen-raw_coding", dest="eigen.raw_coding", transform=split_float_drop_na),
    Column("Eigen-raw_coding_rankscore", dest="eigen.raw_coding_rankscore", transform=split_float_drop_na),
    Column("Eigen-phred_coding", dest="eigen.phred_coding", transform=split_float_drop_na),
    Column("Eigen-PC-raw_coding", dest="eigen-pc.raw_coding", transform=split_float_drop_na),
    Column("Eigen-PC-raw_coding_rankscore", dest="eigen-pc.raw_coding_rankscore", transform=split_float_drop_na),
    Column("Eigen-PC-phred_coding", dest="eigen-pc.phred_coding", transform=split_float_drop_na),
    Column("GenoCanyon_score", transform=split_float_drop_na),
    Column("GenoCanyon_rankscore", transform=split_float_drop_na),
    Column("integrated_fitCons_score", dest="fitcons.integrated.score", transform=split_float_drop_na),
    Column("integrated_fitCons_rankscore", dest="fitcons.integrated.rankscore", transform=split_float_drop_na),
    Column("integrated_confidence_value", dest="fitcons.integrated.confidence_value", transform=split_int_drop_na),
    Column("GM12878_fitCons_score", dest="fitcons.gm12878.score", transform=split_float_drop_na),
    Column("GM12878_fitCons_rankscore", dest="fitcons.gm12878.rankscore", transform=split_float_drop_na),
    Column("GM12878_confidence_value", dest="fitcons.gm12878.confidence_value", transform=split_int_drop_na),
    Column("H1-hESC_fitCons_score", dest="fitcons.h1-hesc.score", transform=split_float_drop_na),
    Column("H1-hESC_fitCons_rankscore", dest="fitcons.h1-hesc.rankscore", transform=split_float_drop_na),
    Column("H1-hESC_confidence_value", dest="fitcons.h1-hesc.confidence_value", transform=split_int_drop_na),
    Column("HUVEC_fitCons_score", dest="fitcons.huvec.score", transform=split_float_drop_na),
    Column("HUVEC_fitCons_rankscore", dest="fitcons.huvec.rankscore", transform=split_float_drop_na),
    Column("HUVEC_confidence_value", dest="fitcons.huvec.confidence_value", transform=split_int_drop_na),
    Column("LINSIGHT", dest="linsight.score", transform=split_float_drop_na),
    Column("LINSIGHT_rankscore", transform=split_float_drop_na),
    Column("GERP++_NR", transform=split_float_drop_na),
    Column("GERP++_RS", transform=split_float_drop_na),
    Column("GERP++_RS_rankscore", dest="gerp++.rs_rankscore", transform=split_float_drop_na),
    Column("phyloP100way_vertebrate", dest="phylop.100way_vertebrate.score", transform=split_float_drop_na),
    Column("phyloP100way_vertebrate_rankscore", dest="phylop.100way_vertebrate.rankscore", transform=split_float_drop_na),
    Column("phyloP470way_mammalian", dest="phylop.470way_mammalian.score", transform=split_float_drop_na),  # replaced 30way_mammalian in 4.4.a
    Column("phyloP470way_mammalian_rankscore", dest="phylop.470way_mammalian.rankscore", transform=split_float_drop_na),  # replaced 30way_mammalian in 4.4.a
    Column("phyloP17way_primate", dest="phylop.17way_primate.score", transform=split_float_drop_na),
    Column("phyloP17way_primate_rankscore", dest="phylop.17way_primate.rankscore", transform=split_float_drop_na),
    Column("phastCons100way_vertebrate", dest="phastcons.100way_vertebrate.score", transform=split_float_drop_na),
    Column("phastCons100way_vertebrate_rankscore", dest="phastcons.100way_vertebrate.rankscore", transform=split_float_drop_na),
    Column("phastCons470way_mammalian", dest="phastcons.470way_mammalian.score", transform=split_float_drop_na),  # replaced 30way_mammalian in 4.4.a
    Column("phastCons470way_mammalian_rankscore", dest="phastcons.470way_mammalian.rankscore", transform=split_float_drop_na),  # replaced 30way_mammalian in 4.4.a
    Column("phastCons17way_primate", dest="phastcons.17way_primate.score", transform=split_float_drop_na),
    Column("phastCons17way_primate_rankscore", dest="phastcons.17way_primate.rankscore", transform=split_float_drop_na),
    Column("SiPhy_29way_pi", dest="siphy_29way.pi", transform=parse_siphy_29way_pi),
    Column("SiPhy_29way_logOdds", dest="siphy_29way.logodds_score", transform=split_float_drop_na),
    Column("SiPhy_29way_logOdds_rankscore", dest="siphy_29way.logodds_rankscore", transform=split_float_drop_na),
    Column("bStatistic", dest="bstatistic.score", transform=split_float_drop_na),
    Column("bStatistic_converted_rankscore", dest="bstatistic.converted_rankscore", transform=split_float_drop_na),
    Column("1000Gp3_AC", dest="1000gp3.ac", transform=int),
    Column("1000Gp3_AF", dest="1000gp3.af", transform=float),
    Column("1000Gp3_AFR_AC", dest="1000gp3.afr.ac", transform=int),  # dest changed since 4.4.a
    Column("1000Gp3_AFR_AF", dest="1000gp3.afr.af", transform=float),
    Column("1000Gp3_EUR_AC", dest="1000gp3.eur.ac", transform=int),
    Column("1000Gp3_EUR_AF", dest="1000gp3.eur.af", transform=float),
    Column("1000Gp3_AMR_AC", dest="1000gp3.amr.ac", transform=int),
    Column("1000Gp3_AMR_AF", dest="1000gp3.amr.af", transform=float),
    Column("1000Gp3_EAS_AC", dest="1000gp3.eas.ac", transform=int),
    Column("1000Gp3_EAS_AF", dest="1000gp3.eas.af", transform=float),
    Column("1000Gp3_SAS_AC", dest="1000gp3.sas.ac", transform=int),
    Column("1000Gp3_SAS_AF", dest="1000gp3.sas.af", transform=float),
    Column("TWINSUK_AC", dest="twinsuk.ac", transform=int),
    Column("TWINSUK_AF", dest="twinsuk.af", transform=float),
    Column("ALSPAC_AC", dest="alspac.ac", transform=int),
    Column("ALSPAC_AF", dest="alspac.af", transform=float),
    Column("UK10K_AC", dest="uk10k.ac", transform=int),
    Column("UK10K_AF", dest="uk10k.af", transform=float),
    Column("ESP6500_AA_AC", dest="esp6500.aa.ac", transform=int),  # dest changed since 4.4.a
    Column("ESP6500_AA_AF", dest="esp6500.aa.af", transform=float),
    Column("ESP6500_EA_AC", dest="esp6500.ea.ac", transform=int),
    Column("ESP6500_EA_AF", dest="esp6500.ea.af", transform=float),
    Column("ExAC_AC", dest="exac.ac", transform=int),  # dest changed since 4.4.a
    Column("ExAC_AF", dest="exac.af", transform=float),
    Column("ExAC_Adj_AC", dest="exac.adj_ac", transform=int),
    Column("ExAC_Adj_AF", dest="exac.adj_af", transform=float),
    Column("ExAC_AFR_AC", dest="exac.afr.ac", transform=int),
    Column("ExAC_AFR_AF", dest="exac.afr.af", transform=float),
    Column("ExAC_AMR_AC", dest="exac.amr.ac", transform=int),
    Column("ExAC_AMR_AF", dest="exac.amr.af", transform=float),
    Column("ExAC_EAS_AC", dest="exac.eas.ac", transform=int),
    Column("ExAC_EAS_AF", dest="exac.eas.af", transform=float),
    Column("ExAC_FIN_AC", dest="exac.fin.ac", transform=int),
    Column("ExAC_FIN_AF", dest="exac.fin.af", transform=float),
    Column("ExAC_NFE_AC", dest="exac.nfe.ac", transform=int),
    Column("ExAC_NFE_AF", dest="exac.nfe.af", transform=float),
    Column("ExAC_SAS_AC", dest="exac.sas.ac", transform=int),
    Column("ExAC_SAS_AF", dest="exac.sas.af", transform=float),
    Column("ExAC_nonTCGA_AC", dest="exac_nontcga.ac", transform=int),
    Column("ExAC_nonTCGA_AF", dest="exac_nontcga.af", transform=float),
    Column("ExAC_nonTCGA_Adj_AC", dest="exac_nontcga.adj_ac", transform=int),
    Column("ExAC_nonTCGA_Adj_AF", dest="exac_nontcga.adj_af", transform=float),
    Column("ExAC_nonTCGA_AFR_AC", dest="exac_nontcga.afr.ac", transform=int),
    Column("ExAC_nonTCGA_AFR_AF", dest="exac_nontcga.afr.af", transform=float),
    Column("ExAC_nonTCGA_AMR_AC", dest="exac_nontcga.amr.ac", transform=int),
    Column("ExAC_nonTCGA_AMR_AF", dest="exac_nontcga.amr.af", transform=float),
    Column("ExAC_nonTCGA_EAS_AC", dest="exac_nontcga.eas.ac", transform=int),
    Column("ExAC_nonTCGA_EAS_AF", dest="exac_nontcga.eas.af", transform=float),
    Column("ExAC_nonTCGA_FIN_AC", dest="exac_nontcga.fin.ac", transform=int),
    Column("ExAC_nonTCGA_FIN_AF", dest="exac_nontcga.fin.af", transform=float),
    Column("ExAC_nonTCGA_NFE_AC", dest="exac_nontcga.nfe.ac", transform=int),
    Column("ExAC_nonTCGA_NFE_AF", dest="exac_nontcga.nfe.af", transform=float),
    Column("ExAC_nonTCGA_SAS_AC", dest="exac_nontcga.sas.ac", transform=int),
    Column("ExAC_nonTCGA_SAS_AF", dest="exac_nontcga.sas.af", transform=float),
    Column("ExAC_nonpsych_AC", dest="exac_nonpsych.ac", transform=int),
    Column("ExAC_nonpsych_AF", dest="exac_nonpsych.af", transform=float),
    Column("ExAC_nonpsych_Adj_AC", dest="exac_nonpsych.adj_ac", transform=int),
    Column("ExAC_nonpsych_Adj_AF", dest="exac_nonpsych.adj_af", transform=float),
    Column("ExAC_nonpsych_AFR_AC", dest="exac_nonpsych.afr.ac", transform=int),
    Column("ExAC_nonpsych_AFR_AF", dest="exac_nonpsych.afr.af", transform=float),
    Column("ExAC_nonpsych_AMR_AC", dest="exac_nonpsych.amr.ac", transform=int),
    Column("ExAC_nonpsych_AMR_AF", dest="exac_nonpsych.amr.af", transform=float),
    Column("ExAC_nonpsych_EAS_AC", dest="exac_nonpsych.eas.ac", transform=int),
    Column("ExAC_nonpsych_EAS_AF", dest="exac_nonpsych.eas.af", transform=float),
    Column("ExAC_nonpsych_FIN_AC", dest="exac_nonpsych.fin.ac", transform=int),
    Column("ExAC_nonpsych_FIN_AF", dest="exac_nonpsych.fin.af", transform=float),
    Column("ExAC_nonpsych_NFE_AC", dest="exac_nonpsych.nfe.ac", transform=int),
    Column("ExAC_nonpsych_NFE_AF", dest="exac_nonpsych.nfe.af", transform=float),
    Column("ExAC_nonpsych_SAS_AC", dest="exac_nonpsych.sas.ac", transform=int),
    Column("ExAC_nonpsych_SAS_AF", dest="exac_nonpsych.sas.af", transform=float),
    Column("ALFA_European_AC", dest="alfa.european.ac", transform=int),
    Column("ALFA_European_AN", dest="alfa.european.an", transform=int),
    Column("ALFA_European_AF", dest="alfa.european.af", transform=float),
    Column("ALFA_African_Others_AC", dest="alfa.african_others.ac", transform=int),
    Column("ALFA_African_Others_AN", dest="alfa.african_others.an", transform=int),
    Column("ALFA_African_Others_AF", dest="alfa.african_others.af", transform=float),
    Column("ALFA_East_Asian_AC", dest="alfa.east_asian.ac", transform=int),
    Column("ALFA_East_Asian_AN", dest="alfa.east_asian.an", transform=int),
    Column("ALFA_East_Asian_AF", dest="alfa.east_asian.af", transform=float),
    Column("ALFA_African_American_AC", dest="alfa.african_american.ac", transform=int),
    Column("ALFA_African_American_AN", dest="alfa.african_american.an", transform=int),
    Column("ALFA_African_American_AF", dest="alfa.african_american.af", transform=float),
    Column("ALFA_Latin_American_1_AC", dest="alfa.latin_american_1.ac", transform=int),
    Column("ALFA_Latin_American_1_AN", dest="alfa.latin_american_1.an", transform=int),
    Column("ALFA_Latin_American_1_AF", dest="alfa.latin_american_1.af", transform=float),
    Column("ALFA_Latin_American_2_AC", dest="alfa.latin_american_2.ac", transform=int),
    Column("ALFA_Latin_American_2_AN", dest="alfa.latin_american_2.an", transform=int),
    Column("ALFA_Latin_American_2_AF", dest="alfa.latin_american_2.af", transform=float),
    Column("ALFA_Other_Asian_AC", dest="alfa.other_asian.ac", transform=int),
    Column("ALFA_Other_Asian_AN", dest="alfa.other_asian.an", transform=int),
    Column("ALFA_Other_Asian_AF", dest="alfa.other_asian.af", transform=float),
    Column("ALFA_South_Asian_AC", dest="alfa.south_asian.ac", transform=int),
    Column("ALFA_South_Asian_AN", dest="alfa.south_asian.an", transform=int),
    Column("ALFA_South_Asian_AF", dest="alfa.south_asian.af", transform=float),
    Column("ALFA_Other_AC", dest="alfa.other.ac", transform=int),
    Column("ALFA_Other_AN", dest="alfa.other.an", transform=int),
    Column("ALFA_Other_AF", dest="alfa.other.af", transform=float),
    Column("ALFA_African_AC", dest="alfa.african.ac", transform=int),
    Column("ALFA_African_AN", dest="alfa.african.an", transform=int),
    Column("ALFA_African_AF", dest="alfa.african.af", transform=float),
    Column("ALFA_Asian_AC", dest="alfa.asian.ac", transform=int),
    Column("ALFA_Asian_AN", dest="alfa.asian.an", transform=int),
    Column("ALFA_Asian_AF", dest="alfa.asian.af", transform=float),
    Column("ALFA_Total_AC", dest="alfa.total.ac", transform=int),
    Column("ALFA_Total_AN", dest="alfa.total.an", transform=int),
    Column("ALFA_Total_AF", dest="alfa.total.af", transform=float),
    Column("clinvar_id", dest="clinvar.clinvar_id", transform=split_clinvar),
    Column("clinvar_clnsig", transform=split_clinvar),
    Column("clinvar_trait", transform=split_clinvar),
    Column("clinvar_review", transform=split_clinvar),
    Column("clinvar_hgvs", transform=split_clinvar),
    Column("clinvar_var_source", dest="clinvar.var_source", transform=split_clinvar),
    Column("clinvar_MedGen_id", dest="clinvar.medgen", transform=split_clinvar),
    Column("clinvar_OMIM_id", dest="clinvar.omim", transform=split_clinvar),
    Column("clinvar_Orphanet_id", dest="clinvar.orphanet", transform=split_clinvar),
    Column("Interpro_domain", transform=split_str_drop_na),
    Column("GTEx_V8_gene", dest="gtex.gene", tag=COLUMN_TAG.GTEX_GENE),  # special column, see prune_gtex()
    Column("GTEx_V8_tissue", dest="gtex.tissue", tag=COLUMN_TAG.GTEX_TISSUE),  # special column, see prune_gtex()
    Column("Geuvadis_eQTL_target_gene", transform=split_str_drop_na)
]

HG19_COLUMNS = [c for c in COLUMNS if c.is_hg19()]
HG38_COLUMNS = [c for c in COLUMNS if c.is_hg38()]
PROTEIN_COLUMNS = [c for c in COLUMNS if c.dest.startswith(r"protein.")]

# Currently not necessary to make assembly-specific tag-column maps.
TAG_COLUMN_MAP = create_tag_column_map(COLUMNS)


def verify_pos(row, pos_column: Column, na_values: set = NA_VALUES):
    pos_value = row[pos_column.name]

    if pos_value in na_values:
        return False

    return True


def verify_hg19_row(row: dict, na_values: set = NA_VALUES):
    pos_column = TAG_COLUMN_MAP[COLUMN_TAG.HG19_POS][0]
    return verify_pos(row, pos_column=pos_column, na_values=na_values)


def verify_hg38_row(row: dict, na_values: set = NA_VALUES):
    pos_column = TAG_COLUMN_MAP[COLUMN_TAG.HG38_POS][0]
    return verify_pos(row, pos_column=pos_column, na_values=na_values)


def normalize_hg19_row(row: dict):
    """
    For unknown reasons, 4 MutationTaster columns and 6 Aloft columns have values ending in ";", which leads to an empty string when splitting the value by ";".
    This function remove the tailing ";" in those values.
    """
    columns = [
        # MutationTaster columns
        TAG_COLUMN_MAP[COLUMN_TAG.MUTATION_TASTER_AAE][0],
        TAG_COLUMN_MAP[COLUMN_TAG.MUTATION_TASTER_MODEL][0],
        TAG_COLUMN_MAP[COLUMN_TAG.MUTATION_TASTER_PRED][0],
        TAG_COLUMN_MAP[COLUMN_TAG.MUTATION_TASTER_SCORE][0],
        # Aloft columns
        TAG_COLUMN_MAP[COLUMN_TAG.ALOFT_FRACTION_TRANSCRIPTS_AFFECTED][0],
        TAG_COLUMN_MAP[COLUMN_TAG.ALOFT_PROB_TOLERANT][0],
        TAG_COLUMN_MAP[COLUMN_TAG.ALOFT_PROB_RECESSIVE][0],
        TAG_COLUMN_MAP[COLUMN_TAG.ALOFT_PROB_DOMINANT][0],
        TAG_COLUMN_MAP[COLUMN_TAG.ALOFT_PRED][0],
        TAG_COLUMN_MAP[COLUMN_TAG.ALOFT_CONFIDENCE][0]
    ]

    for c in columns:
        if row[c.name] and row[c.name][-1] == ";":
            row[c.name] = row[c.name][:-1]

    return row


def normalize_hg38_row(row: dict):
    return normalize_hg19_row(row)


def prune_gtex(raw_doc: dict, gene_column: Column, tissue_column: Column, na_values: set = NA_VALUES):
    """
    Map each GTEx gene name and tissue name from the raw document into a dictionary,
    and assign all such dictionaries to the raw document's top "gtex" field.

    E.g. with the following input value:

        row["gtex.gene"] = "ENOSF1|ENOSF1"
        row["gtex.tissue"] = "Adipose_Subcutaneous|Muscle_Skeletal"

    raw_doc will be assigned as:

         row["gtex"] = [
            {'gene': 'ENOSF1', 'tissue': 'Adipose_Subcutaneous'},
            {'gene': 'ENOSF1', 'tissue': 'Muscle_Skeletal'}
        ]
    """
    # when these two keys are not present in the doc, it means the responding two values in tsv files are NA values
    if (gene_column.dest in raw_doc) and (tissue_column.dest in raw_doc):
        gene_value = raw_doc[gene_column.dest]
        tissue_value = raw_doc[tissue_column.dest]

        # special separator "|" for GTEx
        gtex_result = [{"gene": acc, "tissue": entry} for (acc, entry) in split_zip([gene_value, tissue_value], sep=r"|", na_values=na_values)]
        gtex_result = _check_length(gtex_result)
        if gtex_result is not None:
            raw_doc["gtex"] = gtex_result

        del raw_doc[gene_column.dest]
        del raw_doc[tissue_column.dest]

    return raw_doc


def prune_mutation_taster(raw_doc: dict, aae_column: Column, model_column: Column, pred_column: Column, score_column: Column, na_values: set = NA_VALUES):
    """
    Map each MutationTaster AAE, model, pred, and score value from the raw document into a dictionary,
    and assign all such dictionaries to the raw document's "mutationtaster.analysis" field.

    E.g. with the following input value:

        row["mutationtaster.aae"] = "Y518*;Y518*;D532E"
        row["mutationtaster.model"] = "complex_aae;complex_aae;simple_aae"
        row["mutationtaster.pred"] = "D;D;N"
        row["mutationtaster.score"] = "1;1;1"

    raw_doc will be assigned as:

         row["mutationtaster.analysis"] = [
            {'aae': 'Y518*', 'model': 'complex_aae', 'pred': 'D', 'score': 1},
            {'aae': 'Y518*', 'model': 'complex_aae', 'pred': 'D', 'score': 1},
            {'aae': 'D532E', 'model': 'simple_aae', 'pred': 'N', 'score': 1}
        ]
    """
    if (aae_column.dest in raw_doc) and (model_column.dest in raw_doc) and (pred_column.dest in raw_doc) and (score_column.dest in raw_doc):
        aae_value = raw_doc[aae_column.dest]
        model_value = raw_doc[model_column.dest]
        pred_value = raw_doc[pred_column.dest]
        score_value = raw_doc[score_column.dest]

        analysis_values = split_zip([aae_value, model_value, pred_value, score_value], sep=r";", na_values=na_values)
        analysis_result = [{"aae": aae, "model": model, "pred": pred, "score": float(score)} for (aae, model, pred, score) in analysis_values]
        analysis_result = _check_length(analysis_result)
        if analysis_result is not None:
            raw_doc["mutationtaster.analysis"] = analysis_result

        del raw_doc[aae_column.dest]
        del raw_doc[model_column.dest]
        del raw_doc[pred_column.dest]
        del raw_doc[score_column.dest]

        # note that raw_doc[mutationtaster.converted_rankscore] is kept as-is

    return raw_doc


def prune_protein(raw_doc: set, protein_columns: list[Column]):
    protein_fields = {c.dest: raw_doc[c.dest] for c in protein_columns}

    # assert len(set(map(len, protein_fields.values()))) == 1  # assert all values (as lists) in protein_fields have the same length before zipping

    """
    Convert protein fields (as a dictionary of lists) to a list of dictionaries. E.g.
    
        protein_field = {
            'protein.transcriptid': ['ENST00000624406', 'ENST00000398168'],
            'protein.proteinid': ['ENSP00000485669', 'ENSP00000381234']
        }
        
    will be converted to
    
        protein_result = [
            {'protein.transcriptid': 'ENST00000624406', 'protein.proteinid': 'ENSP00000485669'},
            {'protein.transcriptid': 'ENST00000398168', 'protein.proteinid': 'ENSP00000381234'}
        ]
    """
    protein_result = []
    protein_keys = protein_fields.keys()
    for protein_values in zip(*protein_fields.values()):
        elem = dict((key, value) for key, value in zip(protein_keys, protein_values) if value is not None)
        elem = parse_dot_fields(elem)["protein"]
        protein_result.append(elem)
    # We keep protein_result as a list for easier merging
    # protein_result = _check_length(protein_result)
    # if protein_result is not None:
    #     raw_doc["protein"] = protein_result
    raw_doc["protein"] = protein_result

    for c in protein_columns:
        del raw_doc[c.dest]

    return raw_doc


def prune_hg19_doc(doc: dict, na_values: set = NA_VALUES):
    protein_columns = [c for c in PROTEIN_COLUMNS if c.dest in doc]
    doc = prune_protein(doc, protein_columns=protein_columns)

    gtex_gene_column = TAG_COLUMN_MAP[COLUMN_TAG.GTEX_GENE][0]
    gtex_tissue_column = TAG_COLUMN_MAP[COLUMN_TAG.GTEX_TISSUE][0]
    doc = prune_gtex(doc, gene_column=gtex_gene_column, tissue_column=gtex_tissue_column, na_values=na_values)

    mutation_taster_aae_column = TAG_COLUMN_MAP[COLUMN_TAG.MUTATION_TASTER_AAE][0]
    mutation_taster_model_column = TAG_COLUMN_MAP[COLUMN_TAG.MUTATION_TASTER_MODEL][0]
    mutation_taster_pred_column = TAG_COLUMN_MAP[COLUMN_TAG.MUTATION_TASTER_PRED][0]
    mutation_taster_score_column = TAG_COLUMN_MAP[COLUMN_TAG.MUTATION_TASTER_SCORE][0]
    doc = prune_mutation_taster(doc, aae_column=mutation_taster_aae_column, model_column=mutation_taster_model_column,
                                pred_column=mutation_taster_pred_column, score_column=mutation_taster_score_column, na_values=na_values)

    return doc


def prune_hg38_doc(doc: dict, na_values: set = NA_VALUES):
    return prune_hg19_doc(doc, na_values=na_values)


def construct_raw_doc(row: dict, columns: list, na_values: set = NA_VALUES):
    """
    Construct a raw dbnsfp doc from a dict-like row read from the csv file.
    "Raw" means 1) the doc may contain dot fields that are not parsed, and 2) some values in the doc need further treatment/processing.

    Args:
        row: a dict representing a csv row's content
        columns: a list of Column object indicating how to construct each column
        na_values: a set of values seen as NA
    Returns:
        a dict representing the doc's json object
    """
    result = dict()

    for column in columns:
        value = row[column.name]
        if value in na_values:
            continue

        value = column.transform(value)
        if value is None:
            continue

        result[column.dest] = value

    return result


def construct_hg19_raw_doc(row: dict, na_values: set = NA_VALUES):
    return construct_raw_doc(row, columns=HG19_COLUMNS, na_values=na_values)


def construct_hg38_raw_doc(row: dict, na_values: set = NA_VALUES):
    return construct_raw_doc(row, columns=HG38_COLUMNS, na_values=na_values)


def make_hgvs_id(doc: dict, chrom_column: Column, pos_column: Column, ref_column: Column, alt_column: Column):
    chrom_value = doc[chrom_column.dest]
    pos_value = doc[pos_column.dest]["start"]  # see make_zero_based()
    ref_value = doc[ref_column.dest]
    alt_value = doc[alt_column.dest]

    hgvs_id = "chr%s:g.%d%s>%s" % (chrom_value, pos_value, ref_value, alt_value)
    return hgvs_id


def make_hg19_hgvs_id(doc: dict):
    chrom_column = TAG_COLUMN_MAP[COLUMN_TAG.HG19_CHROM][0]
    pos_column = TAG_COLUMN_MAP[COLUMN_TAG.HG19_POS][0]
    ref_column = TAG_COLUMN_MAP[COLUMN_TAG.REF_ALLELE][0]
    alt_column = TAG_COLUMN_MAP[COLUMN_TAG.ALT_ALLELE][0]

    return make_hgvs_id(doc, chrom_column=chrom_column, pos_column=pos_column, ref_column=ref_column, alt_column=alt_column)


def make_hg38_hgvs_id(doc: dict):
    chrom_column = TAG_COLUMN_MAP[COLUMN_TAG.HG38_CHROM][0]
    pos_column = TAG_COLUMN_MAP[COLUMN_TAG.HG38_POS][0]
    ref_column = TAG_COLUMN_MAP[COLUMN_TAG.REF_ALLELE][0]
    alt_column = TAG_COLUMN_MAP[COLUMN_TAG.ALT_ALLELE][0]

    return make_hgvs_id(doc, chrom_column=chrom_column, pos_column=pos_column, ref_column=ref_column, alt_column=alt_column)


def construct_hg19_doc(row: dict, na_values: set = NA_VALUES):
    verified = verify_hg19_row(row, na_values=na_values)
    if not verified:
        return None

    row = normalize_hg19_row(row)
    raw_doc = construct_hg19_raw_doc(row, na_values=na_values)
    raw_doc = prune_hg19_doc(raw_doc, na_values=na_values)
    hgvs_id = make_hg19_hgvs_id(raw_doc)

    doc = {
        "_id": hgvs_id,
        "dbnsfp": parse_dot_fields(raw_doc)  # convert dot-fields into nested dictionaries
    }
    return doc


def construct_hg38_doc(row: dict, na_values: set = NA_VALUES):
    verified = verify_hg38_row(row, na_values=na_values)
    if not verified:
        return None

    row = normalize_hg38_row(row)
    raw_doc = construct_hg38_raw_doc(row, na_values=na_values)
    raw_doc = prune_hg38_doc(raw_doc, na_values=na_values)
    hgvs_id = make_hg38_hgvs_id(raw_doc)

    doc = {
        "_id": hgvs_id,
        "dbnsfp": parse_dot_fields(raw_doc)  # convert dot-fields into nested dictionaries
    }
    return doc


def load_file(path: str, assembly: str):
    file = anyfile(path)
    file_reader = csv.DictReader(file, delimiter="\t")

    num_columns = len(file_reader.fieldnames)
    assert num_columns == VALID_COLUMN_NO, "Expecting %s columns, but got %s" % (VALID_COLUMN_NO, num_columns)

    _construct_doc = None
    match assembly:
        case "hg19":
            _construct_doc = construct_hg19_doc
        case "hg38":
            _construct_doc = construct_hg38_doc
        case _:
            raise ValueError(f"Cannot recognize assembly. Accept 'hg19' or 'hg38', got '{assembly}'.")

    last_doc = None
    for row in file_reader:
        curr_doc = _construct_doc(row, na_values=NA_VALUES)

        if curr_doc is None:
            continue

        if last_doc is not None:
            if curr_doc["_id"] == last_doc["_id"]:
                last_protein_field = last_doc["dbnsfp"]["protein"]
                curr_protein_field = curr_doc["dbnsfp"]["protein"]

                # We guarantee that the protein field is always a list at this moment. See prune_protein()
                # if not isinstance(last_protein_field, list):
                #     last_protein_field = [last_protein_field]
                last_protein_field.extend(curr_protein_field)

                last_doc["dbnsfp"]["protein"] = last_protein_field
                continue
            else:
                if len(last_doc["dbnsfp"]["protein"]) == 1:
                    last_doc["dbnsfp"]["protein"] = last_doc["dbnsfp"]["protein"][0]
                yield last_doc

        last_doc = curr_doc

    # yield the very last doc
    if last_doc:
        if len(last_doc["dbnsfp"]["protein"]) == 1:
            last_doc["dbnsfp"]["protein"] = last_doc["dbnsfp"]["protein"][0]
        yield last_doc

    file.close()
