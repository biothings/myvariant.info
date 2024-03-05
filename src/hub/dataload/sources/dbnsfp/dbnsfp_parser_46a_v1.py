import re
import csv
from enum import Flag
from dataclasses import dataclass
from itertools import chain
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
VALID_COLUMN_NO = 714  # for 4.6a

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

COLUMN_TAG = SimpleNamespace()
COLUMN_TAG.HG38_POS = "hg38_pos"  # for "pos(1-based)"
COLUMN_TAG.HG19_POS = "hg19_pos"  # for "hg19_pos(1-based)"
COLUMN_TAG.HG38_CHROM = "hg38_chrom"  # for "#chr"
COLUMN_TAG.HG19_CHROM = "hg19_chrom"  # for "hg19_chr"
COLUMN_TAG.REF_ALLELE = "ref"
COLUMN_TAG.ALT_ALLELE = "alt"
COLUMN_TAG.UNIPROT_ACC = "uniprot_acc"
COLUMN_TAG.UNIPROT_ENTRY = "uniprot_entry"
COLUMN_TAG.HGVS_CODING = "hgvsc"  # for "HGVSc_ANNOVAR", "HGVSc_snpEff", and "HGVSc_VEP"
COLUMN_TAG.HGVS_PROTEIN = "hgvsp"  # for "HGVSp_ANNOVAR", "HGVSp_snpEff", and "HGVSp_VEP"
COLUMN_TAG.GTEX_EQTL_GENE = "gtex_eqtl_gene"
COLUMN_TAG.GTEX_EQTL_TISSUE = "gtex_eqtl_tissue"
COLUMN_TAG.GTEX_SQTL_GENE = "gtex_sqtl_gene"
COLUMN_TAG.GTEX_SQTL_TISSUE = "gtex_sqtl_tissue"


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


def split(sep: str, na_values: set = NA_VALUES):
    def _func(value: str):
        result = [v for v in value.split(sep) if v not in na_values]
        return _check_length(result)

    return _func


def split_cast(sep: str, astype: Callable, na_values: set = NA_VALUES):
    def _func(value: str):
        result = [astype(v) for v in value.split(sep) if v not in na_values]
        return _check_length(result)

    return _func


# transforming functions for common data sources
split_str = split(";")
split_float = split_cast(";", float)
split_int = split_cast(";", int)

# transforming functions for specific data sources
split_clinvar = split(r"|")
split_genotype = split(r"/")  # for "AltaiNeandertal", "Denisova", "VindijiaNeandertal", and "ChagyrskayaNeandertal"


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


def split_zip(a_value: str, b_value: str, sep: str, na_values: set = NA_VALUES):
    """
    Split a_value and b_value by sep into two lists, and generate pairs from the two lists.

    This function assumes that the split two lists have the same length.

    E.g. with the following input,

        a_value = "P54578-2;P54578-3;A6NJA2;P54578"
        b_value = UBP14_HUMAN;UBP14_HUMAN;A6NJA2_HUMAN;UBP14_HUMAN

    the returned generator can make:

        [('P54578-2', 'UBP14_HUMAN'),
         ('P54578-3', 'UBP14_HUMAN'),
         ('A6NJA2', 'A6NJA2_HUMAN'),
         ('P54578', 'UBP14_HUMAN')]
    """
    a_list = [v if v not in na_values else None for v in a_value.split(sep)]
    b_list = [v if v not in na_values else None for v in b_value.split(sep)]

    result = ((a, b) for (a, b) in zip(a_list, b_list) if (a, b) != (None, None))
    # DO NOT use _check_length(result) otherwise the generator will be consumed
    return result


