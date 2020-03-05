# ######### #
# HUB VARS  #
# ######### #
import os

DATA_HUB_DB_DATABASE = "variant_hubdb"     # db containing the following (internal use)
DATA_SRC_MASTER_COLLECTION = 'src_master'  # for metadata of each src collections
DATA_SRC_DUMP_COLLECTION = 'src_dump'      # for src data download information
DATA_SRC_BUILD_COLLECTION = 'src_build'    # for src data build information
DATA_PLUGIN_COLLECTION = 'data_plugin'     # for data plugins information
API_COLLECTION = 'api'                     # for api information (running under hub control)
CMD_COLLECTION = 'cmd'                     # for launched/running commands in shell
EVENT_COLLECTION = 'event'                 # for launched/running commands in shell

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
# size in bytes for a diff file (used in diff/reduce step)
MAX_DIFF_SIZE = 10 * 1024**2

# max length for _id field
MAX_ID_LENGTH = 512

# cache file format ("": ascii/text uncompressed, or "gz|zip|xz"
CACHE_FORMAT = "xz"

# How much memory hub is allowed to use:
# - "auto", let hub decides (will use 50%-60% of available RAM)
# - None: no limit
# - otherwise specify a number in bytes
HUB_MAX_MEM_USAGE = None

# Max number of *processes* hub can access to run jobs
HUB_MAX_WORKERS = int(os.cpu_count() / 4)
# Max number of *threads* hub can use (will default to HUB_MAX_WORKERS if undefined)
HUB_MAX_THREADS = HUB_MAX_WORKERS
MAX_SYNC_WORKERS = HUB_MAX_WORKERS

# Max queued jobs in job manager
# this shouldn't be 0 to make sure a job is pending and ready to be processed
# at any time (avoiding job submission preparation) but also not a huge number
# as any pending job will consume some memory).
MAX_QUEUED_JOBS = os.cpu_count() * 4

# Hub environment (like, prod, dev, ...)
# Used to generate remote metadata file, like "latest.json", "versions.json"
# If non-empty, this constant will be used to generate those url, as a prefix 
# with "-" between. So, if "dev", we'll have "dev-latest.json", etc...
# "" means production
HUB_ENV = ""

# Hub name/icon url/version, for display purpose
HUB_NAME = "MyVariant"
HUB_ICON = "http://biothings.io/static/img/myvariant-logo-shiny.svg"
HUB_VERSION = "0.2"


# Pre-prod/test ES definitions
INDEX_CONFIG = {
        "build_config_key" : "assembly", # used to select proper idxr/syncer
        "indexer_select": {
            # default
            None : "hub.dataindex.indexer.VariantIndexer",
            # when there's a cold_collection definition
            "build_config.cold_collection" : "hub.dataindex.indexer.ColdHotVariantIndexer",
            },
        "env" : {
            "prod" : {
                "host" : "<PRODSERVER>:9200",
                "indexer" : {
                    "args" : {
                        "timeout" : 300,
                        "retry_on_timeout" : True,
                        "max_retries" : 10,
                        },
                    },
                "index" : [
                    # keys match build_config_key value
                    {"index": "myvariant_current_hg19", "doc_type": "variant", "hg19": True},
                    {"index": "myvariant_current_hg38", "doc_type": "variant", "hg38": True},
                    ],
                },
            "test" : {
                "host" : "localhost:9200",
                "indexer" : {
                    "args" : {
                        "timeout" : 300,
                        "retry_on_timeout" : True,
                        "max_retries" : 10,
                        },
                    },
                "index" : [
                    # "hg19/hg38" are flags used to filter compatible index from the UI
                    {"index": "myvariant_current_hg19", "doc_type": "variant", "hg19": True},
                    {"index": "myvariant_current_hg38", "doc_type": "variant", "hg38": True},
                    ],
                },
            },
        }

