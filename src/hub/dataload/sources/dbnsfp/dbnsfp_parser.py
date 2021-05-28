import csv
import glob
import itertools
import re

from biothings.utils.dataload import dict_sweep  # list_split, unlist, value_convert_to_number
from biothings.utils.common import anyfile

# VALID_COLUMN_NO = 367  # for 4.1a
VALID_COLUMN_NO = 642  # for 4.2a


"""
this parser is for dbNSFP v4.2a downloaded from
https://sites.google.com/site/jpopgen/dbNSFP
"""


class DbnsfpReader:
    # dbNSFP_variant use "." for missing values;
    # other none values are borrowed from the `biothings.utils.dataload.dict_sweep` function and
    #   from the default `na_values` argument of pandas.read_csv().
    # see https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
    none_values = {r'.', r'', r" ", r"-", r'#N/A', r'#N/A N/A', r'#NA', r'-1.#IND', r'-1.#QNAN', r'-NaN', r'-nan',
                   r'1.#IND', r'1.#QNAN', r'<NA>', r'N/A', r'NA', r'NULL', r'NaN', r'n/a', r'nan', r'null', r'none',
                   r"Not Available", r"unknown"}

    mutpred_top5features_pattern = re.compile(r" \(P = (\d*\.?\d+)\)$")

    # A general rule from observation: for some of the columns, data type can be inferred from the suffix of their
    # column names. E.g. "xxx_score" is usually float.
    # This rule is usually true especially when dealing with grouped columns (like "DANN_score" and "DANN_rankscore").
    # Grouped columns are represented by their common col_prefix (like "DANN").
    # Column names in one group can be restored by concatenating their common col_prefix and individual suffixes.
    col_suffix_to_type = {
        "score": float,
        "rankscore": float,
        "converted_rankscore": float,
        "fitCons_score": float,
        "fitCons_rankscore": float,
        "confidence_value": int,
        "AC": int,
        "AF": float
    }

    @classmethod
    def read_string(cls, row, col, sep=None, transform=None):
        """
        Read `row[col]` as a string. If `sep` is None, return the single string (with transformation).
        If `sep` is not None, separate the string into a list of substrings, transform each substring, and then return
        the list.
        """
        def apply_transformation(_string, _transform):
            """
            If the transformation is to convert the string into an integer or float, wrap it in try-catch;
            otherwise simply apply the transformation as a function to the string.
            """
            if _transform is int or _transform is float:
                try:
                    return _transform(_string)
                except ValueError:
                    raise ValueError("Cannot convert {col} value {string} to {type}".format(col=col, string=_string,
                                                                                            type=_transform))
            return _transform(_string)

        string = row[col]
        if string in cls.none_values:
            return None

        if sep is None:
            if transform is not None:
                string = apply_transformation(string, transform)

            return string
        else:
            string_list = [s for s in string.split(sep=sep) if s not in cls.none_values]
            if not string_list:  # `string_list` is empty after none-values are removed
                return None

            if transform is not None:
                string_list = [apply_transformation(string, transform) for string in string_list]

            return string_list if len(string_list) > 1 else string_list[0]

    @classmethod
    def read_unique_strings(cls, row, cols, sep=None):
        """
        Return the unique strings from the readout union of multiple columns.
        No transformation is applied.
        """
        string_list = [row[key].split(sep=sep) for key in cols]
        string_list = list(set(string for string in itertools.chain.from_iterable(string_list)
                               if string not in cls.none_values))

        if not string_list:  # `string_list` is empty after none-values are removed
            return None

        return string_list if len(string_list) > 1 else string_list[0]

    @classmethod
    def _iter_read_group(cls, row, col_prefix, col_suffixes, sep=";"):
        """
        Some columns other than `*_AC` and `*_AF` are grouped by their prefixes, e.g. "ClinPred_pred",
        "ClinPred_rankscore", and "ClinPred_score". Such groups of columns usually contains scores of some metrics.

        To play safe, I assume each column in such a group is a separable string (although it may not contain any
        separator at all); and I assume all columns in a group should use the same separator, semicolon by default.

        `col_prefix` and `col_suffixes`, when joined with "_", form the column names in the `row` to be read.
        Each column will be read and yielded as in an iterator.

        Args:
            row (dict-like): the data to read in
            col_prefix (string): col_prefix of the keys of interest in `row`, e.g "ClinPred"
            col_suffixes (collection of strings): suffixes of the columns interest in `row`,
                                                  e.g. ("pred", "rankscore", "score")
            sep (string): a single string of the separator
        """
        for col_suffix in col_suffixes:
            # filter(function, iterable):
            #   If function is None, the identity function is assumed, that is,
            #   all elements of iterable that are false are removed.
            col = "_".join(filter(None, (col_prefix, col_suffix)))
            transform = cls.col_suffix_to_type.get(col_suffix)
            yield cls.read_string(row, col, sep=sep, transform=transform)

    @classmethod
    def map_score_rankscore_to_json(cls, row, col_prefix):
        """
        A common case of calling `_iter_read_group`.

        Dozens of columns are grouped into tuple, like "<col_prefix>_score" and "<col_prefix>_rankscore".
        Their data types are usually float.
        """
        col_suffixes = ("score", "rankscore")  # col_suffixes are also the json keys
        return dict(zip(col_suffixes, cls._iter_read_group(row, col_prefix, col_suffixes)))

    @classmethod
    def map_score_rankscore_pred_to_json(cls, row, col_prefix):
        """
        A common case of calling `_iter_read_group`.

        Dozens of columns are grouped into triples, like "<col_prefix>_score", "<col_prefix>_rankscore", and
        "<col_prefix>_pred". Their data types are usually float, float and string.
        """
        col_suffixes = ("score", "rankscore", "pred")  # col_suffixes are also the json keys
        return dict(zip(col_suffixes, cls._iter_read_group(row, col_prefix, col_suffixes)))

    @classmethod
    def map_score_converted_rankscore_pred_to_json(cls, row, col_prefix):
        """
        A common case of calling `_iter_read_group`.

        Dozens of columns are grouped into triples, like "<col_prefix>_score", "<col_prefix>_converted_rankscore", and
        "<col_prefix>_pred". Their data types are usually float, float and string.
        """
        col_suffixes = ("score", "converted_rankscore", "pred")  # col_suffixes are also the json keys
        return dict(zip(col_suffixes, cls._iter_read_group(row, col_prefix, col_suffixes)))

    @classmethod
    def map_fitcons_score_rankscore_confidence_value_to_json(cls, row, col_prefix):
        """
        A common case of calling `_iter_read_group`.

        Dozens of columns are grouped into triples, like "<col_prefix>_fitCons_score", "<col_prefix>_fitCons_rankscore",
        and "<col_prefix>_confidence_value". Their data types are usually float, float and int.
        """
        col_suffixes = ("fitCons_score", "fitCons_rankscore", "confidence_value")
        json_keys = ("fitcons_score", "fitcons_rankscore", "confidence_value")
        return dict(zip(json_keys, cls._iter_read_group(row, col_prefix, col_suffixes)))

    @classmethod
    def map_AC_AF_to_json(cls, row, col_prefix, col_infixes, whole_group=False):
        """
        Read `<col_prefix>_<col_infix>_AC` and `<col_prefix>_<col_infix>_AF` columns for each `col_infix` in
        `col_infixes`.
        When `whole_group` is True, read two extra columns, `<col_prefix>_AC` and `<col_prefix>_AF`.

        AC (allele counts) will be parsed into integers; AF (allele freqs) will be parsed into floats.
        No separator is assumed to exist in such AC/AF columns.

        The readout will be returned as a dict like:

            {
                <col_infix.lower()>_ac : int(<col_prefix>_<col_infix>_AC)
                <col_infix.lower()>_af : float(<col_prefix>_<col_infix>_AF)
            }

        E.g. to read `ESP6500_AA_AC`, `ESP6500_AA_AF`, `ESP6500_EA_AC` and `ESP6500_EA_AF` columns, we can simply call
        map_AC_AF_to_json(col_prefix="ESP6500", col_infixes=["AA", "EA"], whole_group=False)
        """
        if col_infixes is None:
            col_infixes = []

        if whole_group:
            col_infixes = [""] + col_infixes

        col_suffixes = ("AC", "AF")

        def _generate_json_fields():
            for col_infix in col_infixes:
                for col_suffix in col_suffixes:
                    # filter(function, iterable):
                    #   If function is None, the identity function is assumed, that is,
                    #   all elements of iterable that are false are removed.
                    col = "_".join(filter(None, (col_prefix, col_infix, col_suffix)))
                    transform = cls.col_suffix_to_type.get(col_suffix)

                    json_key = "_".join(filter(None, (col_infix, col_suffix))).lower()
                    yield json_key, cls.read_string(row, col, sep=None, transform=transform)

        return dict(_generate_json_fields())

    @classmethod
    def parse_mutpred_top5features(cls, row, col):
        """
        `mutpred_mechanisms` is a string combined from 5 clauses, separated by semicolons (with whitespaces).
        Each clause has the same pattern of "<mechanism> (P = <p_val>)".

        E.g. "Loss of helix (P = 0.0444); Gain of loop (P = 0.0502); Gain of catalytic residue at A444 (P = 0.1876); \
        Gain of solvent accessibility (P = 0.2291); Loss of disorder (P = 0.9475)"

        Here we apply regex to parse this string

            regex = re.compile(r" \(P = (\d*\.?\d+)\)$")
            [(e for e in regex.split(s) if e.strip()) for s in string.split("; ")]

        and get a list of 5 tuples like

            [('Loss of helix', '0.0444'), ('Gain of loop', '0.0502'), ('Gain of catalytic residue at A444', '0.1876'),
            ('Gain of solvent accessibility', '0.2291'), ('Loss of disorder', '0.9475')]

        Then construct a list of 5 dictionaries of <"mechanism": xxx, "p_val": xxx> and return
        """
        string = cls.read_string(row, col)
        if string is None:
            return None

        mp_list = [(e for e in cls.mutpred_top5features_pattern.split(s) if e.strip()) for s in string.split("; ")]
        return [{"mechanism": mp[0], "p_val": float(mp[1])} for mp in mp_list]

    @classmethod
    def parse_uniprot(cls, row, acc_col, entry_col):
        """
        Read uniprot accession numbers and entry names as two strings from `row`. Map each accession number and entry
        name into a dictionary, and return a list of such dictionaries.

        E.g. suppose we have the following readouts

            row[acc_col] = "P54578-2;P54578-3;A6NJA2;P54578"
            row[entry_col] = UBP14_HUMAN;UBP14_HUMAN;A6NJA2_HUMAN;UBP14_HUMAN

        Then we will return a list of dictionaries like:

            [{'acc': 'P54578-2', 'entry': 'UBP14_HUMAN'},
             {'acc': 'P54578-3', 'entry': 'UBP14_HUMAN'},
             {'acc': 'A6NJA2', 'entry': 'A6NJA2_HUMAN'},
             {'acc': 'P54578', 'entry': 'UBP14_HUMAN'}]
        """
        # cls.read_string() is not used here because it will remove the NA substrings from the split string
        acc_list = [s if s not in cls.none_values else None for s in row[acc_col].split(";")]
        entry_list = [s if s not in cls.none_values else None for s in row[entry_col].split(";")]

        return [{"acc": acc, "entry": entry} for (acc, entry) in zip(acc_list, entry_list)
                if (acc, entry) != (None, None)]

    @classmethod
    def parse_gtex(cls, row, gene_col, tissue_col):
        """
        Read GTEx genes and tissues as two strings from `row`. Map each gene and tissue into a dictionary, and return
        a list of such dictionaries.

        E.g. suppose we have the following readouts

            row[gene_col] = "ENOSF1|ENOSF1"
            row[tissue_col] = Adipose_Subcutaneous|Muscle_Skeletal

        Then we will return a list of dictionaries like:

            [{'gene': 'ENOSF1', 'tissue': 'Adipose_Subcutaneous'},
             {'gene': 'ENOSF1', 'tissue': 'Muscle_Skeletal'}]
        """
        # cls.read_string() is not used here because it will remove the NA substrings from the split string
        gene_list = [s if s not in cls.none_values else None for s in row[gene_col].split(r"|")]
        tissue_list = [s if s not in cls.none_values else None for s in row[tissue_col].split(r"|")]

        return [{"gene": gene, "tissue": tissue} for (gene, tissue) in zip(gene_list, tissue_list)
                if (gene, tissue) != (None, None)]

    @classmethod
    def parse_siphy_29way_pi(cls, row, col):
        """
        A "SiPhy_29way_pi" value, if not None, is a string separated by ":", representing an estimated stationary
        distribution of A, C, G and T at a variant site. E.g. "0.0:0.5259:0.0:0.4741".

        Here we split the string and convert it to a dict of {<nt>: <freq>}.
        """
        string = cls.read_string(row, col)
        if string is None:
            return None

        freq = [float(s) for s in string.split(":")]
        pi_dict = {'a': freq[0], 'c': freq[1], 'g': freq[2], 't': freq[3]}
        return pi_dict

    @classmethod
    def map_CADD_to_json(cls, row, version):
        """
        Myvariant.info already has a datasource of CADD, but it's hg19 only.
        When version == "hg19", we will discard all CADD fields in dbNSFP.
        When version == "hg38", we will only include the hg38 CADD fields in dbNSFP.
        """
        if version == "hg38":
            cadd_dict = {
                "raw_score": cls.read_string(row, "CADD_raw", sep=";", tranform=float),
                "raw_rankscore": cls.read_string(row, "CADD_raw_rankscore", sep=";", tranform=float),
                "phred": cls.read_string(row, "CADD_phred", sep=";", tranform=float),
                # "raw_score_hg19": cls.read_string(row, "CADD_raw_hg19", sep=";", tranform=float),
                # "raw_rankscore_hg19": cls.read_string(row, "CADD_raw_rankscore_hg19", sep=";", tranform=float),
                # "phred_hg19": cls.read_string(row, "CADD_phred_hg19", sep=";", tranform=float)
            }
            return cadd_dict
        elif version == "hg19":
            return None
        else:
            raise ValueError("Cannot recognize version. Should be either hg19 or hg38. Got version={}".format(version))

    @classmethod
    def map_row_to_json(cls, row, version):
        """
        Parse each row into a json object
        """

        """
        Step 1: Read basic variant information
        """
        # in case of no hg19 position provided, remove the item
        pos_hg19 = cls.read_string(row, "hg19_pos(1-based)", transform=int)  # Column 9
        if pos_hg19 is None:
            return None

        pos_hg18 = cls.read_string(row, "hg18_pos(1-based)", transform=int)  # Column 11
        pos_hg38 = cls.read_string(row, "pos(1-based)", transform=int)  # Column 2

        # ref and alt cannot be None else hgvs_id is invalid
        ref = cls.read_string(row, "ref", transform=lambda s: s.upper())  # Column 3
        alt = cls.read_string(row, "alt", transform=lambda s: s.upper())  # Column 4

        if version == 'hg19':
            chrom = cls.read_string(row, "hg19_chr", ransform=lambda s: "MT" if s == "M" else s)  # Column 1
            hgvs_id = "chr%s:g.%d%s>%s" % (chrom, pos_hg19, ref, alt)
        elif version == 'hg38':
            chrom = cls.read_string(row, "#chr", ransform=lambda s: "MT" if s == "M" else s)  # Column 8
            hgvs_id = "chr%s:g.%d%s>%s" % (chrom, pos_hg38, ref, alt)
        else:
            raise ValueError("Cannot recognize version. Should be either hg19 or hg38. Got version={}".format(version))

        rsid = cls.read_string(row, "rs_dbSNP")  # Column 7

        # Column 10 "hg18_chr" is skipped

        """
        Step 2: Construct the JSON object
        """
        one_snp_json = {
            "_id": hgvs_id,
            "dbnsfp": {
                "rsid": rsid,  # Column 7
                "chrom": chrom,  # Column 1 or 8
                "hg19": {  # Column 9
                    "start": pos_hg19,
                    "end": pos_hg19
                },
                "hg18": {  # Column 11
                    "start": pos_hg18,
                    "end": pos_hg18
                },
                "hg38": {  # Column 2
                    "start": pos_hg38,
                    "end": pos_hg38
                },
                "ref": ref,  # Column 3
                "alt": alt,  # Column 4
                "aa": {  # Column 5-6, 12, 30-32
                    "ref": cls.read_string(row, "aaref"),
                    "alt": cls.read_string(row, "aaalt"),
                    "pos": cls.read_string(row, "aapos", sep=";", transform=int),
                    "refcodon": cls.read_string(row, "refcodon", sep=";"),
                    "codonpos": cls.read_string(row, "codonpos", sep=";", transform=int),
                    "codon_degeneracy": cls.read_string(row, "codon_degeneracy", sep=";", transform=int),
                },
                # Column 13
                "genename": cls.read_string(row, "genename", sep=";"),
                # Column 14-16
                "ensembl": {
                    "geneid": cls.read_string(row, "Ensembl_geneid", sep=";"),
                    "transcriptid": cls.read_string(row, "Ensembl_transcriptid", sep=";"),
                    "proteinid": cls.read_string(row, "Ensembl_proteinid", sep=";")
                },
                # Column 17-18
                "uniprot": cls.parse_uniprot(row, "Uniprot_acc", "Uniprot_entry"),
                # Column 19-24
                "hgvsc": cls.read_unique_strings(row, cols=["HGVSc_ANNOVAR", "HGVSc_snpEff", "HGVSc_VEP"], sep=";"),
                "hgvsp": cls.read_unique_strings(row, cols=["HGVSp_ANNOVAR", "HGVSp_snpEff", "HGVSp_VEP"], sep=";"),
                # Column 25-29
                "appris": cls.read_string(row, "APPRIS", sep=";"),
                "genecode_basic": cls.read_string(row, "GENCODE_basic", sep=";"),
                "tsl": cls.read_string(row, "TSL", sep=";", transform=int),
                "vep_canonical": cls.read_string(row, "VEP_canonical", sep=";"),
                "cds_strand": cls.read_string(row, "cds_strand", sep=";"),
                # Column 33-36
                "ancestral_allele": cls.read_string(row, "Ancestral_allele", sep=";"),
                "altai_neandertal": cls.read_string(row, "AltaiNeandertal", sep=r"/"),
                "denisova": cls.read_string(row, "Denisova", sep=r"/"),
                "vindijia_neandertal": cls.read_string(row, "VindijiaNeandertal", sep=r"/"),
                # Column 37-42
                "sift": cls.map_score_converted_rankscore_pred_to_json(row, col_prefix="SIFT"),
                "sift4g": cls.map_score_converted_rankscore_pred_to_json(row, col_prefix="SIFT4G"),
                # Column 43-48
                "polyphen2": {
                    "hdiv": cls.map_score_rankscore_pred_to_json(row, col_prefix="Polyphen2_HDIV"),
                    "hvar": cls.map_score_rankscore_pred_to_json(row, col_prefix="Polyphen2_HVAR"),
                },
                # Column 49-52
                "lrt": {
                    "score": cls.read_string(row, "LRT_score", sep=";", transform=float),
                    "converted_rankscore": cls.read_string(row, "LRT_converted_rankscore", sep=";", transform=float),
                    "pred": cls.read_string(row, "LRT_pred", sep=";"),
                    "omega": cls.read_string(row, "LRT_Omega", sep=";", transform=float)
                },
                # Column 53-60
                "mutationtaster": {
                    "score": cls.read_string(row, "MutationTaster_score", sep=";", transform=float),
                    "converted_rankscore": cls.read_string(row, "MutationTaster_converted_rankscore", sep=";", transform=float),
                    "pred": cls.read_string(row, "MutationTaster_pred", sep=";"),
                    "model": cls.read_string(row, "MutationTaster_model", sep=";"),
                    "AAE": cls.read_string(row, "MutationTaster_AAE", sep=";")
                },
                "mutationassessor": cls.map_score_rankscore_pred_to_json(row, col_prefix="MutationAssessor"),
                # Column 61-63
                "fathmm": cls.map_score_converted_rankscore_pred_to_json(row, col_prefix="FATHMM"),
                # Column 64-66
                "provean": cls.map_score_converted_rankscore_pred_to_json(row, col_prefix="PROVEAN"),
                # Column 67-68
                "vest4": cls.map_score_rankscore_to_json(row, col_prefix="VEST4"),
                # Column 69-78
                "metasvm": cls.map_score_rankscore_pred_to_json(row, col_prefix="MetaSVM"),
                "metalr": cls.map_score_rankscore_pred_to_json(row, col_prefix="MetaLR"),
                "reliability_index": cls.read_string(row, "Reliability_index", transform=int),
                "metarnn": cls.map_score_rankscore_pred_to_json(row, col_prefix="MetaRNN"),
                # Column 79-81
                "m-cap": cls.map_score_rankscore_pred_to_json(row, col_prefix="M-CAP"),
                # Column 82-83
                "revel": cls.map_score_rankscore_to_json(row, col_prefix="REVEL"),
                # Column 84-88
                "mutpred": {
                    "score": cls.read_string(row, "MutPred_score", sep=";", transform=float),
                    "rankscore": cls.read_string(row, "MutPred_rankscore", sep=";", transform=float),
                    "accession": cls.read_string(row, "MutPred_protID", sep=";"),
                    "aa_change": cls.read_string(row, "MutPred_AAchange", sep=";"),
                    "pred": cls.parse_mutpred_top5features(row, "MutPred_Top5features"),
                },
                # Column 89-92
                "mvp": cls.map_score_rankscore_to_json(row, col_prefix="MVP"),
                "mpc": cls.map_score_rankscore_to_json(row, col_prefix="MPC"),
                # Column 93-95
                "primateai": cls.map_score_rankscore_pred_to_json(row, col_prefix="PrimateAI"),
                # Column 96-98
                "deogen2": cls.map_score_rankscore_pred_to_json(row, col_prefix="DEOGEN2"),
                # Column 99-104
                "bayesdel": {
                    "add_af": cls.map_score_rankscore_pred_to_json(row, col_prefix="BayesDel_addAF"),
                    "no_af": cls.map_score_rankscore_pred_to_json(row, col_prefix="BayesDel_noAF")
                },
                # Column 105-107
                "clinpred": cls.map_score_rankscore_pred_to_json(row, col_prefix="ClinPred"),
                # Column 108-110
                "list-s2": cls.map_score_rankscore_pred_to_json(row, col_prefix="LIST-S2"),
                # Column 111-116
                "aloft": {
                    "fraction_transcripts_affected": cls.read_string(row, "Aloft_Fraction_transcripts_affected", sep=";"),
                    "prob_tolerant": cls.read_string(row, "Aloft_prob_Tolerant", sep=";"),
                    "prob_recessive": cls.read_string(row, "Aloft_prob_Recessive", sep=";"),
                    "prob_dominant": cls.read_string(row, "Aloft_prob_Dominant", sep=";"),
                    "pred": cls.read_string(row, "Aloft_pred", sep=";"),
                    "confidence": cls.read_string(row, "Aloft_Confidence", sep=";")
                },
                # Column 117-122
                #   Column 117-119 are hg38
                #   Column 120-122 are hg19
                # Only column 117-119 will be included in the document when verison == "hg38"
                # No CADD fields will be included verison == "hg19"
                "cadd": cls.map_CADD_to_json(row, version),
                # Column 123-124
                "dann": cls.map_score_rankscore_to_json(row, col_prefix="DANN"),
                # Column 125-131
                "fathmm-mkl": {
                    "coding_score": cls.read_string(row, "fathmm-MKL_coding_score", sep=";", tranform=float),
                    "coding_rankscore": cls.read_string(row, "fathmm-MKL_coding_rankscore", sep=";", tranform=float),
                    "coding_pred": cls.read_string(row, "fathmm-MKL_coding_pred", sep=";"),
                    "coding_group": cls.read_string(row, "fathmm-MKL_coding_group", sep=";")
                },
                "fathmm-xf": {
                    "coding_score": cls.read_string(row, "fathmm-XF_coding_score", sep=";", tranform=float),
                    "coding_rankscore": cls.read_string(row, "fathmm-XF_coding_rankscore", sep=";", tranform=float),
                    "coding_pred": cls.read_string(row, "fathmm-XF_coding_pred", sep=";")
                },
                # Column 132-137
                # Please note that Eigen uses "-", NOT "_", to connect column name prefix and suffixes
                # Cannot use cls._iter_read_group here
                "eigen":  {
                    "raw_coding": cls.read_string(row, "Eigen-raw_coding", sep=";", transform=float),
                    "raw_coding_rankscore": cls.read_string(row, "Eigen-raw_coding_rankscore", sep=";", transform=float),
                    "phred_coding": cls.read_string(row, "Eigen-phred_coding", sep=";", transform=float)
                },
                "eigen-pc": {
                    "raw_coding": cls.read_string(row, "Eigen-PC-raw_coding", sep=";", transform=float),
                    "raw_coding_rankscore": cls.read_string(row, "Eigen-PC-raw_coding_rankscore", sep=";", transform=float),
                    "phred_coding": cls.read_string(row, "Eigen-PC-phred_coding", sep=";", transform=float),
                },
                # Column 138-139
                # Please note that column 139 in dbNSFP4.2a.readme.txt is "GenoCanyon_score_rankscore" and it's a typo
                "genocanyon": cls.map_score_rankscore_to_json(row, col_prefix="GenoCanyon"),
                # Column 140-142
                "integrated": cls.map_fitcons_score_rankscore_confidence_value_to_json(row, col_prefix="integrated"),
                # Column 143-145
                "gm12878": cls.map_fitcons_score_rankscore_confidence_value_to_json(row, col_prefix="GM12878"),
                # Column 146-148
                "h1-hesc": cls.map_fitcons_score_rankscore_confidence_value_to_json(row, col_prefix="H1-hESC"),
                # Column 149-151
                "huvec": cls.map_fitcons_score_rankscore_confidence_value_to_json(row, col_prefix="HUVEC"),
                # Column 152-153
                # Note that column 152 is "LINSIGHT", not "LINSIGHT_score" (possibly a typo in the source data file)
                "linsight": {
                    "score": cls.read_string(row, 'LINSIGHT', sep=";", transform=float),
                    "rankscore": cls.read_string(row, "LINSIGHT_rankscore", sep=";", transform=float)
                },
                # Column 154-156
                "gerp++": {
                    "nr": cls.read_string(row, "GERP++_NR", sep=";", transform=float),
                    "rs": cls.read_string(row, "GERP++_RS", sep=";", transform=float),
                    "rs_rankscore": cls.read_string(row, "GERP++_RS_rankscore", sep=";", transform=float)
                },
                # Column 157-162
                "phylop": {
                    "vertebrate": {
                        "track": "100way",
                        "score": cls.read_string(row, "phyloP100way_vertebrate", sep=";", transform=float),
                        "rankscore": cls.read_string(row, "phyloP100way_vertebrate_rankscore", sep=";", transform=float)
                    },
                    "mammal": {
                        "track": "30way",
                        "score": cls.read_string(row, "phyloP30way_mammalian", sep=";", transform=float),
                        "rankscore": cls.read_string(row, "phyloP30way_mammalian_rankscore", sep=";", transform=float)
                    },
                    "primate": {
                        "track": "17way",
                        "score": cls.read_string(row, "phyloP17way_primate", sep=";", transform=float),
                        "rankscore": cls.read_string(row, "phyloP17way_primate_rankscore", sep=";", transform=float)
                    }
                },
                # Column 163-168
                "phastcons": {
                    "vertebrate": {
                        "track": "100way",
                        "score": cls.read_string(row, "phastCons100way_vertebrate", sep=";", transform=float),
                        "rankscore": cls.read_string(row, "phastCons100way_vertebrate_rankscore", sep=";", transform=float)
                    },
                    "mammal": {
                        "track": "30way",
                        "score": cls.read_string(row, "phastCons30way_mammalian", sep=";", transform=float),
                        "rankscore": cls.read_string(row, "phastCons30way_mammalian_rankscore", sep=";", transform=float)
                    },
                    "primate": {
                        "track": "17way",
                        "score": cls.read_string(row, "phastCons17way_primate", sep=";", transform=float),
                        "rankscore": cls.read_string(row, "phastCons17way_primate_rankscore", sep=";", transform=float)
                    }
                },
                # Column 169-171
                "siphy": {
                    "mammal": {
                        "track": "29way",
                        "pi": cls.parse_siphy_29way_pi(row, "SiPhy_29way_pi"),
                        # Note that the column name is "SiPhy_29way_logOdds", not "SiPhy_29way_logOdds_score"
                        "logodds_score": cls.read_string(row, "SiPhy_29way_logOdds", sep=";", transform=float),
                        "logodds_rankscore": cls.read_string(row, "SiPhy_29way_logOdds_rankscore", sep=";", transform=float)
                    }
                },
                # Column 172-173
                "bstatistic": {
                    # Note that the column name is "bStatistic", not "bStatistic_score"
                    "score": cls.read_string(row, 'bStatistic', sep=";", transform=float),
                    "converted_rankscore": cls.read_string(row, "bStatistic_converted_rankscore", sep=";", transform=float)
                },
                # map_AC_AF_to_json(cls, row, col_prefix, col_infixes)
                # Column 174-185
                "1000gp3": cls.map_AC_AF_to_json(row, col_prefix="1000Gp3", col_infixes=["AFR", "EUR", "AMR", "EAS", "SAS"], whole_group=True),
                # Column 186-187
                "twinsuk": cls.map_AC_AF_to_json(row, col_prefix="TWINSUK", col_infixes=None, whole_group=True),
                # Column 188-189
                "alspac": cls.map_AC_AF_to_json(row, col_prefix="ALSPAC", col_infixes=None, whole_group=True),
                # Column 190-191
                "uk10k": cls.map_AC_AF_to_json(row, col_prefix="UK10K", col_infixes=None, whole_group=True),
                # Column 192-195
                "esp6500": cls.map_AC_AF_to_json(row, col_prefix="ESP6500", col_infixes=["AA", "EA"], whole_group=False),
                # Column 196-211
                "exac": cls.map_AC_AF_to_json(row, col_prefix="ExAC", col_infixes=["Adj", "AFR", "AMR", "EAS", "FIN", "NFE", "SAS"], whole_group=True),
                # Column 212-227
                "exac_nontcga": cls.map_AC_AF_to_json(row, col_prefix="ExAC_nonTCGA", col_infixes=["Adj", "AFR", "AMR", "EAS", "FIN", "NFE", "SAS"], whole_group=True),
                # Column 228-243
                "exac_nonpsych": cls.map_AC_AF_to_json(row, col_prefix="ExAC_nonpsych", col_infixes=["Adj", "AFR", "AMR", "EAS", "FIN", "NFE", "SAS"], whole_group=True),

                # Column 245-629 are gnomAD_* columns. Skipped.

                # Column 630-638
                "clinvar": {
                    "clinvar_id": cls.read_string(row, "clinvar_id"),
                    "clinsig": cls.read_string(row, "clinvar_clnsig", sep=r"|"),
                    "trait": cls.read_string(row, "clinvar_trait", sep=r"|"),
                    "review": cls.read_string(row, "clinvar_review", sep=r"|"),
                    "hgvs": cls.read_string(row, "clinvar_hgvs", sep=r"|"),
                    "omim": cls.read_string(row, "clinvar_OMIM_id", sep=r"|"),
                    "medgen": cls.read_string(row, "clinvar_MedGen_id", sep=r"|"),
                    "orphanet": cls.read_string(row, "clinvar_Orphanet_id", sep=r"|"),
                    "var_source": cls.read_string(row, "clinvar_var_source", sep=r"|")
                },
                # Column 639-642
                "interpro_domain": cls.read_string(row, "Interpro_domain", sep=";"),
                # "gtex": list(gtex),
                "gtex": cls.parse_gtex(row, "GTEx_V8_gene", "GTEx_V8_tissue"),
                "geuvadis_eqtl_target_gene": cls.read_string(row, "Geuvadis_eQTL_target_gene", sep=";")

                # End of row
            }
        }

        """
        Step 3: Prune the JSON object and return
        """
        # `value_convert_to_number` converts strings to numeric values inside the dictionary
        # `unlist` regresses lists of length 1 to single values inside the dictionary
        # `dict_sweep` remove NA values indicated by `vals` inside the dictionary
        # `list_split` separate fields by `sep` into lists
        one_snp_json = dict_sweep(one_snp_json, vals=[None], remove_invalid_list=True)
        return one_snp_json