def split_dedup(values: list, sep: str, na_values: set = NA_VALUES):
    """
    Split each value from the input values by the separator, merge all the split results, and remove duplicates from the merged result.

    E.g. when values=["a;b;c", "b;c", "d"] and sep=";", the result is ["a", "b", "c", "d"]
    """
    value_list = [value.split(sep=sep) for value in values]  # a list of lists
    value_set = set(chain.from_iterable(value_list))  # flatten and dedup

    result = list(v for v in value_set if v not in na_values)
    return _check_length(result)


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
    Column("aapos", dest="aa.pos", transform=split_int),
    Column("genename", transform=split_str),
    Column("Ensembl_geneid", transform=split_str),
    Column("Ensembl_transcriptid", transform=split_str),
    Column("Ensembl_proteinid", transform=split_str),
    Column("Uniprot_acc", tag=COLUMN_TAG.UNIPROT_ACC),  # special column, see prune_uniprot()
    Column("Uniprot_entry", tag=COLUMN_TAG.UNIPROT_ENTRY),  # special column, see prune_uniprot()
    Column("HGVSc_ANNOVAR", tag=COLUMN_TAG.HGVS_CODING),  # special column, see prune_hgvsc_hgvsp()
    Column("HGVSp_ANNOVAR", tag=COLUMN_TAG.HGVS_PROTEIN),  # ditto
    Column("HGVSc_snpEff", tag=COLUMN_TAG.HGVS_CODING),  # ditto
    Column("HGVSp_snpEff", tag=COLUMN_TAG.HGVS_PROTEIN),  # ditto
    Column("HGVSc_VEP", tag=COLUMN_TAG.HGVS_CODING),  # ditto
    Column("HGVSp_VEP", tag=COLUMN_TAG.HGVS_PROTEIN),  # ditto
    Column("APPRIS", transform=split_str),
    Column("GENCODE_basic", dest="gencode_basic", transform=split_str),
    Column("TSL", transform=split_int),
    Column("VEP_canonical", dest="vep_canonical", transform=split_str),
    Column("cds_strand", dest="cds_strand", transform=split_str),
    Column("refcodon", dest="aa.refcodon", transform=split_str),
    Column("codonpos", dest="aa.codonpos", transform=split_int),
    Column("codon_degeneracy", dest="aa.codon_degeneracy", transform=split_int),
    Column("Ancestral_allele", dest="ancestral_allele", transform=split_str),
    Column("AltaiNeandertal", dest="altai_neandertal", transform=split_genotype),
    Column("Denisova", transform=split_genotype),
    Column("VindijiaNeandertal", dest="vindijia_neandertal", transform=split_genotype),
    Column("ChagyrskayaNeandertal", dest="chagyrskaya_neandertal", transform=split_genotype),
    Column("SIFT_score", transform=split_float),
    Column("SIFT_converted_rankscore", dest="sift.converted_rankscore", transform=split_float),
    Column("SIFT_pred", transform=split_str),
    Column("SIFT4G_score", transform=split_float),
    Column("SIFT4G_converted_rankscore", dest="sift4g.converted_rankscore", transform=split_float),
    Column("SIFT4G_pred", transform=split_str),
    Column("Polyphen2_HDIV_score", transform=split_float),
    Column("Polyphen2_HDIV_rankscore", transform=split_float),
    Column("Polyphen2_HDIV_pred", transform=split_str),
    Column("Polyphen2_HVAR_score", transform=split_float),
    Column("Polyphen2_HVAR_rankscore", transform=split_float),
    Column("Polyphen2_HVAR_pred", transform=split_str),
    Column("LRT_score", transform=split_float),
    Column("LRT_converted_rankscore", dest="lrt.converted_rankscore", transform=split_float),
    Column("LRT_pred", transform=split_str),
    Column("LRT_Omega", transform=split_float),
    Column("MutationTaster_score", transform=split_float),
    Column("MutationTaster_converted_rankscore", dest="mutationtaster.converted_rankscore", transform=split_float),
    Column("MutationTaster_pred", transform=split_str),
    Column("MutationTaster_model", transform=split_str),
    Column("MutationTaster_AAE", transform=split_str),
    Column("MutationAssessor_score", transform=split_float),
    Column("MutationAssessor_rankscore", transform=split_float),
    Column("MutationAssessor_pred", transform=split_str),
    Column("FATHMM_score", transform=split_float),
    Column("FATHMM_converted_rankscore", dest="fathmm.converted_rankscore", transform=split_float),
    Column("FATHMM_pred", transform=split_str),
    Column("PROVEAN_score", transform=split_float),
    Column("PROVEAN_converted_rankscore", dest="provean.converted_rankscore", transform=split_float),
    Column("PROVEAN_pred", transform=split_str),
    Column("VEST4_score", transform=split_float),
    Column("VEST4_rankscore", transform=split_float),
    Column("MetaSVM_score", transform=split_float),
    Column("MetaSVM_rankscore", transform=split_float),
    Column("MetaSVM_pred", transform=split_str),
    Column("MetaLR_score", transform=split_float),
    Column("MetaLR_rankscore", transform=split_float),
    Column("MetaLR_pred", transform=split_str),
    Column("Reliability_index", dest="reliability_index", transform=int),
    Column("MetaRNN_score", transform=split_float),
    Column("MetaRNN_rankscore", transform=split_float),
    Column("MetaRNN_pred", transform=split_str),
    Column("M-CAP_score", transform=split_float),
    Column("M-CAP_rankscore", transform=split_float),
    Column("M-CAP_pred", transform=split_str),
    Column("REVEL_score", transform=split_float),
    Column("REVEL_rankscore", transform=split_float),
    Column("MutPred_score", transform=split_float),
    Column("MutPred_rankscore", transform=split_float),
    Column("MutPred_protID", dest="mutpred.accession", transform=split_str),
    Column("MutPred_AAchange", dest="mutpred.aa_change", transform=split_str),
    Column("MutPred_Top5features", dest="mutpred.pred", transform=parse_mutpred_top5features),
    Column("MVP_score", transform=split_float),
    Column("MVP_rankscore", transform=split_float),
    Column("gMVP_score", transform=split_float),  # new in 4.4.a
    Column("gMVP_rankscore", transform=split_float),  # new in 4.4.a
    Column("MPC_score", transform=split_float),
    Column("MPC_rankscore", transform=split_float),
    Column("PrimateAI_score", transform=split_float),
    Column("PrimateAI_rankscore", transform=split_float),
    Column("PrimateAI_pred", transform=split_str),
    Column("DEOGEN2_score", transform=split_float),
    Column("DEOGEN2_rankscore", transform=split_float),
    Column("DEOGEN2_pred", transform=split_str),
    Column("BayesDel_addAF_score", dest="bayesdel.add_af.score", transform=split_float),
    Column("BayesDel_addAF_rankscore", dest="bayesdel.add_af.rankscore", transform=split_float),
    Column("BayesDel_addAF_pred", dest="bayesdel.add_af.pred", transform=split_str),
    Column("BayesDel_noAF_score", dest="bayesdel.no_af.score", transform=split_float),
    Column("BayesDel_noAF_rankscore", dest="bayesdel.no_af.rankscore", transform=split_float),
    Column("BayesDel_noAF_pred", dest="bayesdel.no_af.pred", transform=split_str),
    Column("ClinPred_score", transform=split_float),
    Column("ClinPred_rankscore", transform=split_float),
    Column("ClinPred_pred", transform=split_str),
    Column("LIST-S2_score", transform=split_float),
    Column("LIST-S2_rankscore", transform=split_float),
    Column("LIST-S2_pred", transform=split_str),
    Column("VARITY_R_score", transform=split_float),  # new in 4.4.a
    Column("VARITY_R_rankscore", transform=split_float),
    Column("VARITY_ER_score", transform=split_float),
    Column("VARITY_ER_rankscore", transform=split_float),
    Column("VARITY_R_LOO_score", dest="varity.r_loo.score", transform=split_float),
    Column("VARITY_R_LOO_rankscore", dest="varity.r_loo.rankscore", transform=split_float),
    Column("VARITY_ER_LOO_score", dest="varity.er_loo.score", transform=split_float),
    Column("VARITY_ER_LOO_rankscore", dest="varity.er_loo.rankscore", transform=split_float),
    Column("ESM1b_score", dest="esm1b.score", transform=split_float),  # new in 4.5.a
    Column("ESM1b_rankscore", dest="esm1b.rankscore", transform=split_float),  # new in 4.5.a
    Column("ESM1b_pred", dest="esm1b.pred", transform=split_str),  # new in 4.5.a
    Column("EVE_score", dest="eve.score", transform=split_float),  # new in 4.5.a
    Column("EVE_rankscore", dest="eve.rankscore", transform=split_float),  # new in 4.5.a
    Column("EVE_Class10_pred", dest="eve.class10_pred", transform=split_str),  # new in 4.5.a
    Column("EVE_Class20_pred", dest="eve.class20_pred", transform=split_str),  # new in 4.5.a
    Column("EVE_Class25_pred", dest="eve.class25_pred", transform=split_str),  # new in 4.5.a
    Column("EVE_Class30_pred", dest="eve.class30_pred", transform=split_str),  # new in 4.5.a
    Column("EVE_Class40_pred", dest="eve.class40_pred", transform=split_str),  # new in 4.5.a
    Column("EVE_Class50_pred", dest="eve.class50_pred", transform=split_str),  # new in 4.5.a
    Column("EVE_Class60_pred", dest="eve.class60_pred", transform=split_str),  # new in 4.5.a
    Column("EVE_Class70_pred", dest="eve.class70_pred", transform=split_str),  # new in 4.5.a
    Column("EVE_Class75_pred", dest="eve.class75_pred", transform=split_str),  # new in 4.5.a
    Column("EVE_Class80_pred", dest="eve.class80_pred", transform=split_str),  # new in 4.5.a
    Column("EVE_Class90_pred", dest="eve.class90_pred", transform=split_str),  # new in 4.5.a
    Column("AlphaMissense_score", dest="alphamissense.score", transform=split_float),  # new in 4.5.a
    Column("AlphaMissense_rankscore", dest="alphamissense.rankscore", transform=split_float),  # new in 4.5.a
    Column("AlphaMissense_pred", dest="alphamissense.pred", transform=split_str),  # new in 4.5.a
    Column("Aloft_Fraction_transcripts_affected", dest="aloft.fraction_transcripts_affected", transform=split_str),
    Column("Aloft_prob_Tolerant", dest="aloft.prob_tolerant", transform=split_str),
    Column("Aloft_prob_Recessive", dest="aloft.prob_recessive", transform=split_str),
    Column("Aloft_prob_Dominant", dest="aloft.prob_dominant", transform=split_str),
    Column("Aloft_pred", transform=split_str),
    Column("Aloft_Confidence", transform=split_str),
    Column("CADD_raw", dest="cadd.raw_score", transform=split_float, assembly="hg38"),  # TODO CADD will have hg38 next update. Deprecate these 3 field then.
    Column("CADD_raw_rankscore", dest="cadd.raw_rankscore", transform=split_float, assembly="hg38"),
    Column("CADD_phred", transform=split_float, assembly="hg38"),  # CADD phred-like scores, not as other predications of string type
    # Column("CADD_raw_hg19", assembly="hg19"),  # discarded because Myvariant.info already has a hg19-only datasource of CADD.
    # Column("CADD_raw_rankscore_hg19", assembly="hg19"),  # ditto
    # Column("CADD_phred_hg19", assembly="hg19"),  # ditto
    Column("DANN_score", transform=split_float),
    Column("DANN_rankscore", transform=split_float),
    Column("fathmm-MKL_coding_score", dest="fathmm-mkl.coding_score", transform=split_float),
    Column("fathmm-MKL_coding_rankscore", dest="fathmm-mkl.coding_rankscore", transform=split_float),
    Column("fathmm-MKL_coding_pred", dest="fathmm-mkl.coding_pred", transform=split_str),
    Column("fathmm-MKL_coding_group", dest="fathmm-mkl.coding_group", transform=split_str),
    Column("fathmm-XF_coding_score", dest="fathmm-xf.coding_score", transform=split_float),
    Column("fathmm-XF_coding_rankscore", dest="fathmm-xf.coding_rankscore", transform=split_float),
    Column("fathmm-XF_coding_pred", dest="fathmm-xf.coding_pred", transform=split_str),
    Column("Eigen-raw_coding", dest="eigen.raw_coding", transform=split_float),
    Column("Eigen-raw_coding_rankscore", dest="eigen.raw_coding_rankscore", transform=split_float),
    Column("Eigen-phred_coding", dest="eigen.phred_coding", transform=split_float),
    Column("Eigen-PC-raw_coding", dest="eigen-pc.raw_coding", transform=split_float),
    Column("Eigen-PC-raw_coding_rankscore", dest="eigen-pc.raw_coding_rankscore", transform=split_float),
    Column("Eigen-PC-phred_coding", dest="eigen-pc.phred_coding", transform=split_float),
    Column("GenoCanyon_score", transform=split_float),
    Column("GenoCanyon_rankscore", transform=split_float),
    Column("integrated_fitCons_score", dest="fitcons.integrated.score", transform=split_float),
    Column("integrated_fitCons_rankscore", dest="fitcons.integrated.rankscore", transform=split_float),
    Column("integrated_confidence_value", dest="fitcons.integrated.confidence_value", transform=split_int),
    Column("GM12878_fitCons_score", dest="fitcons.gm12878.score", transform=split_float),
    Column("GM12878_fitCons_rankscore", dest="fitcons.gm12878.rankscore", transform=split_float),
    Column("GM12878_confidence_value", dest="fitcons.gm12878.confidence_value", transform=split_int),
    Column("H1-hESC_fitCons_score", dest="fitcons.h1-hesc.score", transform=split_float),
    Column("H1-hESC_fitCons_rankscore", dest="fitcons.h1-hesc.rankscore", transform=split_float),
    Column("H1-hESC_confidence_value", dest="fitcons.h1-hesc.confidence_value", transform=split_int),
    Column("HUVEC_fitCons_score", dest="fitcons.huvec.score", transform=split_float),
    Column("HUVEC_fitCons_rankscore", dest="fitcons.huvec.rankscore", transform=split_float),
    Column("HUVEC_confidence_value", dest="fitcons.huvec.confidence_value", transform=split_int),
    Column("LINSIGHT", dest="linsight.score", transform=split_float),
    Column("LINSIGHT_rankscore", transform=split_float),
    Column("GERP++_NR", transform=split_float),
    Column("GERP++_RS", transform=split_float),
    Column("GERP++_RS_rankscore", dest="gerp++.rs_rankscore", transform=split_float),
    Column("phyloP100way_vertebrate", dest="phylop.100way_vertebrate.score", transform=split_float),
    Column("phyloP100way_vertebrate_rankscore", dest="phylop.100way_vertebrate.rankscore", transform=split_float),
    Column("phyloP470way_mammalian", dest="phylop.470way_mammalian.score", transform=split_float),  # replaced 30way_mammalian in 4.4.a
    Column("phyloP470way_mammalian_rankscore", dest="phylop.470way_mammalian.rankscore", transform=split_float),  # replaced 30way_mammalian in 4.4.a
    Column("phyloP17way_primate", dest="phylop.17way_primate.score", transform=split_float),
    Column("phyloP17way_primate_rankscore", dest="phylop.17way_primate.rankscore", transform=split_float),
    Column("phastCons100way_vertebrate", dest="phastcons.100way_vertebrate.score", transform=split_float),
    Column("phastCons100way_vertebrate_rankscore", dest="phastcons.100way_vertebrate.rankscore", transform=split_float),
    Column("phastCons470way_mammalian", dest="phastcons.470way_mammalian.score", transform=split_float),  # replaced 30way_mammalian in 4.4.a
    Column("phastCons470way_mammalian_rankscore", dest="phastcons.470way_mammalian.rankscore", transform=split_float),  # replaced 30way_mammalian in 4.4.a
    Column("phastCons17way_primate", dest="phastcons.17way_primate.score", transform=split_float),
    Column("phastCons17way_primate_rankscore", dest="phastcons.17way_primate.rankscore", transform=split_float),
    Column("SiPhy_29way_pi", dest="siphy_29way.pi", transform=parse_siphy_29way_pi),
    Column("SiPhy_29way_logOdds", dest="siphy_29way.logodds_score", transform=split_float),
    Column("SiPhy_29way_logOdds_rankscore", dest="siphy_29way.logodds_rankscore", transform=split_float),
    Column("bStatistic", dest="bstatistic.score", transform=split_float),
    Column("bStatistic_converted_rankscore", dest="bstatistic.converted_rankscore", transform=split_float),
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
    Column("Interpro_domain", transform=split_str),
    Column("GTEx_V8_eQTL_gene", dest="gtex.eqtl.gene", tag=COLUMN_TAG.GTEX_EQTL_GENE),  # special column, see prune_gtex_eqtl()
    Column("GTEx_V8_eQTL_tissue", dest="gtex.eqtl.tissue", tag=COLUMN_TAG.GTEX_EQTL_TISSUE),  # special column, see prune_gtex_eqtl()
    Column("GTEx_V8_sQTL_gene", dest="gtex.sqtl.gene", tag=COLUMN_TAG.GTEX_SQTL_GENE),  # special column, see prune_gtex_sqtl()
    Column("GTEx_V8_sQTL_tissue", dest="gtex.sqtl.tissue", tag=COLUMN_TAG.GTEX_SQTL_TISSUE),  # special column, see prune_gtex_sqtl()
    Column("eQTLGen_snp_id", dest="eqtlgen.snp_id", transform=split_str),
    Column("eQTLGen_gene_id", dest="eqtlgen.gene_id", transform=split_str),
    Column("eQTLGen_gene_symbol", dest="eqtlgen.gene_symbol", transform=split_str),
    Column("eQTLGen_cis_or_trans", dest="eqtlgen.cis_or_trans", transform=split_str),
    Column("Geuvadis_eQTL_target_gene", transform=split_str)
]

