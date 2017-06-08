# -*- coding: utf-8 -*-
# LOGGING #
import logging, os, datetime, time

LOGGER_NAME = "hub"
from biothings.utils.loggers import setup_default_log

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
URL_BASE = 'http://myvariant.info'

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

# ################### #
# MYVARIANT HUB VARS  #
# ################### #

DATA_SRC_MASTER_COLLECTION = 'src_master'   # for metadata of each src collections
DATA_SRC_DUMP_COLLECTION = 'src_dump'       # for src data download information
DATA_SRC_BUILD_COLLECTION = 'src_build'     # for src data build information

DATA_TARGET_MASTER_COLLECTION = 'db_master'

# where to store info about processes launched by the hub
RUN_DIR = './run'

# define valid sources to get chrom from, and for each, name of the chrom field
CHROM_FIELDS = {'cadd':'chrom', 'clinvar':'chrom', 'cosmic':'chrom', 'dbnsfp':'chrom',
                'dbsnp':'chrom', 'docm':'chrom', 'evs':'chrom', 'exac':'chrom'}

HG38_FIELDS = ['clinvar.hg38', 'dbnsfp.hg38', 'evs.hg38']
HG19_FIELDS = ['clinvar.hg19', 'cosmic.hg19', 'dbnsfp.hg19', 'dbsnp.hg19', 'docm.hg19', 'evs.hg19', 'grasp.hg19']

# Max length for vcf.alt and vcf.ref fields (must be less than 32k, ElasticSearch limit)
MAX_REF_ALT_LEN = 1000

# reporting diff results, number of IDs to consider (to avoid too much mem usage)
MAX_REPORTED_IDS = 1000
# for diff updates, number of IDs randomly picked as examples when rendering the report
MAX_RANDOMLY_PICKED = 10

# ES s3 repository to use snapshot/restore (must be pre-configured in ES)
SNAPSHOT_REPOSITORY = "variant_repository"

# cache file format ("": ascii/text uncompressed, or "gz|zip|xz"
CACHE_FORMAT = "xz"

# Max queued jobs in job manager
# this shouldn't be 0 to make sure a job is pending and ready to be processed
# at any time (avoiding job submission preparation) but also not a huge number
# as any pending job will consume some memory).
MAX_QUEUED_JOBS = os.cpu_count() * 4

# when creating a snapshot, how long should we wait before querying ES
# to check snapshot status/completion ? (in seconds)
# Since myvariant's indices are pretty big, a whole snaphost won't happne in few secs,
# let's just monitor the status every 5min
MONITOR_SNAPSHOT_DELAY = 5 * 60

# Hub environment (like, prod, dev, ...)
# Used to generate remote metadata file, like "latest.json", "versions.json"
# If non-empty, this constant will be used to generate those url, as a prefix 
# with "-" between. So, if "dev", we'll have "dev-latest.json", etc...
# "" means production
HUB_ENV = ""


# Pre-prod/test ES definitions
# (see bt.databuild.backend.create_backend() for the notation)
ES_TEST_HOST = 'localhost:9200'
ES_TEST_HG19 = (ES_TEST_HOST,"myvariant_current_hg19","variant")
ES_TEST_HG38 = (ES_TEST_HOST,"myvariant_current_hg38","variant")
# Prod ES definitions
ES_PROD_HG19 = (ES_PROD_HOST,"myvariant_current_hg19","variant")
ES_PROD_HG38 = (ES_PROD_HOST,"myvariant_current_hg38","variant")