# open file, parse, pass to json mapper
def data_generator(input_file, version):
    with anyfile(input_file) as file:
        file_reader = csv.reader(file, delimiter="\t")

        header = next(file_reader)
        assert len(header) == VALID_COLUMN_NO, "Expecting %s columns, but got %s" % (VALID_COLUMN_NO, len(header))

        previous_row = None
        for row in file_reader:
            row = dict(zip(header, row))

            # use transposed matrix to have 1 line with N 187 columns
            current_row = DbnsfpReader.map_row_to_json(row, version=version)
            if previous_row and current_row:
                if current_row["_id"] == previous_row["_id"]:
                    aa = previous_row["dbnsfp"]["aa"]
                    if not isinstance(aa, list):
                        aa = [aa]
                    aa.append(current_row["dbnsfp"]["aa"])
                    previous_row["dbnsfp"]["aa"] = aa
                    if len(previous_row["dbnsfp"]["aa"]) > 1:
                        continue
                else:
                    yield previous_row

            previous_row = current_row

        if previous_row:
            yield previous_row


def load_data_file(input_file, version):
    data = data_generator(input_file, version=version)
    for one_snp_json in data:
        yield one_snp_json


# load path and find files, pass to data_generator
def load_data(path_glob, version='hg19'):
    for input_file in sorted(glob.glob(path_glob)):
        for d in load_data_file(input_file, version):
            yield d
