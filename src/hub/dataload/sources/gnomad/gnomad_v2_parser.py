import vcf
import math

from biothings.utils.dataload import dict_sweep, unlist, value_convert_to_number
from utils.hgvs import get_hgvs_from_vcf

CHROM_VALID_VALUES = {str(_chr) for _chr in list(range(1, 23)) + ['X', 'Y', 'MT']}


class PopulationFrequencyParser:
    def __init__(self, info_keys):
        """
        Iterate all keys in the "INFO" field (which is a dict essentially) of a gnomAD VCF record, and pick the keys to
        population frequency data (as shown in the gnomAD browser).

        The keys of interest will be packed into a dict of the following structure:

            prefix_to_keys = {
                "AC": [<Allele_Count> keys],
                "AN": [<Allele_Number> keys],
                "nhomalt": [<Number_of_Homozygotes> keys],
                "AF": [<Allele_Frequency> keys]
            }

        N.B. Previous prefixes of interest include "GC" and "Hemi", however they are not present in v2.1.1 or v3.1.1
        """
        self.prefix_to_info_keys = {
            "ac": [key for key in info_keys if key.startswith("AC")],
            "an": [key for key in info_keys if key.startswith("AN")],
            "nhomalt": [key for key in info_keys if key.startswith("nhomalt")],
            "af": [key for key in info_keys if key.startswith("AF")],
        }

    @classmethod
    def rename_nhomalt(cls, nhomalt_key):
        """
        Replace the prefix of a "nhomalt_*" key to "hom". E.g. "nhomalt_fin_female" will changed to "hom_fin_female".
        """
        return "hom" + nhomalt_key[7:]

    def parse(self, info, index):
        """
        For each `key` in the values of `prefix_to_keys`, read the value of `info[key]`. If `info[key]` should be treated
        as a list, read the value of `info[key][index]`. The readout values are packed into a nested dict of the following
        structure, with the prefixes being the top level keys:

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


def parse_site_quality_metrics(info):
    """
    Read site quality metrics (as shown in the gnomAD browser) from the "INFO" field (which is a dict essentially) of a
    gnomAD VCF record.

    N.B. there is a "SiteQuality" metric shown in the gnomAD browser; however it's not included in the "INFO" field.
    Probably it's calculated from other metrics.

    N.B. "VQSR_culprit" is not a metric but is related to "VQSLOD". Legacy code included it, so I keep it here.
    """
    # the keys of site quality metrics could be missing in the `info` dict
    # so use dict.get() method for default None values

    # "VQSLOD" is a little special. Legacy code will check if it's equal to INF
    vqslod = info.get("VQSLOD")
    if vqslod == math.inf:
        vqslod = None

    sqm_dict = {
        "baseqranksum": info.get("BaseQRankSum"),
        "clippingranksum": info.get("ClippingRankSum"),
        "dp": info.get("DP"),
        "fs": info.get("FS"),
        "inbreedingcoeff": info.get("InbreedingCoeff"),
        "mq": {
            "mq": info.get("MQ"),
            "mqranksum": info.get("MQRankSum"),
        },
        "pab_max": info.get("pab_max"),
        "qd": info.get("QD"),
        "readposranksum": info.get('ReadPosRankSum'),
        "rf": info.get("rf_tp_probability"),
        "sor": info.get("SOR"),
        "vqslod": vqslod,
        "vqsr_culprit": info.get("VQSR_culprit")
    }

    return sqm_dict


def _map_record_to_json(record, population_freq_parser, doc_key):
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
    chrom = str(record.CHROM)
    if chrom.startswith('chr'):
        chrom = chrom[3:]
    if chrom not in CHROM_VALID_VALUES:
        return

    info = record.INFO

    assert len(record.ALT) == len(info['AC']), \
        "Expecting length of record.ALT= length of info.AC, but not for %s" % record.ID
    assert len(record.ALT) == len(info['AF']), \
        "Expecting length of record.ALT= length of info.AF, but not for %s" % record.ID

    # although each ALT looks exactly like a string, it is a special type
    record.ALT = [str(alt) for alt in record.ALT]
    # map each ALT to its (hgvs_id, var_type) tuple
    alt_to_hgvs = {alt: get_hgvs_from_vcf(chrom, record.POS, record.REF, alt, mutant_type=True) for alt in record.ALT}
    # if multi-allelic, put all variants as a list in multi-allelic field
    hgvs_list = [t[0] for t in alt_to_hgvs.values()] if len(record.ALT) > 1 else None

    sqm_dict = parse_site_quality_metrics(info)

    for i, alt in enumerate(record.ALT):
        hgvs_id, var_type = alt_to_hgvs[alt]
        if hgvs_id is None:
            return  # TODO use `continue` instead?

        pf_dict = population_freq_parser.parse(info, i)

        one_snp_json = {
            "_id": hgvs_id,
            doc_key: {
                "chrom": chrom,
                "pos": record.POS,
                "filter": record.FILTER,
                "multi-allelic": hgvs_list,
                "ref": record.REF,
                "alt": alt,
                "alleles": record.ALT,
                "type": var_type,
                "rsid": record.ID,
                **sqm_dict,
                **pf_dict
            }
        }

        obj = (dict_sweep(unlist(value_convert_to_number(one_snp_json, skipped_keys=['chrom'])), [None]))
        yield obj


def load_genome_data(input_file):
    vcf_reader = vcf.Reader(filename=input_file, compressed=True)
    pf_parser = PopulationFrequencyParser(vcf_reader.infos.keys())
    for record in vcf_reader:
        for doc in _map_record_to_json(record, pf_parser, doc_key="gnomad_genome"):
            yield doc


def load_exome_data(input_file):
    vcf_reader = vcf.Reader(filename=input_file, compressed=True)
    pf_parser = PopulationFrequencyParser(vcf_reader.infos.keys())
    for record in vcf_reader:
        for doc in _map_record_to_json(record, pf_parser, doc_key="gnomad_exome"):
            yield doc