# Snapshot environment configuration
SNAPSHOT_CONFIG = {
        "env" : {
            "prod" : {
                "cloud" : {
                    "type" : "aws", # default, only one supported by now
                    "access_key" : None,
                    "secret_key" : None,
                    },
                "repository" : {
                    "name" : "variant_repository",
                    "type" : "s3",
                    "settings" : {
                        "bucket" : "<SNAPSHOT_BUCKET_NAME>",
                        "base_path" : "myvariant.info/$(Y)", # per year
                        "region" : "us-west-2",
                        },
                    "acl" : "private",
                    },
                "indexer" : {
                    # reference to INDEX_CONFIG
                    "env" : "prod",
                    },
                # when creating a snapshot, how long should we wait before querying ES
                # to check snapshot status/completion ? (in seconds)
                "monitor_delay" : 60 * 5,
                },
            "demo" : {
                "cloud" : {
                    "type" : "aws", # default, only one supported by now
                    "access_key" : None,
                    "secret_key" : None,
                    },
                "repository" : {
                    "name" : "variant_repository-demo",
                    "type" : "s3",
                    "settings" : {
                        "bucket" : "<SNAPSHOT_DEMO_BUCKET_NAME>",
                        "base_path" : "myvariant.info/$(Y)", # per year
                        "region" : "us-west-2",
                        },
                    "acl" : "public",
                    },
                "indexer" : {
                    # reference to INDEX_CONFIG
                    "env" : "test",
                    },
                # when creating a snapshot, how long should we wait before querying ES
                # to check snapshot status/completion ? (in seconds)
                "monitor_delay" : 10,
                }
            }
        }

# Release configuration
# Each root keys define a release environment (test, prod, ...)
RELEASE_CONFIG = {
        "env" : {
            "prod" : {
                "cloud" : {
                    "type" : "aws", # default, only one supported by now
                    "access_key" : None,
                    "secret_key" : None,
                    },
                "release" : {
                    "bucket" : "<RELEASES_BUCKET_NAME>",
                    "region" : "us-west-2",
                    "folder" : "myvariant.info",
                    "auto" : True, # automatically generate release-note ?
                    },
                "diff" : {
                    "bucket" : "<DIFFS_BUCKET_NAME>",
                    "folder" : "myvariant.info",
                    "region" : "us-west-2",
                    "auto" : True, # automatically generate diff ? Careful if lots of changes
                    },
                },
            "demo": {
                "cloud" : {
                    "type" : "aws", # default, only one supported by now
                    "access_key" : None,
                    "secret_key" : None,
                    },
                "release" : {
                    "bucket" : "<RELEASES_BUCKET_NAME>",
                    "region" : "us-west-2",
                    "folder" : "myvariant.info-demo",
                    "auto" : True, # automatically generate release-note ?
                    },
                "diff" : {
                    "bucket" : "<DIFFS_BUCKET_NAME>",
                    "folder" : "myvariant.info",
                    "region" : "us-west-2",
                    "auto" : True, # automatically generate diff ? Careful if lots of changes
                    },
                }
            }
        }

SLACK_WEBHOOK = None

# SSH port for hub console
HUB_SSH_PORT = 7022
HUB_API_PORT = 7080

################################################################################
# HUB_PASSWD
################################################################################
# The format is a dictionary of 'username': 'cryptedpassword'
# Generate crypted passwords with 'openssl passwd -crypt'
HUB_PASSWD = {"guest":"9RKfd8gDuNf0Q"}

# cached data (it None, caches won't be used at all)
CACHE_FOLDER = None

# when publishing releases, specify the targetted (ie. required) standalone version
STANDALONE_VERSION = "standalone_v3"

import logging
from biothings.utils.loggers import setup_default_log

########################################
# APP-SPECIFIC CONFIGURATION VARIABLES #
########################################
# The following variables should or must be defined in your
# own application. Create a config.py file, import that config_common
# file as:
#
#   from config_hub import *
#
# then define the following variables to fit your needs. You can also override any
# any other variables in this file as required. Variables defined as ValueError() exceptions
# *must* be defined
#
from biothings import ConfigurationError, ConfigurationDefault, ConfigurationValue

# Individual source database connection
DATA_SRC_SERVER = ConfigurationError("Define hostname for source database")
DATA_SRC_PORT = ConfigurationError("Define port for source database")
DATA_SRC_DATABASE = ConfigurationError("Define name for source database")
DATA_SRC_SERVER_USERNAME = ConfigurationError("Define username for source database connection (or None if not needed)")
DATA_SRC_SERVER_PASSWORD = ConfigurationError("Define password for source database connection (or None if not needed)")

