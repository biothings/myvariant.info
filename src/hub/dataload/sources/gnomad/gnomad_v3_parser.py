import vcf
import math
from itertools import chain
from .gnomad_common_parser import PopulationFrequencyParser, ProfileParser, AbstractSiteQualityMetricsParser, GnomadVcfRecordParser


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

    """
    Exclude the following prefixes when parsing population frequencies:
    
        excluded_prefixes = ["AC_controls_and_biobanks", "AC_non_cancer", "AC_non_neuro", "AC_non_topmed", "AC_non_v2",
                             "AF_controls_and_biobanks", "AF_non_cancer", "AF_non_neuro", "AF_non_topmed", "AF_non_v2",
                             "nhomalt_controls_and_biobanks", "nhomalt_non_cancer", "nhomalt_non_neuro", 
                             "nhomalt_non_topmed", "nhomalt_non_v2",
                             "AN_controls_and_biobanks", "AN_non_cancer", "AN_non_neuro", "AN_non_topmed", "AN_non_v2"]
    """
    pop_freq_prefixes = ["AC", "AF", "nhomalt", "AN"]
    excluded_infixes = ["controls_and_biobanks", "non_cancer", "non_neuro", "non_topmed", "non_v2"]
    excluded_prefixes = list(chain.from_iterable((prefix + "_" + infix for infix in excluded_infixes)
                                                 for prefix in pop_freq_prefixes))

    pop_freq_parser = PopulationFrequencyParser(vcf_reader.infos.keys(), excluded_prefixes=excluded_prefixes)

    record_parser = GnomadVcfRecordParser(ProfileParser, SiteQualityMetricsParser, pop_freq_parser)
    for record in vcf_reader:
        for doc in record_parser.parse(record, doc_key="gnomad_genome"):
            yield doc