HG19_COLUMNS = [c for c in COLUMNS if c.is_hg19()]
HG38_COLUMNS = [c for c in COLUMNS if c.is_hg38()]

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


def prune_uniprot(raw_doc: dict, acc_column: Column, entry_column: Column, na_values: set = NA_VALUES):
    """
    Map each UniProt accession number and entry name from the raw document into a dictionary,
    and assign all such dictionaries to the raw document's top "uniprot" field.

    E.g. with the following input value:

        raw_doc["uniprot.acc"] = "P54578-2;P54578-3;A6NJA2;P54578"
        raw_doc["uniprot.entry"] = "UBP14_HUMAN;UBP14_HUMAN;A6NJA2_HUMAN;UBP14_HUMAN"

    raw_doc will be assigned as:

        raw_doc["uniprot"] = [
            {'acc': 'P54578-2', 'entry': 'UBP14_HUMAN'},
            {'acc': 'P54578-3', 'entry': 'UBP14_HUMAN'},
            {'acc': 'A6NJA2', 'entry': 'A6NJA2_HUMAN'},
            {'acc': 'P54578', 'entry': 'UBP14_HUMAN'}
        ]
    """
    # acc_column = TAG_COLUMN_MAP[COLUMN_TAG.UNIPROT_ACC][0]
    # entry_column = TAG_COLUMN_MAP[COLUMN_TAG.UNIPROT_ENTRY][0]

    if (acc_column.dest in raw_doc) and (entry_column.dest in raw_doc):
        acc_value = raw_doc[acc_column.dest]
        entry_value = raw_doc[entry_column.dest]

        uniprot_result = [{"acc": acc, "entry": entry} for (acc, entry) in split_zip(acc_value, entry_value, sep=";", na_values=na_values)]
        uniprot_result = _check_length(uniprot_result)
        if uniprot_result is not None:
            raw_doc["uniprot"] = uniprot_result

        del raw_doc[acc_column.dest]
        del raw_doc[entry_column.dest]

    return raw_doc


