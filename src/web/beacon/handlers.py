import sys

from biothings.web.handlers import BaseAPIHandler
from biothings.web.handlers import BaseESRequestHandler
from biothings.utils.common import dotdict


class BeaconHandler(BaseESRequestHandler):
    # Initialize Assembly and Datasets
    assembly_keys = {'NCBI36': 'hg18', 'GRCh37': 'hg19', 'GRCh38': 'hg38'}
    pos_dbs = ['exac', 'cadd']  # These are hg19 ONLY
    assembly_dbs = ['dbnsfp', 'dbsnp', 'clinvar', 'evs', 'mutdb', 'cosmic', 'docm', 'wellderly']

    def post(self, src=None):
        self.receive_data()
        self.ga_event_object_ret['action'] = 'beacon_post'

    def get(self, src=None):
        self.receive_data()
        self.ga_event_object_ret['action'] = 'beacon_get'

    def receive_data(self):
        chrom = self.get_argument('referenceName', None)
        start = self.get_argument('start', None)
        ref = self.get_argument('referenceBases', None)
        alt = self.get_argument('alternateBases', None)
        assembly = self.get_argument('assemblyId', None)
        datasets = self.get_arguments('datasetIds', strip=False)
        include_datasets = self.get_argument('includeDatasetResponses', None)

        # Prep request for return
        allele_request = {
            'referenceName': chrom, 'start': start, 'referenceBases': ref,
            'alternateBases': alt, 'assemblyId': assembly, 'datsetIds': datasets,
            'includeDatasetResponses': include_datasets
        }
        if len(datasets) < 1:
            datasets = self.pos_dbs + self.assembly_dbs
        try:
            dataset_responses = []
            for dataset in datasets:
                dataset_responses.append(self.query_dataset(
                    chrom, start, ref, alt, assembly, dataset))
            exists = any([response['exists'] for response in dataset_responses])
            out = {'exists': exists, 'alleleRequest': allele_request}
            if include_datasets:
                out['alleleDatasetRespone'] = dataset_responses
        except NameError as e:
            out = {'`error`': '{}'.format(e), 'alleleRequest': allele_request}
        except TypeError as e:
            out = {'`error`': '{}'.format(e), 'alleleRequest': allele_request}
        except AttributeError as e:
            out = {'`error`': '{}'.format(e), 'alleleRequest': allele_request}
        except BaseException:
            e = sys.exc_info()[0]
            out = {'`error`': '{}'.format(e), 'alleleRequest': allele_request}

        # Return the JSON response
        self.finish(out)

    def query_dataset(self, chrom, start, ref, alt, assembly, dataset):
        # Initialzie output
        out = {'datasetId': dataset, 'exists': False}
        q_type = 'snp'

        # verify information and build query string
        if dataset in self.pos_dbs + self.assembly_dbs:
            if chrom and start and alt and assembly in self.assembly_keys:
                assembly = self.assembly_keys[assembly]  # get hg assembly notation
                if alt[:3] == 'DEL':  # syntax: "alternateBases": "DEL85689"
                    q_type = 'del'
                    ref = ''
                elif alt[:3] == 'DUP':  # "alternateBases": "DUP85689"
                    q_type = 'dup'
                    ref = ''
                elif not ref:
                    q_type = 'ins'
                    ref = ''

                q = self.format_query_string(q_type, chrom, start, ref, alt, assembly, dataset)
                # perform query and format result
                # for now always search against hg19 index...
                res = self.web_settings.es_client.search(
                    index=self.web_settings.ES_INDICES[assembly],
                    body={"query": {"query_string": {"query": q}}},
                    _source=[dataset]
                )
                res = self.query_transform.transform(res, dotdict(dotfield=True))
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
            end = int(start) + int(length) - 1

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
        if q_type not in del_dup:
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
            out['info'] = {k: v for k, v in hits[0].items() if not k.startswith('_')}
        else:
            out['info'] = [hit for hit in hits]
        return out


class BeaconInfoHandler(BaseAPIHandler):

    # Current list of datasets in myvariant.info
    dataset_names = [
        'dbnsfp', 'dbsnp', 'clinvar', 'evs', 'cadd',
        'mutdb', 'cosmic', 'docm', 'wellderly', 'exac'
    ]

    def prepare(self):
        self.meta = {
            'GRCh37': self.web_settings.source_metadata['hg19']['src'],
            'GRCh38': self.web_settings.source_metadata['hg38']['src']
        }

    def get(self):
        self.get_beacon_info()
        self.ga_event_object_ret['action'] = 'beacon_info_post'

    def post(self):
        self.get_beacon_info()
        self.ga_event_object_ret['action'] = 'beacon_info_post'

    def get_beacon_info(self):
        # Boilerplate Beacon Info
        out = {
            'id': 'myvariant.info',
            'apiVersion': 'v1',
            'BeaconOrganization': 'TSRI',
            'welcomeUrl': 'http://www.myvariant.info'
        }

        # Loop through datasets to generate info
        datasets = {}

        for assembly, sources in self.meta.items():
            for source, meta in sources.items():
                version = meta['version']
                for dataset, count in meta['stats'].items():
                    dataset = dataset.rstrip('_hg19')
                    dataset = dataset.rstrip('_hg38')
                    if dataset in self.dataset_names:
                        if dataset in datasets:
                            datasets[dataset]['variantCount'] += count
                            datasets[dataset]['assemblyId'].append(assembly)
                        else:
                            datasets[dataset] = {
                                'id': dataset,
                                'version': version,
                                'variantCount': count,
                                'assemblyId': [assembly]
                            }

        out['datasets'] = list(datasets.values())

        # Return info
        self.finish(out)