# Target (merged collection) database connection
DATA_TARGET_SERVER = ConfigurationError("Define hostname for target database (merged collections)")
DATA_TARGET_PORT = ConfigurationError("Define port for target database (merged collections)")
DATA_TARGET_DATABASE = ConfigurationError("Define name for target database (merged collections)")
DATA_TARGET_SERVER_USERNAME = ConfigurationError("Define username for target database connection (or None if not needed)")
DATA_TARGET_SERVER_PASSWORD = ConfigurationError("Define password for target database connection (or None if not needed)")

HUB_DB_BACKEND = ConfigurationError("Define Hub DB connection")
# Internal backend. Default to mongodb
# For now, other options are: mongodb, sqlite3, elasticsearch
#HUB_DB_BACKEND = {
#        "module" : "biothings.utils.sqlite3",
#        "sqlite_db_foder" : "./db",
#        }
#HUB_DB_BACKEND = {
#        "module" : "biothings.utils.mongo",
#        "uri" : "mongodb://localhost:27017",
#        #"uri" : "mongodb://user:passwd@localhost:27017", # mongodb std URI
#        }
#HUB_DB_BACKEND = {
#        "module" : "biothings.utils.es",
#        "host" : "localhost:9200",
#        }

#ES_HOST = ConfigurationError("Define ElasticSearch host used for index creation (eg localhost:9200)")

# Path to a folder to store all downloaded files, logs, caches, etc...
DATA_ARCHIVE_ROOT = ConfigurationError("Define path to folder which will contain all downloaded data, cache files, etc...")

# Path to a folder to store all 3rd party parsers, dumpers, etc...
DATA_PLUGIN_FOLDER = ConfigurationDefault(
        default="./plugins",
        desc="Define path to folder which will contain all 3rd party parsers, dumpers, etc...")

# Path to folder containing diff files
DIFF_PATH = ConfigurationDefault(
        default=ConfigurationValue("""os.path.join(DATA_ARCHIVE_ROOT,"diff")"""),
        desc="Define path to folder which will contain output files from diff")

# Path to folder containing release note files
RELEASE_PATH = ConfigurationDefault(
        default=ConfigurationValue("""os.path.join(DATA_ARCHIVE_ROOT,"release")"""),
        desc="Define path to folder which will contain release files")

# this dir must be created manually
LOG_FOLDER = ConfigurationDefault(
        default=ConfigurationValue("""os.path.join(DATA_ARCHIVE_ROOT,"logs")"""),
        desc="Define path to folder which will contain log files")

IDS_S3_BUCKET =  ConfigurationDefault(
        default="myvariant-ids",
        desc="Define a bucket name to upload myvariant _ids to")

# default hub logger
logger = ConfigurationDefault(
        default=logging,
        desc="Provide a default hub logger instance (use setup_default_log(name,log_folder)")

ACTIVE_DATASOURCES = [
    # auto-updated
    'hub.dataload.sources.clinvar',
    'hub.dataload.sources.dbsnp',
    'hub.dataload.sources.dbnsfp',
    'hub.dataload.sources.exac',
    'hub.dataload.sources.clingen',

    # manually-updated
    'hub.dataload.sources.cadd',
    'hub.dataload.sources.grasp',
    'hub.dataload.sources.emv',
    'hub.dataload.sources.evs',
    'hub.dataload.sources.geno2mp',
    'hub.dataload.sources.uniprot',
    'hub.dataload.sources.civic',
    'hub.dataload.sources.cgi',
    'hub.dataload.sources.gnomad',

    # dead-resources
    'hub.dataload.sources.cosmic',
    'hub.dataload.sources.wellderly',
    'hub.dataload.sources.snpedia',
    'hub.dataload.sources.mutdb',
    'hub.dataload.sources.gwassnps',
    'hub.dataload.sources.docm',

    # generated resources
    'hub.dataload.sources.snpeff',
    ]
