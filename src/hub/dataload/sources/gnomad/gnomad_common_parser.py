import vcf
from abc import ABC, abstractmethod

from biothings.utils.dataload import dict_sweep, unlist, value_convert_to_number
from utils.hgvs import get_hgvs_from_vcf

CHROM_VALID_VALUES = {str(_chr) for _chr in list(range(1, 23)) + ['X', 'Y', 'MT']}


class PopulationFrequencyParser:
    def __init__(self, info_keys: list, excluded_prefixes: list):
        """
        Iterate all keys in the "INFO" field (which is a dict essentially) of a gnomAD VCF record, and pick the keys to
        population frequency data (as shown in the gnomAD browser).

        The keys of interest will be packed into a dict of the following structure:

            prefix_to_keys = {
                "ac": [<Allele_Count> keys],
                "an": [<Allele_Number> keys],
                "nhomalt": [<Number_of_Homozygotes> keys],
                "af": [<Allele_Frequency> keys]
            }

        N.B. Previous prefixes of interest include "GC" and "Hemi", however they are not present in v2.1.1 or v3.1.1

        Some keys starting with "AC", "AN", "nhomalt" or "AF" are not needed. They are excluded by checking against the
        `excluded_prefixes`. E.g. if the following argument is used,

            excluded_prefixes = ["AC_controls_and_biobanks", "AC_non_cancer", "AC_non_neuro",
                                 "AC_non_topmed", "AC_non_v2"]

        Then all keys starts with these prefixes are excluded (and thus are not categorized into key "ac" in
        `self.prefix_to_info_keys`)
        """
        if excluded_prefixes:
            info_keys = [key for key in info_keys if not any(key.startswith(prefix) for prefix in excluded_prefixes)]

        self.prefix_to_info_keys = {
            "ac": [key for key in info_keys if key.startswith("AC")],
            "an": [key for key in info_keys if key.startswith("AN")],
            "nhomalt": [key for key in info_keys if key.startswith("nhomalt")],
            "af": [key for key in info_keys if key.startswith("AF")]
        }

    @classmethod
    def rename_nhomalt(cls, nhomalt_str: str) -> str:
        """
        Replace the prefix of a "nhomalt_*" string to "hom". E.g. "nhomalt_fin_female" will changed to "hom_fin_female".
        """
        return "hom" + nhomalt_str[7:]

    def parse(self, info: dict, index: int) -> dict:
        """
        For each `key` in the values of `prefix_to_keys`, read the value of `info[key]`. If `info[key]` should be
        treated as a list, read the value of `info[key][index]`. The readout values are packed into a nested dict of
        the following structure, with the prefixes being the top level keys:

            pf_dict = {
                "ac": {
                    "AC_key_1": info["AC_key_1"][index],
                    "AC_key_2": info["AC_key_2"][index],
                    ...
                },
                "an": {
                    "AN_key_1": info["AN_key_1"],
                    "AN_key_2": info["AN_key_2"],
                    ...
                },
                "hom": {
                    "hom_key_1": info["nhomalt_key_1"][index],
                    "hom_key_2": info["nhomalt_key_2"][index],
                    ...
                },
                "af": {
                    "AF_key_1": info["AF_key_1"][index],
                    "AF_key_2": info["AF_key_2"][index],
                    ...
                }
            }

        N.B. "hom_*" keys are renamed from "nhomalt_*" keys in the original info dict
        N.B. "AC_*", "nhomalt_*", and "AF_*" (and "Hemi_*" in legacy code) values are lists;
             "AN_*" (and "GC_*" in legacy code) values are scalars.
        """
        pf_dict = dict()
        for (prefix, info_keys) in self.prefix_to_info_keys.items():
            # This is a little bit tricky.
            # Note that `self.prefix_to_info_keys` can be initialized using the global `vcf_reader.infos.keys()`
            # However part of the `vcf_reader.infos.keys()` may not reside in a specific `info` dict
            keys = [key for key in info_keys if key in info]

            if prefix == "nhomalt":
                pf_dict[self.rename_nhomalt(prefix)] = {self.rename_nhomalt(key): info[key][index] for key in keys}
            elif prefix == "ac" or prefix == "af":
                pf_dict[prefix] = {key: info[key][index] for key in keys}
            else:
                pf_dict[prefix] = {key: info[key] for key in keys}
        return pf_dict


