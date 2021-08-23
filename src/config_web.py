import copy
import re

from biothings.web.settings.default import (
    ANNOTATION_KWARGS, APP_LIST, QUERY_KWARGS)

# *****************************************************************************
# Elasticsearch variables
# *****************************************************************************
ES_HOST = 'es6.biothings.io'
ES_ARGS = {
    'timeout': 120,
}
ES_INDICES = {
    None: 'myvariant_current_hg19',
    'variant': 'myvariant_current_hg19',
    'hg19': 'myvariant_current_hg19',
    'hg38': 'myvariant_current_hg38'
}

# *****************************************************************************
# App URL Patterns
# *****************************************************************************
API_VERSION = 'v1'
APP_LIST = [
    (r'/v1/variant/(chr.{1,2}):(?!g\.)[g\.]{0,2}(\d+.*)',
     'tornado.web.RedirectHandler', {'url': '/v1/variant/{0}:g.{1}'}),
    *APP_LIST,  # default handlers
    (r"/{pre}/metadata/fields/?", 'web.handlers.MVMetadataFieldHandler'),
    (r"/{pre}/metadata/?", 'web.handlers.MVMetadataSourceHandler'),
    (r"/{pre}/{ver}/metadata/fields/?", 'web.handlers.MVMetadataFieldHandler'),
    (r"/{pre}/{ver}/metadata/?", 'web.handlers.MVMetadataSourceHandler'),
]
# *****************************************************************************
# ES Query Pipeline
# *****************************************************************************
ES_QUERY_BUILDER = 'web.pipeline.MVQueryBuilder'
ES_QUERY_BACKEND = 'web.pipeline.MVQueryBackend'

# *****************************************************************************
# Analytics & Tracking
# *****************************************************************************

URL_BASE = 'http://myvariant.info'

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
ANNOTATION_DOCS_URL = "http://docs.myvariant.info/en/latest/doc/variant_annotation_service.html"

# kwargs for status check get
STATUS_CHECK = {
    'id': 'chr1:g.218631822G>A',
    'index': 'myvariant_current_hg19'
}

# *****************************************************************************
# User Input Control
# *****************************************************************************
ANNOTATION_ID_REGEX_LIST = [
    (re.compile(r'rs[0-9]+', re.I), 'dbsnp.rsid'),
    (re.compile(r'rcv[0-9\.]+', re.I), 'clinvar.rcv.accession'),
    (re.compile(r'var_[0-9]+', re.I), 'uniprot.humsavar.ftid')
]
ANNOTATION_DEFAULT_SCOPES = ['_id', 'clingen.caid']

# typedef for assembly parameter
ASSEMBLY_TYPEDEF = {
    'assembly': {
        'type': str,
        'default': 'hg19',
        'enum': ('hg19', 'hg38')
    }
}

ANNOTATION_KWARGS = copy.deepcopy(ANNOTATION_KWARGS)
ANNOTATION_KWARGS['*'].update(ASSEMBLY_TYPEDEF)

QUERY_KWARGS = copy.deepcopy(QUERY_KWARGS)
QUERY_KWARGS['*'].update(ASSEMBLY_TYPEDEF)

METADATA_KWARGS = {'*': ASSEMBLY_TYPEDEF}
FIELDS_KWARGS = {'*': ASSEMBLY_TYPEDEF}

LICENSE_TRANSFORM = {
    "exac_nontcga": "exac",
    "gnomad_exome": "gnomad",
    "gnomad_genome": "gnomad"
}
