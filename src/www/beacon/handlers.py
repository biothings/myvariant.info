import sys
from biothings.www.api.helper import BaseHandler
from biothings.utils.common import dotdict
from www.api.transform import ESResultTransformer
import logging

class BeaconHandler(BaseHandler):
    # Initialize Assembly and Datasets
    assembly_keys = {'NCBI36':'hg18', 'GRCh37':'hg19', 'GRCh38':'hg38'}
    pos_dbs = ['exac', 'cadd'] # These are hg19 ONLY
    assembly_dbs = ['dbnsfp','dbsnp','clinvar','evs','mutdb','cosmic','docm','wellderly']

    def post(self, src=None):
        self.receive_data()

    def get(self, src=None):
        self.receive_data()

    def receive_data(self):
        chrom = self.get_argument('referenceName', None)
        start = self.get_argument('start', None)
        ref = self.get_argument('referenceBases', None)
        alt = self.get_argument('alternateBases', None)
        assembly = self.get_argument('assemblyId', None)
        datasets = self.get_arguments('datasetIds', strip=False)
        include_datasets = self.get_argument('includeDatasetResponses', None)

        # Prep request for return
        allele_request = {'referenceName':chrom, 'start':start, 'referenceBases':ref,
                         'alternateBases':alt, 'assemblyId': assembly, 'datsetIds': datasets,
                         'includeDatasetResponses': include_datasets}

        if len(datasets) < 1:
            datasets = self.pos_dbs+self.assembly_dbs
        try:
            dataset_responses = []
            for dataset in datasets:
                dataset_responses.append(self.query_dataset(chrom, start, ref, alt, assembly, dataset))
            exists = any([response['exists'] for response in dataset_responses])
            out = {'exists':exists, 'alleleRequest': allele_request}
            if include_datasets:
                out['alleleDatasetRespone'] = dataset_responses
        except NameError as e:
            out = {'`error`':'{}'.format(e), 'alleleRequest': allele_request}
        except TypeError as e:
            out = {'`error`':'{}'.format(e), 'alleleRequest': allele_request}
        except AttributeError as e:
            out = {'`error`':'{}'.format(e), 'alleleRequest': allele_request}
        except:
            e = sys.exc_info()[0]
            out = {'`error`':'{}'.format(e), 'alleleRequest': allele_request}

        #Return the JSON response
        self.return_json(out)

    def query_dataset(self, chrom, start, ref, alt, assembly, dataset):
        # Initialzie output
        out = {'datasetId': dataset, 'exists':False}
        q_type = 'snp'

        # verify information and build query string
        if dataset in self.pos_dbs+self.assembly_dbs:
            if chrom and start and alt and assembly in self.assembly_keys:
                assembly = self.assembly_keys[assembly]  #get hg assembly notation
                if alt[:3] == 'DEL': # syntax: "alternateBases": "DEL85689"
                    q_type = 'del'
                    ref = ''
                elif alt[:3] == 'DUP': # "alternateBases": "DUP85689"
                    q_type = 'dup'
                    ref = ''
                elif not ref:
                    q_type = 'ins'
                    ref = ''

                q = self.format_query_string(q_type, chrom, start, ref, alt, assembly, dataset)
                # perform query and format result
                # for now always search against hg19 index...
                res = self.web_settings.es_client.search(index='_'.join([self.web_settings.ES_INDEX_BASE, 'hg19']),
                    doc_type=self.web_settings.ES_DOC_TYPE, body={"query":{"query_string":{"query":q}}}, 
                    _source=[dataset])
                _transformer = ESResultTransformer(options=dotdict({'dotfield': True}), host=self.request.host)
                res = _transformer.clean_query_GET_response(res)
                
                if res and res.get('total') > 0:
                    out = self.format_output(res, out, q_type)
        return out


    def format_query_string(self, q_type, chrom, start, ref, alt, assembly, dataset):
        # Initialize some variables specific to Deletions and Duplicatoins
        # Querying for deletions and duplcations can be done with same syntax
        # issue then comes in resolving query result deletion or a duplication
        # will perform query using same logic, and verify afterward
        del_dup = ['del', 'dup']
        if q_type in del_dup:
            length = alt[3:]
            end = int(start)+int(length)-1

        q = dataset + '.chrom:"{}" AND '.format(chrom)
        if dataset in self.pos_dbs and assembly == 'hg19':
            q += dataset + '.pos:{} AND '.format(start)
            if q_type in del_dup:
                q += 'hg19.end:{} AND '.format(end)
        elif dataset in self.assembly_dbs:
            q += dataset + '.{}.start:{} AND '.format(assembly, start)
            if q_type in del_dup:
                q += dataset + '.{}.end:{} AND '.format(assembly, end)
        else:
            return ''
        if not q_type in del_dup:
            q += dataset + '.ref:{} AND '.format(ref)
            q += dataset + '.alt:{} AND '.format(alt)
        q += '_exists_:{}'.format(dataset)

        return q


    def format_output(self, res, out, q_type):
        if q_type in ['dup', 'del']:
            hits = [hit for hit in res.get('hits') if q_type in hit['_id']]
        else:
            hits = res.get('hits')
        if len(hits) == 1:
            out['exists'] = True
            out['info'] = {k:v for k,v in hits[0].items() if not k.startswith('_')}
        else:
            out['info'] = [hit for hit in hits]
        return out


class BeaconInfoHandler(BaseHandler):
    # Use esq to grab metadata on myvariant.info
    def initialize(self, web_settings):
        super(BeaconInfoHandler, self).initialize(web_settings)
        _meta = self.web_settings.es_client.indices.get_mapping(index='_'.join([self.web_settings.ES_INDEX_BASE, 'hg19']),
                                                        doc_type=self.web_settings.ES_DOC_TYPE)
        self.m = _meta[list(_meta.keys())[0]]['mappings'][self.web_settings.ES_DOC_TYPE]['properties']
        _transformer = ESResultTransformer(options=dotdict(), host=self.request.host)
        self.meta = _transformer.clean_metadata_response(_meta)

    # Current list of datasets in myvariant.info
    dataset_names = ['dbnsfp', 'dbsnp', 'clinvar', 'evs', 'cadd', 'mutdb', 'cosmic', 'docm', 'wellderly', 'exac']


    def get(self):
        self.get_beacon_info()

    def post(self):
        self.get_beacon_info()

    def get_beacon_info(self):
        # Boilerplate Beacon Info
        out = {'id': 'myvariant.info', 'apiVersion': 'v1', 'BeaconOrganization': 'TSRI',
               'welcomeUrl': 'http://www.myvariant.info'}

        # Loop through datasets to generate info
        datasets = []
        for dataset in self.dataset_names:
            datasets.append(self.get_dataset_info(dataset))
        out['datasets'] = datasets

        # Return info
        self.return_json(out)


    def get_dataset_info(self, dataset):
        #Get Basic Dataset info
        out = {'id': dataset}
        out['version'] = self.meta['src_version'].get(dataset, None)
        out['variantCount'] = self.meta['stats'].get(dataset, None)

        # Determine assemblies supported by dataset
        assemblies = []
        dataset_keys = self.m[dataset]['properties'].keys()

        if 'hg18' in dataset_keys:
            assemblies.append('NCBI36')
        if 'hg19' in dataset_keys or dataset in ['exac', 'cadd']:
            assemblies.append('GRCh37')
        if 'hg38' in dataset_keys:
            assemblies.append('GRCh38')

        out['assemblyId'] = assemblies

        return out

