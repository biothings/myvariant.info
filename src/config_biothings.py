# -*- coding: utf-8 -*-
# *****************************************************************************
# Elasticsearch variables
# *****************************************************************************
# elasticsearch server transport url
ES_HOST = 'su07:9200'
# elasticsearch index name
ES_INDEX_NAME = 'myvariant_current'
# elasticsearch document type
ES_DOC_TYPE = 'variant'
# Only these options are passed to the elasticsearch query from kwargs
ALLOWED_OPTIONS = ['_source', 'start', 'from_', 'size',
                   'sort', 'explain', 'version', 'facets', 'fetch_all']
ES_SCROLL_TIME = '1m'
ES_SCROLL_SIZE = 1000
ES_QUERY_MODULE = 'www.api.es'

# *****************************************************************************
# myvariant.info specific settings
# *****************************************************************************
HG38_FIELDS = ['clinvar.hg38', 'dbnsfp.hg38', 'evs.hg38']
HG19_FIELDS = ['clinvar.hg19', 'cosmic.hg19', 'dbnsfp.hg19', 'dbsnp.hg19', 'docm.hg19', 'evs.hg19', 'grasp.hg19'] #, 'mutdb.hg19', 'wellderly.hg19']
CHROM_FIELDS = ['cadd.chrom', 'clinvar.chrom', 'cosmic.chrom', 'dbnsfp.chrom', 'dbsnp.chrom', 'docm.chrom',
                'evs.chrom', 'exac.chrom']#, 'mutdb.chrom', 'wellderly.chrom']

# *****************************************************************************
# Google Analytics Settings
# *****************************************************************************
# Google Analytics Account ID
GA_ACCOUNT = ''
# Turn this to True to start google analytics tracking
GA_RUN_IN_PROD = False

# 'category' in google analytics event object
GA_EVENT_CATEGORY = 'v1_api'
# 'action' for get request in google analytics event object
GA_EVENT_GET_ACTION = 'get'
# 'action' for post request in google analytics event object
GA_EVENT_POST_ACTION = 'post'
# url for google analytics tracker
GA_TRACKER_URL = 'MyVariant.info'

# *****************************************************************************
# URL settings
# *****************************************************************************
# For URL stuff
ANNOTATION_ENDPOINT = 'variant'
QUERY_ENDPOINT = 'query'
API_VERSION = 'v1'
# TODO Fill in a status id here
STATUS_CHECK_ID = 'chr1:g.218631822G>A'
# Path to a file containing a json object with information about elasticsearch fields
FIELD_NOTES_PATH = 'www/context/myvariant_field_table_notes.json'
JSONLD_CONTEXT_PATH = 'www/context/context.json'
NOSETEST_SETTINGS = 'tests.nosetest_config'
