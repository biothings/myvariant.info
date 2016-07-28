import sys
from biothings.www.helper import BaseHandler
from www.api.es import ESQuery


class BeaconHandler(BaseHandler):
    esq = ESQuery()
    # Initialize Assembly and Datasets
    assembly_keys = {'NCBI36':'hg18', 'GRCh37':'hg19', 'GRCh38':'hg38'}
    pos_dbs = ['exac', 'cadd'] # These are hg19 ONLY
    assembly_dbs = ['dbnsfp','dbsnp','clinvar','evs','mutdb','cosmic','docm','wellderly']

    def post(self, src=None):
        self.recieve_data()

    def get(self, src=None):
        self.recieve_data()

    def recieve_data(self):
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
                    length = alt[3:]
                    q = self.del_dup_query(chrom, start, length, assembly, dataset)
                    q_type = 'del'
                elif alt[:3] == 'DUP': # "alternateBases": "DUP85689"
                    length = alt[3:]
                    q = self.del_dup_query(chrom, start, length, assembly, dataset)
                    q_type = 'dup'
                elif ref and alt:
                    q = self.snp_query(chrom, start, ref, alt, assembly, dataset)

                # perform query and format result
                res = self.esq.query(q, fields=dataset, dotfield=1)
                if res and res.get('total') > 0:
                    out = self.format_output(res, out, q_type)
        return out


    def snp_query(self, chrom, start, ref, alt, assembly, dataset):
        q = dataset + '.chrom:"{}" AND '.format(chrom)
        if dataset in self.pos_dbs and assembly == 'hg19':
            q += dataset + '.pos:{} AND '.format(start)
        elif dataset in self.assembly_dbs:
            q += dataset + '.{}.start:{} AND '.format(assembly, start)
        else:
            return ''
        q += dataset + '.ref:{} AND '.format(ref)
        q += dataset + '.alt:{} AND '.format(alt)
        q += '_exists_:{}'.format(dataset)

        return q

    # Querying for deletions and duplcations can be done with same syntax
    # issue then comes in resolving is this query a deletion or a duplication
    # can just perform the query and test afterward
    def del_dup_query(self, chrom, start, length, assembly, dataset):
        end = int(start)+int(length)-1
        q = dataset + '.chrom:"{}" AND '.format(chrom)
        if dataset in self.pos_dbs and assembly == 'hg19':
            q += 'hg19.start:{} AND '.format(start)
            q += 'hg19.end:{} AND '.format(end)
        elif dataset in self.assembly_dbs:
            q += dataset + '.{}.start:{} AND '.format(assembly, start)
            q += dataset + '.{}.end:{} AND '.format(assembly, end)
        else:
            return ''
        q += '_exists_:{}'.format(dataset)

        print(chrom, start, length, str(end), assembly, dataset, q)

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
