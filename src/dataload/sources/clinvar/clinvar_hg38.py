
__metadata__ = {
    "name" : "clinvar_hg38",
    "main_source" : "clinvar"
}

from .clinvar_xml_parser import load_data as load_common
from . import get_mapping

def load_data(self):
    return load_common(self,hg19=False)