def prune_hgvsc_hgvsp(raw_doc: dict, hgvsc_columns: list[Column], hgvsp_columns: list[Column], na_values: set = NA_VALUES):
    """
    Split "HGVSc_ANNOVAR", "HGVSc_snpEff", and "HGVSc_VEP" values into "hgvsc" field;
    split "HGVSp_ANNOVAR", "HGVSp_snpEff", and "HGVSp_VEP" values into "hgvsp" field.
    """
    coding_values = [raw_doc[c.dest] for c in hgvsc_columns if c.dest in raw_doc]
    protein_values = [raw_doc[c.dest] for c in hgvsp_columns if c.dest in raw_doc]

    coding_result = split_dedup(coding_values, sep=";", na_values=na_values)
    protein_result = split_dedup(protein_values, sep=";", na_values=na_values)

    if coding_result is not None:
        raw_doc["hgvsc"] = coding_result
    if protein_result is not None:
        raw_doc["hgvsp"] = protein_result

    for c in hgvsc_columns:
        raw_doc.pop(c.dest, None)  # safely delete the key because it can be absent
    for c in hgvsp_columns:
        raw_doc.pop(c.dest, None)  # safely delete the key because it can be absent

    return raw_doc


def prune_gtex(new_doc_key: str, raw_doc: dict, gene_column: Column, tissue_column: Column, na_values: set = NA_VALUES):
    """
    Map each GTEx gene name and tissue name from the raw document into a dictionary,
    and assign all such dictionaries to the raw document's top "gtex" field.

    E.g. with the following input value for GTEx eQTL:

        row["gtex_gene"] = "ENOSF1|ENOSF1"
        row["gtex_tissue"] = "Adipose_Subcutaneous|Muscle_Skeletal"

    raw_doc will be assigned as:

         row["gtex.eqtl"] = [
            {'gene': 'ENOSF1', 'tissue': 'Adipose_Subcutaneous'},
            {'gene': 'ENOSF1', 'tissue': 'Muscle_Skeletal'}
        ]
    """
    # when these two keys are not present in the doc, it means the responding two values in tsv files are NA values
    if (gene_column.dest in raw_doc) and (tissue_column.dest in raw_doc):
        gene_value = raw_doc[gene_column.dest]
        tissue_value = raw_doc[tissue_column.dest]

        # special separator "|" for GTEx
        gtex_result = [{"gene": acc, "tissue": entry} for (acc, entry) in split_zip(gene_value, tissue_value, sep=r"|", na_values=na_values)]
        gtex_result = _check_length(gtex_result)
        if gtex_result is not None:
            raw_doc[new_doc_key] = gtex_result

        del raw_doc[gene_column.dest]
        del raw_doc[tissue_column.dest]

    return raw_doc


