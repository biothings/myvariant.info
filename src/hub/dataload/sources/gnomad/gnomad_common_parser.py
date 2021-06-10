import vcf
from abc import ABC, abstractmethod

from biothings.utils.dataload import dict_sweep, unlist, value_convert_to_number
from utils.hgvs import get_hgvs_from_vcf

CHROM_VALID_VALUES = {str(_chr) for _chr in list(range(1, 23)) + ['X', 'Y', 'MT']}


class PopulationName:
    """
    Helps to generate population names to access `_RECORD.INFO`.

    According to https://gnomad.broadinstitute.org/help/how-are-population-names-abbreviated, population names in gnomAD
    VCF and Hail Table are abbreviated to 3 letter IDs:

    - afr: African/African-American
    - ami: Amish
    - amr: Latino/Admixed American
    - asj: Ashkenazi Jewish
    - eas: East Asian
        - jpn: Japanese
        - kor: Korean
        - oea: Other East Asian
    - fin: European (Finnish)
    - mid: Middle Eastern
    - nfe: European (non-Finnish)
        - bgr: Bulgarian
        - est: Estonian
        - nwe: North-western European
        - onf: Other non-Finnish European
        - seu: Southern European
        - swe: Swedish
    - oth: Other
    - sas: South Asian

    Take "East Asian" as an example. It actually spawns 6 populations in gnomAD, i.e. `eas`, `eas_jpn`, `eas_kor`,
    `eas_oea`, `eas_XX` (or `eas_female` in v2), and `eas_XY` (or `eas_male` in v2). We can use the following code to
    generate the 6 population names at once:

        eas = PopulationName("eas", ["jpn", "kor", "oea", "XX", "XY"], separator="_")
        eas.to_list()  # returns [`eas`, `eas_jpn`, `eas_kor`, `eas_oea`, `eas_XX`, `eas_XY`]
    """
    def __init__(self, primary_name, secondary_names, separator="_"):
        self.primary_name = primary_name
        self.secondary_names = secondary_names
        self.separator = separator

        self.name_list = None

    def to_list(self):
        if self.name_list is None:
            self.name_list = [self.primary_name] + [self.separator.join((self.primary_name, secondary_name)) for
                                                    secondary_name in self.secondary_names]

        return self.name_list


