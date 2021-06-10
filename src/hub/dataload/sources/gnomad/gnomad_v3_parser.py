import vcf
import math
from itertools import chain
from .gnomad_common_parser import PopulationName, PopulationFrequencyParser, ProfileParser, \
    AbstractSiteQualityMetricsParser, GnomadVcfRecordParser

# Globals of population names
_FEMALE, _MALE = "XX", "XY"
_POPULATION_NAME_OBJ_LIST = [
    PopulationName("afr", [_FEMALE, _MALE]),
    PopulationName("ami", [_FEMALE, _MALE]),
    PopulationName("amr", [_FEMALE, _MALE]),
    PopulationName("asj", [_FEMALE, _MALE]),
    PopulationName("eas", [_FEMALE, _MALE, "jpn", "kor", "oea"]),
    PopulationName("fin", [_FEMALE, _MALE]),
    PopulationName("mid", [_FEMALE, _MALE]),
    PopulationName("nfe", [_FEMALE, _MALE, "bgr", "est", "nwe", "onf", "seu", "swe"]),
    PopulationName("oth", [_FEMALE, _MALE]),
    PopulationName("sas", [_FEMALE, _MALE])
]
_POPULATION_NAME_STR_LIST = list(chain.from_iterable(pop_name.to_list() for pop_name in _POPULATION_NAME_OBJ_LIST))

"""
Global PopulationFrequencyParser object.

Keys starts with the following prefixes are not parsed as population frequencies:

    ["AC_controls_and_biobanks", "AC_non_cancer", "AC_non_neuro", "AC_non_topmed", "AC_non_v2",
     "AF_controls_and_biobanks", "AF_non_cancer", "AF_non_neuro", "AF_non_topmed", "AF_non_v2",
     "nhomalt_controls_and_biobanks", "nhomalt_non_cancer", "nhomalt_non_neuro", "nhomalt_non_topmed", "nhomalt_non_v2",
     "AN_controls_and_biobanks", "AN_non_cancer", "AN_non_neuro", "AN_non_topmed", "AN_non_v2"]
"""
population_frequency_parser = PopulationFrequencyParser.from_suffixes(suffixes=[_FEMALE, _MALE] + _POPULATION_NAME_STR_LIST)


class SiteQualityMetricsParser(AbstractSiteQualityMetricsParser):
    @classmethod
    def parse(cls, info: dict) -> dict:
        """
        Read site quality metrics (as shown in the gnomAD browser) from the "INFO" field (which is a dict essentially)
        of a gnomAD VCF record.

        N.B. there is a "SiteQuality" metric shown in the gnomAD browser; however it's not included in the "INFO" field.
        Probably it's calculated from other metrics.

        N.B. there is a "AS_QUALapprox" metric shown in the gnomAD browser; however there is no such field in "INFO".
        (somehow there exists a "QUALapprox" field in "INFO" but I assume they are different)

        N.B. there is a "AS_VarDP" metric shown in the gnomAD browser; however there is no such field in "INFO".
        (somehow there exists a "VarDP" field in "INFO" but I assume they are different)
        """
        # the keys of site quality metrics could be missing in the `info` dict
        # so use dict.get() method for default None values

        # "AS_VQSLOD" is a little special. Legacy code will check if it's equal to INF
        as_vqslod = info.get("AS_VQSLOD")
        if as_vqslod == math.inf:
            as_vqslod = None

        sqm_dict = {
            "inbreedingcoeff": info.get("InbreedingCoeff"),
            "as_fs": info.get("AS_FS"),
            "as_mq": {
                "as_mq": info.get("AS_MQ"),
                "as_mqranksum": info.get("AS_MQRankSum"),
            },
            "as_pab_max": info.get("AS_pab_max"),
            "as_qd": info.get("AS_QD"),
            "as_readposranksum": info.get('AS_ReadPosRankSum'),
            "as_sor": info.get("AS_SOR"),
            "as_vqslod": as_vqslod,
        }

        return sqm_dict


def load_genome_data(input_file):
    vcf_reader = vcf.Reader(filename=input_file, compressed=True)

    record_parser = GnomadVcfRecordParser(ProfileParser, SiteQualityMetricsParser, population_frequency_parser)

    for record in vcf_reader:
        for doc in record_parser.parse(record, doc_key="gnomad_genome"):
            yield doc