def prune_gtex_sqtl(raw_doc: dict, gene_column: Column, tissue_column: Column, na_values: set = NA_VALUES):
    """
    Map each GTEx gene name and tissue name from the raw document into a dictionary,
    and assign all such dictionaries to the raw document's top "gtex" field.

    E.g. with the following input value:

        row["gtex_gene"] = "ENOSF1|ENOSF1"
        row["gtex_tissue"] = "Adipose_Subcutaneous|Muscle_Skeletal"

    raw_doc will be assigned as:

         row["gtex.sqtl"] = [
            {'gene': 'ENOSF1', 'tissue': 'Adipose_Subcutaneous'},
            {'gene': 'ENOSF1', 'tissue': 'Muscle_Skeletal'}
        ]
    """
    doc = prune_gtex(new_doc_key="gtex.sqtl", raw_doc=raw_doc, gene_column=gene_column, tissue_column=tissue_column, na_values=na_values)
    return doc


def prune_gtex_eqtl(raw_doc: dict, gene_column: Column, tissue_column: Column, na_values: set = NA_VALUES):
    """
    Map each GTEx gene name and tissue name from the raw document into a dictionary,
    and assign all such dictionaries to the raw document's top "gtex" field.

    E.g. with the following input value:

        row["gtex_gene"] = "ENOSF1|ENOSF1"
        row["gtex_tissue"] = "Adipose_Subcutaneous|Muscle_Skeletal"

    raw_doc will be assigned as:

         row["gtex.eqtl"] = [
            {'gene': 'ENOSF1', 'tissue': 'Adipose_Subcutaneous'},
            {'gene': 'ENOSF1', 'tissue': 'Muscle_Skeletal'}
        ]
    """
    doc = prune_gtex(new_doc_key="gtex.eqtl", raw_doc=raw_doc, gene_column=gene_column, tissue_column=tissue_column, na_values=na_values)
    return doc