class PopulationFrequencyParser:
    def __init__(self, ac_keys: list, an_keys: list, nhomalt_keys: list, af_keys: list):
        """
        Save the keys to allele count (AC), allele number (AN), allele frequency (AF), and number of homozygotes
        (nhomalt) data in a gnomAD VCF `_RECORD.INFO` object.

        In theory, these four lists represent the whole set of keys of interest to parse population frequency data, but
        they are NOT guaranteed to appear in every `record.INFO` object.

        Args:
            ac_keys (list): a list of "AC*" keys, e.g. ["AC", "AC_XX", "AC_XY", "AC_afr", "AC_afr_XX", "AC_afr_XY"]
            an_keys (list): a list of "AN*" keys, e.g. ["AN", "AN_XX", "AN_XY", "AN_ami", "AN_ami_XX", "AN_ami_XY"]
            af_keys (list): a list of "AF*" keys, e.g. ["AN", "AF_XX", "AF_XY", "AF_asj", "AF_asj_XX", "AF_asj_XY"]
            nhomalt_keys (list): a list of "nhomalt*" keys, e.g. ["nhomalt_fin", "nhomalt_fin_XX", "nhomalt_fin_XY"]
        """
        self.ac_keys = ac_keys
        self.an_keys = an_keys
        self.nhomalt_keys = nhomalt_keys
        self.af_keys = af_keys

        self.keys = {
            "AC": self.ac_keys,
            "AN": self.an_keys,
            "nhomalt": self.nhomalt_keys,
            "AF": self.af_keys
        }

        # "AC_*", "nhomalt_*", and "AF_*" (and "Hemi_*" in legacy code) values are alt-specific, i.e. they are lists
        #   with each element mapped to a alternative nucleotide in _RECORD.ALT.
        # "AN_*" (and "GC_*" in legacy code) values are scalars.
        self._alt_specific = {
            "AC": True,
            "AN": False,
            "nhomalt": True,
            "AF": True
        }

        # Lazy initialization in self.get_field_name()
        self._key_to_field_name = dict()

    @classmethod
    def from_suffixes(cls, suffixes, separator="_"):
        parser = PopulationFrequencyParser(None, None, None, None)

        for prefix in parser.keys:
            parser.keys[prefix] = cls._create_keys(prefix, suffixes, separator)

        return parser

    @classmethod
    def _create_keys(cls, prefix, suffixes, separator="_"):
        """
        Generates the keys to access a gnomAD VCF `_RECORD.INFO` object for population frequency data.

        E.g. generate_population_frequency_keys("AC", ["afr", "ami", "XX", "XY"], "_") will return a list of keys
        `["AC", "AC_afr", "AC_ami", "AC_XX", "AC_XY"]`
        """
        pop_freq_keys = [prefix]
        if suffixes:
            pop_freq_keys.extend(separator.join((prefix, suffix)) for suffix in suffixes)
        return pop_freq_keys

    @classmethod
    def rename_nhomalt(cls, nhomalt_str: str) -> str:
        """
        Change a "nhomalt*" string to "hom*". E.g. "nhomalt_fin_female" will be changed to "hom_fin_female".
        This is the naming convention used in myvariant.info and has nothing to do with gnomAD.
        """
        return "hom" + nhomalt_str[7:]

    def get_field_name(self, key):
        """
        Return the corresponding field name (that would appear in our JSON document), given a key in the INFO object.

        General rules:

        - Keys like "AC_*", "AN_*", or "AF_*" will be converted to lowercase as field names
        - Keys like "nhomalt_*" will be converted to "hom_*" and then lowercase as field names
        """
        field_name = self._key_to_field_name.get(key)
        if field_name is None:
            if key.startswith("AC") or key.startswith("AN") or key.startswith("AF"):
                field_name = key.lower()
            elif key.startswith("nhomalt"):
                field_name = self.rename_nhomalt(key).lower()
            else:
                raise ValueError("Cannot recognize key %s." % key)

            self._key_to_field_name[key] = field_name
        return field_name

    def parse(self, info: dict, index: int) -> dict:
        """
        For each `key` in `self.ac_keys`, `self.an_keys`, `self.nhomalt_keys`, and `self.af_keys`, read the value of
        `info[key]`. If `info[key]` should be treated as a list, read the value of `info[key][index]`.
        The readout values are packed into a nested dict of the following structure, with the prefixes being
        allele count (ac), allele number (an), allele frequency (af), or number of homozygotes (hom):

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

        # A particular `_RECORD.INFO` object is not guaranteed to contain all keys saved in `self.ac_keys`,
        #   `self.an_keys`, `self.nhomalt_keys`, and `self.af_keys`, so here we need to check the key existence by
        #   using `if key in info`
        #
        # The dict construction below is a little hard to read. Take prefix "AC" as an example. It's equivalent to:
        #
        #   is_alt_specific = True
        #
        #   primary_field_name = "ac"
        #   pf_dict["ac"] = dict()
        #
        #   for key in self.keys["AC"]:
        #       if key in info:
        #           pf_dict["ac"][self._key_to_field_name[key]] = info[key][index]
        for prefix in self.keys:
            is_alt_specific = self._alt_specific[prefix]

            # `prefix` is also an INFO key. we have its corresponding field name saved in `self._key_to_field_name`
            primary_field_name = self.get_field_name(prefix)
            pf_dict[primary_field_name] = dict()

            for key in self.keys[prefix]:
                if key in info:
                    # alt-specific values are lists; use `index` to fetch individual values
                    # non-alt-specific values are scalars; `index` ignored
                    value = info[key][index] if is_alt_specific else info[key]

                    secondary_field_name = self.get_field_name(key)
                    pf_dict[primary_field_name][secondary_field_name] = value

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
    def __init__(self, profile_parser, site_quality_metrics_parser, population_frequency_parser):
        self.profile_parser = profile_parser
        self.site_quality_metrics_parser = site_quality_metrics_parser
        self.population_frequency_parser = population_frequency_parser

    def parse(self, record: vcf.model._Record, doc_key: str):
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
        site_quality_metrics_dict = self.site_quality_metrics_parser.parse(info)

        for i in range(len(record.ALT)):
            hgvs_id, profile_dict = profile_list[i]
            if hgvs_id is None:
                continue

            population_frequency_dict = self.population_frequency_parser.parse(info, i)

            one_snp_json = {
                "_id": hgvs_id,
                doc_key: {
                    **profile_dict,
                    **site_quality_metrics_dict,
                    **population_frequency_dict
                }
            }

            obj = (dict_sweep(unlist(value_convert_to_number(one_snp_json, skipped_keys=['chrom'])), [None]))
            yield obj
