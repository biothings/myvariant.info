# -*- coding: utf-8 -*-
from biothings.www.settings.default import *
from www.api.query_builder import ESQueryBuilder
from www.api.query import ESQuery
from www.api.transform import ESResultTransformer
from www.api.handlers import VariantHandler, QueryHandler, MetadataHandler, StatusHandler, DemoHandler
from www.beacon.handlers import BeaconHandler, BeaconInfoHandler

# *****************************************************************************
# Elasticsearch variables
# *****************************************************************************
# elasticsearch server transport url
ES_HOST = 'localhost:9200'
# elasticsearch index name
ES_INDEX = 'myvariant_current'
# base index name - used to switch indices
ES_INDEX_BASE = 'myvariant_current'
# Assemblies supported (must resolve to a valid ES index, along with ES_INDEX_BASE)
SUPPORTED_ASSEMBLIES = ['hg19', 'hg38']
# elasticsearch document type
ES_DOC_TYPE = 'variant'

API_VERSION = 'v1'

# *****************************************************************************
# App URL Patterns
# *****************************************************************************
APP_LIST = [
    (r"/status", StatusHandler),
    (r"/metadata/?", MetadataHandler),
    (r"/metadata/fields/?", MetadataHandler),
    (r"/demo/?$", DemoHandler),
    (r"/beacon/query?", BeaconHandler),
    (r"/beacon/info", BeaconInfoHandler),
    (r"/{}/variant/(.+)/?".format(API_VERSION), VariantHandler),
    (r"/{}/variant/?$".format(API_VERSION), VariantHandler),
    (r"/{}/query/?".format(API_VERSION), QueryHandler),
    (r"/{}/metadata/?".format(API_VERSION), MetadataHandler),
    (r"/{}/metadata/fields/?".format(API_VERSION), MetadataHandler),
]

###############################################################################
#   app-specific query builder, query, and result transformer classes
###############################################################################

# *****************************************************************************
# Subclass of biothings.www.api.es.query_builder.ESQueryBuilder to build
# queries for this app
# *****************************************************************************
ES_QUERY_BUILDER = ESQueryBuilder
# *****************************************************************************
# Subclass of biothings.www.api.es.query.ESQuery to execute queries for this app
# *****************************************************************************
ES_QUERY = ESQuery
# *****************************************************************************
# Subclass of biothings.www.api.es.transform.ESResultTransformer to transform
# ES results for this app
# *****************************************************************************
ES_RESULT_TRANSFORMER = ESResultTransformer

GA_ACTION_QUERY_GET = 'query_get'
GA_ACTION_QUERY_POST = 'query_post'
GA_ACTION_ANNOTATION_GET = 'variant_get'
GA_ACTION_ANNOTATION_POST = 'variant_post'
GA_TRACKER_URL = 'MyVariant.info'

STATUS_CHECK_ID = 'chr1:g.218631822G>A'

# hipchat message color for this app
HIPCHAT_MESSAGE_COLOR = 'green'

# Allow searching by other ids with annotation endpoint
ANNOTATION_ID_REGEX_LIST = [(re.compile(r'rs[0-9]+', re.I), 'dbsnp.rsid'),
                            (re.compile(r'rcv[0-9\.]+', re.I), 'clinvar.rcv.accession'),
                            (re.compile(r'var_[0-9]+', re.I), 'uniprot.humsavar.ftid')]

ASSEMBLY_TYPEDEF = {'assembly': {'type': str, 'default': 'hg19'}}
ANNOTATION_GET_ESQB_KWARGS.update(ASSEMBLY_TYPEDEF)
ANNOTATION_POST_ESQB_KWARGS.update(ASSEMBLY_TYPEDEF)
QUERY_GET_ESQB_KWARGS.update(ASSEMBLY_TYPEDEF)
QUERY_POST_ESQB_KWARGS.update(ASSEMBLY_TYPEDEF)
METADATA_GET_ESQB_KWARGS.update(ASSEMBLY_TYPEDEF)

JSONLD_CONTEXT_PATH = 'www/context/context.json'
