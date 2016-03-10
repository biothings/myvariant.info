import os.path

SRC_PATH = os.path.split(os.path.abspath(__file__))[0]

######################################
# For both dataload and www modules  #
######################################

ES_HOST = 'localhost:9200'
ES_INDEX_NAME = 'myvariant_current'
ES_DOC_TYPE = 'variant'


###############################
# For dataload module only    #
###############################

# defautlt number_of_shards when create a new index
ES_NUMBER_OF_SHARDS = 20

DATA_SRC_SERVER = 'localhost'
DATA_SRC_PORT = 27017
DATA_SRC_DATABASE = 'variantdoc'
#DATA_SRC_MASTER_COLLECTION = 'src_master'   #for metadata of each src collections
#DATA_SRC_DUMP_COLLECTION = 'src_dump'       #for src data download information
#DATA_SRC_BUILD_COLLECTION = 'src_build'       #for src data build information

DATA_SERVER_USERNAME = ''
DATA_SERVER_PASSWORD = ''

HG19_DATAFILE = '/path/to/hg19_bit_p13.pyobj'

###############################
# For www module only         #
###############################
FIELD_NOTES_PATH = os.path.join(SRC_PATH, 'www/context/myvariant_field_table_notes.json')
JSONLD_CONTEXT_PATH = os.path.join(SRC_PATH, 'www/context/context.json')
GA_ACCOUNT = ''
RUN_IN_PROD = False    # set to True in prod server
