import vcf
import math
from itertools import chain
from .gnomad_common_parser import PopulationName, PopulationFrequencyParser, generate_population_frequency_keys, \
    ProfileParser, AbstractSiteQualityMetricsParser, GnomadVcfRecordParser

# Globals of population names
_FEMALE, _MALE = "female", "male"
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

# Global PopulationFrequencyParser object
population_frequency_parser = PopulationFrequencyParser.from_suffixes(population_suffixes=_POPULATION_NAME_STR_LIST,
                                                                      extra_suffixes=[_FEMALE, _MALE])


class SiteQualityMetricsParser(AbstractSiteQualityMetricsParser):
    @classmethod
    def parse(cls, info: dict) -> dict:
        """
        Read site quality metrics (as shown in the gnomAD browser) from the "INFO" field (which is a dict essentially)
        of a gnomAD VCF record.

        N.B. there is a "SiteQuality" metric shown in the gnomAD browser; however it's not included in the "INFO" field.
        Probably it's calculated from other metrics.

        N.B. "VQSR_culprit" is not a metric but is related to "VQSLOD". Legacy code has it, so I keep it here.
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


def load_genome_data(input_file):
    vcf_reader = vcf.Reader(filename=input_file, compressed=True)

    record_parser = GnomadVcfRecordParser(ProfileParser, SiteQualityMetricsParser, population_frequency_parser)

    for record in vcf_reader:
        for doc in record_parser.parse(record, doc_key="gnomad_genome"):
            yield doc


def load_exome_data(input_file):
    vcf_reader = vcf.Reader(filename=input_file, compressed=True)

    record_parser = GnomadVcfRecordParser(ProfileParser, SiteQualityMetricsParser, population_frequency_parser)

    for record in vcf_reader:
        for doc in record_parser.parse(record, doc_key="gnomad_exome"):
            yield doc
