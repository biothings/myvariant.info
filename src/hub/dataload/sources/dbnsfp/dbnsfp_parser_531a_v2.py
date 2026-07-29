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
# VALID_COLUMN_NO = 689  # for 4.4a
# VALID_COLUMN_NO = 708  # for 4.5a
# VALID_COLUMN_NO = 714  # for 4.6a
# VALID_COLUMN_NO = 450  # for 4.7a
# VALID_COLUMN_NO = 456  # for 4.8a
# VALID_COLUMN_NO = 458  # for 4.9a
VALID_COLUMN_NO = 505  # for 5.3.1a

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

# A tag can be any string value; columns with the same tag are looked-up as a group
COLUMN_TAG = SimpleNamespace()
COLUMN_TAG.HG38_POS = "hg38_pos"  # for "pos(1-based)"
COLUMN_TAG.HG19_POS = "hg19_pos"  # for "hg19_pos(1-based)"
COLUMN_TAG.HG38_CHROM = "hg38_chrom"  # for "#chr"
COLUMN_TAG.HG19_CHROM = "hg19_chrom"  # for "hg19_chr"
COLUMN_TAG.REF_ALLELE = "ref"
COLUMN_TAG.ALT_ALLELE = "alt"
# GTEx, eQTLGen, and Geuvadis eQTL columns retired by dbNSFP 5.0 (no longer in the variant file)
# MutationTaster_AAE retired and per-transcript tree count columns added when dbNSFP 5.0 adopted MutationTaster2021
COLUMN_TAG.MUTATION_TASTER_MODEL = "MutationTaster_model"
COLUMN_TAG.MUTATION_TASTER_PRED = "MutationTaster_pred"
COLUMN_TAG.MUTATION_TASTER_SCORE = "MutationTaster_score"
COLUMN_TAG.MUTATION_TASTER_TREES_BENIGN = "MutationTaster_trees_benign"
COLUMN_TAG.MUTATION_TASTER_TREES_DELETERIOUS = "MutationTaster_trees_deleterious"
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
    # Column("hs1_chr"),  # Not Used, same rationale as hg18_chr above (chrom label doesn't vary by build)
    Column("hs1_pos(1-based)", dest="hs1", transform=make_zero_based),  # hs1/T2T-CHM13 v2.0 coordinates, added in dbNSFP 5.3.1; stored on both hg19 and hg38 docs like hg18
    Column("aapos", dest="protein.aa.pos", transform=split_int),
    Column("genename", dest="protein.genename", transform=split_str),
    Column("Ensembl_geneid", dest="protein.geneid", transform=split_str),
    Column("Ensembl_transcriptid", dest="protein.transcriptid", transform=split_str),
    Column("Ensembl_proteinid", dest="protein.proteinid", transform=split_str),
    Column("Uniprot_acc", dest="protein.uniprot.acc", transform=split_str),
    Column("Uniprot_entry", dest="protein.uniprot.entry", transform=split_str),
    # HGVSc_ANNOVAR and HGVSp_ANNOVAR retired by dbNSFP 5.0; only snpEff and VEP sources remain
    Column("HGVSc_snpEff", dest="protein.hgvsc.snpeff", transform=split_str),
    Column("HGVSp_snpEff", dest="protein.hgvsp.snpeff", transform=split_str),
    Column("HGVSc_VEP", dest="protein.hgvsc.vep", transform=split_str),
    Column("HGVSp_VEP", dest="protein.hgvsp.vep", transform=split_str),
    Column("APPRIS", dest="protein.appris", transform=split_str),
    Column("GENCODE_basic", dest="protein.gencode_basic", transform=split_str),
    Column("TSL", dest="protein.tsl", transform=split_int),
    Column("VEP_canonical", dest="protein.vep_canonical", transform=split_str),
    Column("MANE", dest="protein.mane", transform=split_str),  # added in dbNSFP 5.0; per-transcript canonical designation
    Column("cds_strand", dest="cds_strand", transform=split_str_drop_na),
    Column("refcodon", dest="protein.aa.refcodon", transform=split_str),
    Column("codonpos", dest="protein.aa.codonpos", transform=split_int),
    Column("codon_degeneracy", dest="protein.aa.codon_degeneracy", transform=split_int),
    Column("Ancestral_allele", dest="ancestral_allele", transform=split_str_drop_na),
    Column("AltaiNeandertal", dest="altai_neandertal", transform=split_genotype),
    Column("Denisova", transform=split_genotype),
    Column("VindijiaNeandertal", dest="vindijia_neandertal", transform=split_genotype),
    Column("ChagyrskayaNeandertal", dest="chagyrskaya_neandertal", transform=split_genotype),
    # Note: clinvar and Interpro_domain appear at different column positions than in dbNSFP 4.9a; no code impact (DictReader is order-independent)
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
    # LRT retired by dbNSFP 5.0
    Column("MutationTaster_score", tag=COLUMN_TAG.MUTATION_TASTER_SCORE),
    Column("MutationTaster_rankscore", dest="mutationtaster.rankscore", transform=split_float_drop_na),  # renamed from MutationTaster_converted_rankscore when dbNSFP 5.0 adopted MutationTaster2021
    Column("MutationTaster_pred", tag=COLUMN_TAG.MUTATION_TASTER_PRED),
    Column("MutationTaster_model", tag=COLUMN_TAG.MUTATION_TASTER_MODEL),
    Column("MutationTaster_trees_benign", tag=COLUMN_TAG.MUTATION_TASTER_TREES_BENIGN),  # added in dbNSFP 5.0; per-transcript benign tree count
    Column("MutationTaster_trees_deleterious", tag=COLUMN_TAG.MUTATION_TASTER_TREES_DELETERIOUS),  # added in dbNSFP 5.0; per-transcript deleterious tree count
    # MutationTaster_AAE retired by dbNSFP 5.0 (tied to the pre-2021 MutationTaster model)
    Column("MutationAssessor_score", dest="protein.mutationassessor.score", transform=split_float),
    Column("MutationAssessor_rankscore", transform=split_float_drop_na),
    Column("MutationAssessor_pred", dest="protein.mutationassessor.pred", transform=split_str),
    # FATHMM retired by dbNSFP 5.0
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
    # MutPred (v1) replaced by MutPred2 in dbNSFP 5.2
    Column("MutPred2_score", dest="mutpred2.score", transform=split_float_drop_na),  # added in dbNSFP 5.2
    Column("MutPred2_rankscore", dest="mutpred2.rankscore", transform=split_float_drop_na),  # added in dbNSFP 5.2
    Column("MutPred2_pred", dest="mutpred2.pred", transform=split_str_drop_na),  # added in dbNSFP 5.2
    Column("MutPred2_top5_mechanisms", dest="mutpred2.mechanisms", transform=parse_mutpred_top5features),  # added in dbNSFP 5.2
    Column("MVP_score", dest="protein.mvp.score", transform=split_float),
    Column("MVP_rankscore", transform=split_float_drop_na),
    Column("gMVP_score", dest="protein.gmvp.score", transform=split_float),
    Column("gMVP_rankscore", transform=split_float_drop_na),
    Column("MisFit_D_score", dest="misfit.d.score", transform=split_float_drop_na),  # added in dbNSFP 5.3
    Column("MisFit_D_rankscore", dest="misfit.d.rankscore", transform=split_float_drop_na),  # added in dbNSFP 5.3
    Column("MisFit_D_pred_lenient", dest="misfit.d.pred_lenient", transform=split_str_drop_na),  # added in dbNSFP 5.3
    Column("MisFit_D_pred_stringent", dest="misfit.d.pred_stringent", transform=split_str_drop_na),  # added in dbNSFP 5.3
    Column("MisFit_S_score", dest="misfit.s.score", transform=split_float_drop_na),  # added in dbNSFP 5.3
    Column("MisFit_S_rankscore", dest="misfit.s.rankscore", transform=split_float_drop_na),  # added in dbNSFP 5.3
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
    Column("VARITY_R_score", transform=split_float_drop_na),
    Column("VARITY_R_rankscore", transform=split_float_drop_na),
    Column("VARITY_ER_score", transform=split_float_drop_na),
    Column("VARITY_ER_rankscore", transform=split_float_drop_na),
    Column("VARITY_R_LOO_score", dest="varity.r_loo.score", transform=split_float_drop_na),
    Column("VARITY_R_LOO_rankscore", dest="varity.r_loo.rankscore", transform=split_float_drop_na),
    Column("VARITY_ER_LOO_score", dest="varity.er_loo.score", transform=split_float_drop_na),
    Column("VARITY_ER_LOO_rankscore", dest="varity.er_loo.rankscore", transform=split_float_drop_na),
    Column("ESM1b_score", dest="esm1b.score", transform=split_float_drop_na),
    Column("ESM1b_converted_rankscore", dest="esm1b.converted_rankscore", transform=split_float_drop_na),  # renamed from ESM1b_rankscore when dbNSFP 5.2 updated ESM1b scoring
    Column("ESM1b_pred", dest="esm1b.pred", transform=split_str_drop_na),
    # EVE retired by dbNSFP 5.0
    Column("AlphaMissense_score", dest="alphamissense.score", transform=split_float_drop_na),
    Column("AlphaMissense_rankscore", dest="alphamissense.rankscore", transform=split_float_drop_na),
    Column("AlphaMissense_pred", dest="alphamissense.pred", transform=split_str_drop_na),
    Column("PHACTboost_score", dest="phactboost.score", transform=split_float_drop_na),
    Column("PHACTboost_rankscore", dest="phactboost.rankscore", transform=split_float_drop_na),
    Column("MutFormer_score", dest="mutformer.score", transform=split_float_drop_na),
    Column("MutFormer_rankscore", dest="mutformer.rankscore", transform=split_float_drop_na),
    Column("MutScore_score", dest="mutscore.score", transform=split_float_drop_na),
    Column("MutScore_rankscore", dest="mutscore.rankscore", transform=split_float_drop_na),
    Column("popEVE_score", dest="popeve.score", transform=split_float_drop_na),  # new in 5.3.1a
    Column("popEVE_pred", dest="popeve.pred", transform=split_str_drop_na),  # new in 5.3.1a
    Column("popEVE_converted_rankscore", dest="popeve.converted_rankscore", transform=split_float_drop_na),  # new in 5.3.1a
    Column("Aloft_Fraction_transcripts_affected", dest="protein.aloft.fraction_transcripts_affected", transform=split_str, tag=COLUMN_TAG.ALOFT_FRACTION_TRANSCRIPTS_AFFECTED),
    Column("Aloft_prob_Tolerant", dest="protein.aloft.prob_tolerant", transform=split_str, tag=COLUMN_TAG.ALOFT_PROB_TOLERANT),
    Column("Aloft_prob_Recessive", dest="protein.aloft.prob_recessive", transform=split_str, tag=COLUMN_TAG.ALOFT_PROB_RECESSIVE),
    Column("Aloft_prob_Dominant", dest="protein.aloft.prob_dominant", transform=split_str, tag=COLUMN_TAG.ALOFT_PROB_DOMINANT),
    Column("Aloft_pred", dest="protein.aloft.pred", transform=split_str, tag=COLUMN_TAG.ALOFT_PRED),
    Column("Aloft_Confidence", dest="protein.aloft.confidence", transform=split_str, tag=COLUMN_TAG.ALOFT_CONFIDENCE),
    Column("CADD_raw", dest="cadd.raw_score", transform=split_float_drop_na, assembly="hg38"),
    Column("CADD_raw_rankscore", dest="cadd.raw_rankscore", transform=split_float_drop_na, assembly="hg38"),
    Column("CADD_phred", transform=split_float_drop_na, assembly="hg38"),
    Column("DANN_score", transform=split_float_drop_na),
    Column("DANN_rankscore", transform=split_float_drop_na),
    # fathmm-MKL retired by dbNSFP 5.0
    Column("fathmm-XF_coding_score", dest="fathmm-xf.coding_score", transform=split_float_drop_na),
    Column("fathmm-XF_coding_rankscore", dest="fathmm-xf.coding_rankscore", transform=split_float_drop_na),
    Column("fathmm-XF_coding_pred", dest="fathmm-xf.coding_pred", transform=split_str_drop_na),
    Column("Eigen-raw_coding", dest="eigen.raw_coding", transform=split_float_drop_na),
    Column("Eigen-raw_coding_rankscore", dest="eigen.raw_coding_rankscore", transform=split_float_drop_na),
    Column("Eigen-phred_coding", dest="eigen.phred_coding", transform=split_float_drop_na),
    Column("Eigen-PC-raw_coding", dest="eigen-pc.raw_coding", transform=split_float_drop_na),
    Column("Eigen-PC-raw_coding_rankscore", dest="eigen-pc.raw_coding_rankscore", transform=split_float_drop_na),
    Column("Eigen-PC-phred_coding", dest="eigen-pc.phred_coding", transform=split_float_drop_na),
    # GenoCanyon retired by dbNSFP 5.0
    # fitCons (integrated, GM12878, H1-hESC, HUVEC) retired by dbNSFP 5.0
    # LINSIGHT retired by dbNSFP 5.0
    Column("GERP++_NR", transform=split_float_drop_na),
    Column("GERP++_RS", transform=split_float_drop_na),
    Column("GERP++_RS_rankscore", dest="gerp++.rs_rankscore", transform=split_float_drop_na),
    Column("GERP_92_mammals", dest="gerp.92_mammals.score", transform=split_float_drop_na),  # added as GERP_91_mammals in dbNSFP 4.8; renamed to GERP_92_mammals in dbNSFP 5.3
    Column("GERP_92_mammals_rankscore", dest="gerp.92_mammals.rankscore", transform=split_float_drop_na),  # ditto
    Column("phyloP100way_vertebrate", dest="phylop.100way_vertebrate.score", transform=split_float_drop_na),
    Column("phyloP100way_vertebrate_rankscore", dest="phylop.100way_vertebrate.rankscore", transform=split_float_drop_na),
    Column("phyloP470way_mammalian", dest="phylop.470way_mammalian.score", transform=split_float_drop_na),
    Column("phyloP470way_mammalian_rankscore", dest="phylop.470way_mammalian.rankscore", transform=split_float_drop_na),
    Column("phyloP17way_primate", dest="phylop.17way_primate.score", transform=split_float_drop_na),
    Column("phyloP17way_primate_rankscore", dest="phylop.17way_primate.rankscore", transform=split_float_drop_na),
    Column("phastCons100way_vertebrate", dest="phastcons.100way_vertebrate.score", transform=split_float_drop_na),
    Column("phastCons100way_vertebrate_rankscore", dest="phastcons.100way_vertebrate.rankscore", transform=split_float_drop_na),
    Column("phastCons470way_mammalian", dest="phastcons.470way_mammalian.score", transform=split_float_drop_na),
    Column("phastCons470way_mammalian_rankscore", dest="phastcons.470way_mammalian.rankscore", transform=split_float_drop_na),
    Column("phastCons17way_primate", dest="phastcons.17way_primate.score", transform=split_float_drop_na),
    Column("phastCons17way_primate_rankscore", dest="phastcons.17way_primate.rankscore", transform=split_float_drop_na),
    # SiPhy retired by dbNSFP 5.0
    Column("bStatistic", dest="bstatistic.score", transform=split_float_drop_na),
    Column("bStatistic_converted_rankscore", dest="bstatistic.converted_rankscore", transform=split_float_drop_na),
    Column("1000Gp3_AC", dest="1000gp3.ac", transform=int),
    Column("1000Gp3_AF", dest="1000gp3.af", transform=float),
    Column("1000Gp3_AFR_AC", dest="1000gp3.afr.ac", transform=int),
    Column("1000Gp3_AFR_AF", dest="1000gp3.afr.af", transform=float),
    Column("1000Gp3_EUR_AC", dest="1000gp3.eur.ac", transform=int),
    Column("1000Gp3_EUR_AF", dest="1000gp3.eur.af", transform=float),
    Column("1000Gp3_AMR_AC", dest="1000gp3.amr.ac", transform=int),
    Column("1000Gp3_AMR_AF", dest="1000gp3.amr.af", transform=float),
    Column("1000Gp3_EAS_AC", dest="1000gp3.eas.ac", transform=int),
    Column("1000Gp3_EAS_AF", dest="1000gp3.eas.af", transform=float),
    Column("1000Gp3_SAS_AC", dest="1000gp3.sas.ac", transform=int),
    Column("1000Gp3_SAS_AF", dest="1000gp3.sas.af", transform=float),
    # TWINSUK, ALSPAC, UK10K, ESP6500, ExAC, ExAC_nonTCGA, ExAC_nonpsych retired by dbNSFP 5.0
    # TOPMed freeze8 (3 cols, added 5.0), gnomAD2.1.1 exomes controls/non_neuro/non_cancer (109 cols, added 5.0),
    # gnomAD4.1 joint (45 cols, updated to v4.1 in 5.0), All of Us (28 cols, added 5.1), and RegeneronME (84 cols,
    # added 5.1) are in the file but not parsed here (counted in VALID_COLUMN_NO only), consistent with gnomAD
    # never being expanded into individual columns in earlier versions either (e.g. 4.8a)
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
    # dbNSFP-computed POPMAX across all population databases (added in dbNSFP 5.1)
    Column("dbNSFP_POPMAX_AF", dest="dbnsfp_popmax.af", transform=float),
    Column("dbNSFP_POPMAX_AC", dest="dbnsfp_popmax.ac", transform=int),
    Column("dbNSFP_POPMAX_POP", dest="dbnsfp_popmax.pop"),
    # GTEx, eQTLGen, and Geuvadis eQTL columns retired by dbNSFP 5.0
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
    For unknown reasons, MutationTaster columns and Aloft columns have values ending in ";", which leads to an empty
    string when splitting the value by ";". This function removes the trailing ";" in those values.
    In dbNSFP 5.0, MutationTaster_AAE was removed and MutationTaster_trees_benign/deleterious were added (MutationTaster2021 model).
    """
    columns = [
        # MutationTaster per-transcript columns
        TAG_COLUMN_MAP[COLUMN_TAG.MUTATION_TASTER_MODEL][0],
        TAG_COLUMN_MAP[COLUMN_TAG.MUTATION_TASTER_PRED][0],
        TAG_COLUMN_MAP[COLUMN_TAG.MUTATION_TASTER_SCORE][0],
        TAG_COLUMN_MAP[COLUMN_TAG.MUTATION_TASTER_TREES_BENIGN][0],
        TAG_COLUMN_MAP[COLUMN_TAG.MUTATION_TASTER_TREES_DELETERIOUS][0],
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


def prune_mutation_taster(raw_doc: dict, model_column: Column, pred_column: Column, score_column: Column,
                           trees_benign_column: Column, trees_deleterious_column: Column, na_values: set = NA_VALUES):
    """
    Map each MutationTaster model, pred, score, trees_benign, and trees_deleterious value from the raw document
    into a dictionary, and assign all such dictionaries to the raw document's "mutationtaster.analysis" field.
    In dbNSFP 5.0, MutationTaster_AAE was removed and two new tree count columns were added (MutationTaster2021 model).

    E.g. with the following input value:

        row["mutationtaster.model"] = "complex_aae;complex_aae;simple_aae"
        row["mutationtaster.pred"] = "D;D;N"
        row["mutationtaster.score"] = "1;1;1"
        row["mutationtaster.trees_benign"] = "0;0;45"
        row["mutationtaster.trees_deleterious"] = "100;100;55"

    raw_doc will be assigned as:

         row["mutationtaster.analysis"] = [
            {'model': 'complex_aae', 'pred': 'D', 'score': 1, 'trees_benign': 0, 'trees_deleterious': 100},
            {'model': 'complex_aae', 'pred': 'D', 'score': 1, 'trees_benign': 0, 'trees_deleterious': 100},
            {'model': 'simple_aae', 'pred': 'N', 'score': 1, 'trees_benign': 45, 'trees_deleterious': 55}
        ]
    """
    required_columns = [model_column, pred_column, score_column, trees_benign_column, trees_deleterious_column]
    if all(c.dest in raw_doc for c in required_columns):
        model_value = raw_doc[model_column.dest]
        pred_value = raw_doc[pred_column.dest]
        score_value = raw_doc[score_column.dest]
        trees_benign_value = raw_doc[trees_benign_column.dest]
        trees_deleterious_value = raw_doc[trees_deleterious_column.dest]

        analysis_values = split_zip(
            [model_value, pred_value, score_value, trees_benign_value, trees_deleterious_value],
            sep=r";",
            na_values=na_values
        )
        analysis_result = [
            {
                "model": model,
                "pred": pred,
                "score": float(score) if score is not None else None,
                "trees_benign": int(trees_benign) if trees_benign is not None else None,
                "trees_deleterious": int(trees_deleterious) if trees_deleterious is not None else None
            }
            for (model, pred, score, trees_benign, trees_deleterious) in analysis_values
        ]
        # Remove None values from each analysis entry
        analysis_result = [{k: v for k, v in entry.items() if v is not None} for entry in analysis_result]
        analysis_result = _check_length(analysis_result)
        if analysis_result is not None:
            raw_doc["mutationtaster.analysis"] = analysis_result

        for c in required_columns:
            del raw_doc[c.dest]

        # note that raw_doc["mutationtaster.rankscore"] is kept as-is

    return raw_doc


def prune_protein(raw_doc: set, protein_columns: list[Column]):
    protein_fields = {c.dest: raw_doc[c.dest] for c in protein_columns}

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
    raw_doc["protein"] = protein_result

    for c in protein_columns:
        del raw_doc[c.dest]

    return raw_doc


def prune_hg19_doc(doc: dict, na_values: set = NA_VALUES):
    protein_columns = [c for c in PROTEIN_COLUMNS if c.dest in doc]
    doc = prune_protein(doc, protein_columns=protein_columns)

    mutation_taster_model_column = TAG_COLUMN_MAP[COLUMN_TAG.MUTATION_TASTER_MODEL][0]
    mutation_taster_pred_column = TAG_COLUMN_MAP[COLUMN_TAG.MUTATION_TASTER_PRED][0]
    mutation_taster_score_column = TAG_COLUMN_MAP[COLUMN_TAG.MUTATION_TASTER_SCORE][0]
    mutation_taster_trees_benign_column = TAG_COLUMN_MAP[COLUMN_TAG.MUTATION_TASTER_TREES_BENIGN][0]
    mutation_taster_trees_deleterious_column = TAG_COLUMN_MAP[COLUMN_TAG.MUTATION_TASTER_TREES_DELETERIOUS][0]
    doc = prune_mutation_taster(
        doc,
        model_column=mutation_taster_model_column,
        pred_column=mutation_taster_pred_column,
        score_column=mutation_taster_score_column,
        trees_benign_column=mutation_taster_trees_benign_column,
        trees_deleterious_column=mutation_taster_trees_deleterious_column,
        na_values=na_values
    )

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
    if VALID_COLUMN_NO is not None:
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
