# -*- coding: utf-8 -*-
from biothings.web.settings.default import *


# *****************************************************************************
# Elasticsearch variables
# *****************************************************************************
ES_HOST = 'localhost:9200'
ES_INDEX = 'myvariant_current_hg19'
ES_DOC_TYPE = 'variant'
ES_INDICES = {
    'hg19': 'myvariant_current_hg19',
    'hg38': 'myvariant_current_hg38'
}

# *****************************************************************************
# App URL Patterns
# *****************************************************************************
API_VERSION = 'v1'
APP_LIST = [
    (r'/v1/variant/(chr.{1,2}):(?!g\.)[g\.]{0,2}(\d+.*)', 'tornado.web.RedirectHandler', {'url': '/v1/variant/{0}:g.{1}'}),
] + APP_LIST
# *****************************************************************************
# ES Query Pipeline
# *****************************************************************************
ES_QUERY_BUILDER = 'web.pipelines.MVQueryBuilder'
ES_QUERY_BACKEND = 'web.pipelines.MVQueryBackend'

# *****************************************************************************
# Analytics & Tracking
# *****************************************************************************

GA_ACTION_QUERY_GET = 'query_get'
GA_ACTION_QUERY_POST = 'query_post'
GA_ACTION_ANNOTATION_GET = 'variant_get'
GA_ACTION_ANNOTATION_POST = 'variant_post'
GA_TRACKER_URL = 'MyVariant.info'
URL_BASE = 'http://myvariant.info'

# for logo on format=html
HTML_OUT_HEADER_IMG = "/static/favicon.ico"

# for title line on format=html
HTML_OUT_TITLE = """<p style="font-family:'Open Sans',sans-serif;font-weight:bold; font-size:16px;"><a href="http://myvariant.info" target="_blank" style="text-decoration: none; color: black">MyVariant.info - Variant Annotation as a Service</a></p>"""

METADATA_DOCS_URL = "http://docs.myvariant.info/en/latest/doc/data.html"
QUERY_DOCS_URL = "http://docs.myvariant.info/en/latest/doc/variant_query_service.html"
ANNOTATION_DOCS_URL = "http://docs.myvariant.info/en/latest/doc/variant_annotation_service.html"

# kwargs for status check get
STATUS_CHECK = {
    'id': 'chr1:g.218631822G>A',
    'index': 'myvariant_current_hg19',
    'doc_type': 'variant'
}

# *****************************************************************************
# User Input Control
# *****************************************************************************
ANNOTATION_ID_REGEX_LIST = [(re.compile(r'rs[0-9]+', re.I), 'dbsnp.rsid'),
                            (re.compile(r'rcv[0-9\.]+', re.I), 'clinvar.rcv.accession'),
                            (re.compile(r'var_[0-9]+', re.I), 'uniprot.humsavar.ftid')]
ANNOTATION_DEFAULT_SCOPES = ['_id', 'clingen.caid']

# typedef for assembly parameter
ASSEMBLY_TYPEDEF = {'assembly': {'type': str, 'default': 'hg19', 'enum': ('hg19', 'hg38')}}


ANNOTATION_GET_ES_KWARGS = dict(ASSEMBLY_TYPEDEF)
ANNOTATION_POST_ES_KWARGS = dict(ASSEMBLY_TYPEDEF)
QUERY_GET_ES_KWARGS.update(ASSEMBLY_TYPEDEF)
QUERY_POST_ES_KWARGS = dict(ASSEMBLY_TYPEDEF)

ANNOTATION_GET_ESQB_KWARGS.update(ASSEMBLY_TYPEDEF)
ANNOTATION_POST_ESQB_KWARGS.update(ASSEMBLY_TYPEDEF)
QUERY_GET_ESQB_KWARGS.update(ASSEMBLY_TYPEDEF)
QUERY_POST_ESQB_KWARGS.update(ASSEMBLY_TYPEDEF)

LICENSE_TRANSFORM = {
    "exac_nontcga": "exac",
    "gnomad_exome": "gnomad",
    "gnomad_genome": "gnomad"
}

JSONLD_CONTEXT_PATH = 'web/context/context.json'
AVAILABLE_FIELDS_NOTES_PATH = 'web/context/myvariant_field_table_notes.json'
