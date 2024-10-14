# ######### #
# HUB VARS  #
# ######### #
import copy

# Hub name/icon url/version, for display purpose
HUB_NAME = "MyVariant Data Hub"
HUB_ICON = "http://biothings.io/static/img/myvariant-logo-shiny.svg"
HUB_VERSION = "0.2"


# Pre-prod/test ES definitions
INDEX_CONFIG = {
    "build_config_key": "assembly",  # used to select proper idxr/syncer
    "indexer_select": {
        # default
        None: "hub.dataindex.indexer.VariantIndexer",
        # when there's a cold_collection definition
        "build_config.cold_collection": "hub.dataindex.indexer.ColdHotVariantIndexer",
    },
    "env": {
        "prod": {
            "host": "<PRODSERVER>:9200",
            "indexer": {
                    "args": {
                        "timeout": 300,
                        "retry_on_timeout": True,
                        "max_retries": 10,
                    },
                    #"concurrency": HUB_MAX_WORKERS,
                    "bulk": {
                        "chunk_size": 500,  # 500 by default
                        "max_chunk_bytes": 104857600  # 100Mb by default
                    }
            },
            "index": [
                # keys match build_config_key value
                {"index": "myvariant_current_hg19", "doc_type": "variant", "hg19": True},
                {"index": "myvariant_current_hg38", "doc_type": "variant", "hg38": True},
            ],
        },
        "local": {
            "host": "http://localhost:9200",
            "indexer": {
                    "args": {
                        "timeout": 300,
                        "retry_on_timeout": True,
                        "max_retries": 10,
                    },
                    #"concurrency": HUB_MAX_WORKERS,
                    "bulk": {
                        "chunk_size": 500,  # 500 by default
                        "max_chunk_bytes": 104857600  # 100Mb by default
                    }
            },
            "index": [
                # "hg19/hg38" are flags used to filter compatible index from the UI
                {"index": "myvariant_current_hg19", "doc_type": "variant", "hg19": True},
                {"index": "myvariant_current_hg38", "doc_type": "variant", "hg38": True},
            ],
        },
    },
}

# Snapshot environment configuration
SNAPSHOT_CONFIG = {
    "env": {
        "prod": {
            "cloud": {
                "type": "aws",  # default, only one supported by now
                "access_key": None,
                "secret_key": None,
            },
            "repository": {
                "name": "variant_repository-$(Y)",
                "type": "s3",
                "settings": {
                    "bucket": "<SNAPSHOT_BUCKET_NAME>",
                    "base_path": "myvariant",
                    "region": "us-west-2",
                },
                "acl": "private",
            },
            "indexer": {
                # reference to INDEX_CONFIG
                "env": "local",
            },
            # when creating a snapshot, how long should we wait before querying ES
            # to check snapshot status/completion ? (in seconds)
            "monitor_delay": 60 * 5,
        },
        "demo": {
            "cloud": {
                "type": "aws",  # default, only one supported by now
                "access_key": None,
                "secret_key": None,
            },
            "repository": {
                "name": "variant_repository-demo-$(Y)",
                "type": "s3",
                "settings": {
                    "bucket": "<SNAPSHOT_DEMO_BUCKET_NAME>",
                    "base_path": "myvariant.info/$(Y)",  # per year
                    "region": "us-west-2",
                },
                "acl": "public",
            },
            "indexer": {
                # reference to INDEX_CONFIG
                "env": "local",
            },
            # when creating a snapshot, how long should we wait before querying ES
            # to check snapshot status/completion ? (in seconds)
            "monitor_delay": 10,
        }
    }
}

