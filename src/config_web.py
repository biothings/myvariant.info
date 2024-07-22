import copy
import re

from biothings.web.settings.default import ANNOTATION_KWARGS, APP_LIST, QUERY_KWARGS

# *****************************************************************************
# Elasticsearch variables
# *****************************************************************************
ES_HOST = "http://es8.biothings.io:9200"
ES_ARGS = {
    "request_timeout": 210,
}
ES_INDICES = {
    None: "myvariant_current_hg19",
    "variant": "myvariant_current_hg19",
    "hg19": "myvariant_current_hg19",
    "hg38": "myvariant_current_hg38",
}

# *****************************************************************************
# App URL Patterns
# *****************************************************************************
API_VERSION = "v1"
APP_LIST = [
    (
        r"/v1/variant/(chr.{1,2}):(?!g\.)[g\.]{0,2}(\d+.*)",
        "tornado.web.RedirectHandler",
        {"url": "/v1/variant/{0}:g.{1}"},
    ),
    *APP_LIST,  # default handlers
    (r"/{pre}/metadata/fields/?", "web.handlers.MVMetadataFieldHandler"),
    (r"/{pre}/metadata/?", "web.handlers.MVMetadataSourceHandler"),
    (r"/{pre}/{ver}/metadata/fields/?", "web.handlers.MVMetadataFieldHandler"),
    (r"/{pre}/{ver}/metadata/?", "web.handlers.MVMetadataSourceHandler"),
    (r"/beacon/query?", "web.beacon.handlers.BeaconHandler"),
    (r"/beacon/info", "web.beacon.handlers.BeaconInfoHandler"),
]
# *****************************************************************************
# ES Query Pipeline
# *****************************************************************************
ES_QUERY_BUILDER = "web.pipeline.MVQueryBuilder"
ES_QUERY_BACKEND = "web.pipeline.MVQueryBackend"

# *****************************************************************************
# Analytics & Tracking
# *****************************************************************************

URL_BASE = "http://myvariant.info"

# for logo on format=html
HTML_OUT_HEADER_IMG = "/static/favicon.ico"

# for title line on format=html
HTML_OUT_TITLE = """
<p style="font-family:'Open Sans',sans-serif;font-weight:bold; font-size:16px;">
    <a href="http://myvariant.info" target="_blank" style="text-decoration: none; color: black">
        MyVariant.info - Variant Annotation as a Service
    </a>
</p>"""

METADATA_DOCS_URL = "http://docs.myvariant.info/en/latest/doc/data.html"
QUERY_DOCS_URL = "http://docs.myvariant.info/en/latest/doc/variant_query_service.html"
ANNOTATION_DOCS_URL = (
    "http://docs.myvariant.info/en/latest/doc/variant_annotation_service.html"
)

# kwargs for status check get
STATUS_CHECK = {"id": "chr1:g.218631822G>A", "index": "myvariant_current_hg19"}

# *****************************************************************************
# User Input Control
# *****************************************************************************
BIOLINK_MODEL_PREFIX_BIOTHINGS_VARIANT_MAPPING = {
    "DBSNP": {
        "type": "variant",
        "field": "dbsnp.rsid",
        "regex_term_pattern": "(?P<term>(DBSNP:rs[0-9]+|rs[0-9]+))",
    },
    "CLINVAR": {
        "type": "variant",
        "field": "clinvar.variant_id",
        "regex_term_pattern": "(?P<term>(CLINVAR:[0-9]+|[0-9]+))",
    },
    "CAID": {
        "type": "variant",
        "field": "clingen.caid",
        "regex_term_pattern": "(?P<term>(CAID:CA[0-9]+|CA[0-9]+))",
    },
}

# CURIE ID support based on BioLink Model
biolink_curie_regex_list = []
for (
    biolink_prefix,
    mapping,
) in BIOLINK_MODEL_PREFIX_BIOTHINGS_VARIANT_MAPPING.items():
    field_match = mapping.get("field", [])
    term_pattern = mapping.get("regex_term_pattern", None)
    if term_pattern is None:
        term_pattern = "(?P<term>[^:]+)"

    raw_expression = rf"({biolink_prefix}):{term_pattern}"
    compiled_expression = re.compile(raw_expression, re.I)

    pattern = (compiled_expression, field_match)
    biolink_curie_regex_list.append(pattern)


# Custom prefix handling for variant specific identifiers
variant_prefix_handling = [
    (re.compile(r"chr(.?)+", re.I), "_id"),
    (re.compile(r"rs[0-9]+", re.I), "dbsnp.rsid"),
    (re.compile(r"rcv[0-9\.]+", re.I), "clinvar.rcv.accession"),
    (re.compile(r"var_[0-9]+", re.I), "uniprot.humsavar.ftid"),
]


ANNOTATION_ID_REGEX_LIST = [
    *biolink_curie_regex_list,
    *variant_prefix_handling,
]


ANNOTATION_DEFAULT_SCOPES = ["_id", "clingen.caid"]

# typedef for assembly parameter
ASSEMBLY_TYPEDEF = {
    "assembly": {"type": str, "default": "hg19", "enum": ("hg19", "hg38")}
}

ANNOTATION_KWARGS = copy.deepcopy(ANNOTATION_KWARGS)
ANNOTATION_KWARGS["*"].update(ASSEMBLY_TYPEDEF)

QUERY_KWARGS = copy.deepcopy(QUERY_KWARGS)
QUERY_KWARGS["*"].update(ASSEMBLY_TYPEDEF)

METADATA_KWARGS = {"*": ASSEMBLY_TYPEDEF}
FIELDS_KWARGS = {"*": ASSEMBLY_TYPEDEF}

LICENSE_TRANSFORM = {
    "exac_nontcga": "exac",
    "gnomad_exome": "gnomad",
    "gnomad_genome": "gnomad",
}