def prune_hg19_doc(doc: dict, na_values: set = NA_VALUES):
    uniprot_acc_column = TAG_COLUMN_MAP[COLUMN_TAG.UNIPROT_ACC][0]
    uniprot_entry_column = TAG_COLUMN_MAP[COLUMN_TAG.UNIPROT_ENTRY][0]
    doc = prune_uniprot(doc, acc_column=uniprot_acc_column, entry_column=uniprot_entry_column, na_values=na_values)

    hgvs_coding_columns = TAG_COLUMN_MAP[COLUMN_TAG.HGVS_CODING]
    hgvs_protein_columns = TAG_COLUMN_MAP[COLUMN_TAG.HGVS_PROTEIN]
    doc = prune_hgvsc_hgvsp(doc, hgvsc_columns=hgvs_coding_columns, hgvsp_columns=hgvs_protein_columns, na_values=na_values)

    gtex_sqtl_gene_column = TAG_COLUMN_MAP[COLUMN_TAG.GTEX_SQTL_GENE][0]
    gtex_sqtl_tissue_column = TAG_COLUMN_MAP[COLUMN_TAG.GTEX_SQTL_TISSUE][0]
    doc = prune_gtex_sqtl(doc, gene_column=gtex_sqtl_gene_column, tissue_column=gtex_sqtl_tissue_column, na_values=na_values)

    gtex_eqtl_gene_column = TAG_COLUMN_MAP[COLUMN_TAG.GTEX_EQTL_GENE][0]
    gtex_eqtl_tissue_column = TAG_COLUMN_MAP[COLUMN_TAG.GTEX_EQTL_TISSUE][0]
    doc = prune_gtex_eqtl(doc, gene_column=gtex_eqtl_gene_column, tissue_column=gtex_eqtl_tissue_column, na_values=na_values)

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
        current_doc = _construct_doc(row, na_values=NA_VALUES)

        if current_doc is None:
            continue

        if last_doc is not None:
            if current_doc["_id"] == last_doc["_id"]:
                last_aa = last_doc["dbnsfp"]["aa"]
                current_aa = current_doc["dbnsfp"]["aa"]

                if not isinstance(last_aa, list):
                    last_aa = [last_aa]
                last_aa.append(current_aa)

                last_doc["dbnsfp"]["aa"] = last_aa
                continue
            else:
                yield last_doc

        last_doc = current_doc

    # yield the very last doc
    if last_doc:
        yield last_doc

    file.close()