class ProfileParser:
    @classmethod
    def parse(cls, record: vcf.model._Record) -> list:
        """
        Read the profile data from a VCF record. Note that there is no such "profile" section shown in the gnomAD
        browser. These fields, i.e. "chrom", "pos", "filter", "multi-allelic", "ref", "alt", "alleles", "type", and
        "rsid", are named as profile fields simply for the convenience of implementation.

        Each ALT has its own profile (which will be wrapped into a dict) and this function will return a list of tuples
        (<hgvs_id>, <profile_dict>).

        It's feasible to return a dict of {<hgvs_id>: <profile_dict>} instead of a list of tuples, but the order of
        <hgvs_id> should be preserved (to the order of ALTs). It's easier to just use an index to iterate over the list
        of tuples, considering the implementation of `PopulationFrequencyParser.parse()` method.
        """
        # although each ALT looks exactly like a string, it is a special type
        alt_list = [str(alt) for alt in record.ALT]
        # for each ALT, get its (hgvs_id, var_type) tuple
        # Here I assume that the "chr" prefix of `record.CHROM`, if any, has already been removed
        hgvs_list = [get_hgvs_from_vcf(record.CHROM, record.POS, record.REF, alt, mutant_type=True) for alt in alt_list]

        # if multi-allelic, put all variants' HGVS ids as a list in multi-allelic field
        multi_allelic = [t[0] for t in hgvs_list] if len(hgvs_list) > 1 else None

        def generate_profiles():
            for alt, (hgvs_id, var_type) in zip(alt_list, hgvs_list):
                profile_dict = {
                    "chrom": record.CHROM,
                    "pos": record.POS,
                    "filter": record.FILTER,
                    "multi-allelic": multi_allelic,
                    "ref": record.REF,
                    "alt": alt,
                    "alleles": alt_list,
                    "type": var_type,
                    "rsid": record.ID
                }
                yield hgvs_id, profile_dict

        return list(generate_profiles())


class AbstractSiteQualityMetricsParser(ABC):
    @classmethod
    @abstractmethod
    def parse(cls, info: dict) -> dict:
        pass


class GnomadVcfRecordParser:
    def __init__(self, profile_parser, site_quality_metrics_parser, population_freq_parser):
        self.profile_parser = profile_parser
        self.site_quality_metrics_parser = site_quality_metrics_parser
        self.population_freq_parser = population_freq_parser

    def parse(self, record: vcf.model._Record, doc_key):
        """
            When parsing gnomad.genomes.*.vcf.bgz files, `doc_key` should be "gnomad_genome";
            when parsing gnomad.exomes.*.vcf.bgz files, `doc_key` should be "gnomad_exome".

            The returned document has the following structure:

                one_snp_json = {
                    "_id": hgvs_id,
                    doc_key: {
                        "chrom": chrom,
                        ...
                    }
                }
            """
        # the value of CHROM in hg38 GNOMAD source file startswith 'chr'; need to remove it first
        if record.CHROM.startswith('chr'):
            record.CHROM = record.CHROM[3:]  # This step is necessary to `profile_parser.parse()` method
        if record.CHROM not in CHROM_VALID_VALUES:
            return

        info = record.INFO

        assert len(record.ALT) == len(info['AC']), \
            "length of record.ALT != length of info.AC, at CHROM=%s, POS=%s" % (record.CHROM, record.POS)
        assert len(record.ALT) == len(info['AF']), \
            "length of record.ALT != length of info.AF, at CHROM=%s, POS=%s" % (record.CHROM, record.POS)
        assert len(record.ALT) == len(info['nhomalt']), \
            "length of record.ALT != length of info.nhomalt, at CHROM=%s, POS=%s" % (record.CHROM, record.POS)

        profile_list = self.profile_parser.parse(record)
        sqm_dict = self.site_quality_metrics_parser.parse(info)

        for i in range(len(record.ALT)):
            hgvs_id, profile_dict = profile_list[i]
            if hgvs_id is None:
                continue

            pf_dict = self.population_freq_parser.parse(info, i)

            one_snp_json = {
                "_id": hgvs_id,
                doc_key: {
                    **profile_dict,
                    **sqm_dict,
                    **pf_dict
                }
            }

            obj = (dict_sweep(unlist(value_convert_to_number(one_snp_json, skipped_keys=['chrom'])), [None]))
            yield obj