# Release configuration
# Each root keys define a release environment (test, prod, ...)
RELEASE_CONFIG = {
    "env": {
        "prod-hg19": {
            "cloud": {
                "type": "aws",  # default, only one supported by now
                "access_key": None,
                "secret_key": None,
            },
            "release": {
                "bucket": "<RELEASES_BUCKET_NAME>",
                "region": "us-west-2",
                "folder": "myvariant.info-hg19",
                "auto": True,  # automatically generate release-note ?
            },
            "diff": {
                "bucket": "<DIFFS_BUCKET_NAME>",
                "folder": "myvariant.info-hg19",
                "region": "us-west-2",
                "auto": True,  # automatically generate diff ? Careful if lots of changes
            },
        },
        "demo-hg19": {
            "cloud": {
                "type": "aws",  # default, only one supported by now
                "access_key": None,
                "secret_key": None,
            },
            "release": {
                "bucket": "<RELEASES_BUCKET_NAME>",
                "region": "us-west-2",
                "folder": "myvariant.info-demo_hg19",
                "auto": True,  # automatically generate release-note ?
            },
            "diff": {
                "bucket": "<DIFFS_BUCKET_NAME>",
                "folder": "myvariant.info-demo_hg19",
                "region": "us-west-2",
                "auto": True,  # automatically generate diff ? Careful if lots of changes
            },
        }
    }
}


# fir hg38 it's almost the same
# prod
RELEASE_CONFIG["env"]["prod-hg38"] = copy.deepcopy(RELEASE_CONFIG["env"]["prod-hg19"])
RELEASE_CONFIG["env"]["prod-hg38"]["release"]["folder"] = "myvariant.info-hg38"
RELEASE_CONFIG["env"]["prod-hg38"]["diff"]["folder"] = "myvariant.info-hg38"
# demo
RELEASE_CONFIG["env"]["demo-hg38"] = copy.deepcopy(RELEASE_CONFIG["env"]["demo-hg19"])
RELEASE_CONFIG["env"]["demo-hg38"]["release"]["folder"] = "myvariant.info-demo_hg38"
RELEASE_CONFIG["env"]["demo-hg38"]["diff"]["folder"] = "myvariant.info-demo_hg38"


SLACK_WEBHOOK = None

# when publishing releases, specify the targetted (ie. required) standalone version
STANDALONE_VERSION = {"branch": "standalone_v3"}

# Autohub configuration, either from a static definition...
STANDALONE_CONFIG = {
    "_default": {
        "es_host": "http://localhost:9200",
        "index": "myvariant_test",
        "doc_type": "variant"
    },
    "myvariant.info-hg19": {
        "es_host": "prodserver:9200",
        "index": "myvariant_prod_hg19",
        "doc_type": "variant"
    },
    "myvariant.info-hg38": {
        "es_host": "prodserver:9200",
        "index": "myvariant_prod_hg38",
        "doc_type": "variant"
    },
}
# ... or using a dynamic indexer factory and ES host (index names are then
# taken from VERSION_URLS and all are managed on one given ES host)
#AUTOHUB_INDEXER_FACTORY = "biothings.hub.dataindex.indexer.DynamicIndexerFactory"
#AUTOHUB_ES_HOST = "localhost:9200"


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

# ####################### #-
# MyVariant Specific VARS #
# ####################### #

# define valid sources to get chrom from, and for each, name of the chrom field
CHROM_FIELDS = {'cadd': 'chrom', 'clinvar': 'chrom', 'cosmic': 'chrom', 'dbnsfp': 'chrom',
                'dbsnp': 'chrom', 'docm': 'chrom', 'evs': 'chrom', 'exac': 'chrom'}

HG38_FIELDS = ['clinvar.hg38', 'dbnsfp.hg38', 'evs.hg38']
HG19_FIELDS = ['clinvar.hg19', 'cosmic.hg19', 'dbnsfp.hg19',
               'dbsnp.hg19', 'docm.hg19', 'evs.hg19', 'grasp.hg19']

# Max length for vcf.alt and vcf.ref fields (must be less than 32k as a keyword field in ElasticSearch)
# otherwise, Elasticsearch will raise an error like this:
#   "type": "max_bytes_length_exceeded_exception",
#   "reason": "bytes can be at most 32766 in length; got 32770"
MAX_REF_ALT_LEN = 10000

# max length for _id field
MAX_ID_LENGTH = 512
