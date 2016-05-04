from www.helper import BaseHandler
from www.api.es import ESQuery
import json

class BeaconHandler(BaseHandler):
    esq = ESQuery()
    """
    def post(self, src = None):
        data = json.loads(self.request.body.decode('utf-8'))

        chrom = data['genome.chrom']
        pos = data['genome.position']
        allele = data['genome.allele']
        assembly = data['genome.assembly']

        out = self.get_output(chrom, pos, allele, assembly, src)

        #Return the JSON response
        self.return_json(out)
    """
    def post(self, src = None):

        chrom = self.get_argument('genome.chrom', None)
        pos = self.get_argument('genome.position', None)
        allele = self.get_argument('genome.allele', None)
        assembly = self.get_argument('genome.assembly', default='GRCh37')

        out = self.get_output(chrom, pos, allele, assembly, src)

        #Return the JSON response
        self.return_json(out)


    def get(self, src=None):
       
        chrom = self.get_argument('chrom', None)
        pos = self.get_argument('pos', None)
        allele = self.get_argument('allele', None)
        assembly = self.get_argument('assembly', default='GRCh37')

        out = self.get_output(chrom, pos, allele, assembly, src)

        #Return the JSON response
        self.return_json(out)


    def get_output(self, chrom, pos, allele, assembly, src):             
        #Initialize Sources and Output
        pos_dbs = ['wellderly', 'exac', 'cadd'] #cadd not working (no alt)
        hg19_dbs = ['dbnsfp','dbsnp','clinvar','evs','mutdb','cosmic','docm']
        out = {'exists':False} 

        # check if enough infomation and assembly is correct and format query
        if chrom and pos and allele and assembly in ['GRCh37', 'GRCh38']:
            q = ''
            if src in pos_dbs+hg19_dbs:
                q += src + '.chrom:"{}" AND '
                if src in pos_dbs:
                    q += src + '.pos:{} AND '
                elif src in hg19_dbs:
                    q += src + '.hg19.start:{} AND '
                q += src + '.alt:{}'
            else:
                q = 'chr{}:{}'
            q = q.format(chrom, pos, allele)

            # perform query and format result
            res = self.esq.query(q)
            if res and res.get('total') > 0:
                if src in pos_dbs+hg19_dbs:
                    out = self.format_output_src(res, src, out)
                else:
                    out = self.verify_hits(res.get('hits'), out, allele)
        return(out)


    def format_output_src(self, res, src, out):
        out['exists'] = True
        if len(res.get('hits')) == 1:
            out['metadata'] = res.get('hits')[0][src]
        else:
            out['metadata'] = [hit[src] for hit in res.get('hits')]
        return out


    # TODO Enventually incorparte this logic into the search itself
    def verify_hits(self, hits, out, allele):
        for hit in hits:
            for key in hit.keys():
                if not key.startswith('_') and isinstance(hit[key], dict) and 'alt' in hit[key].keys():
                    if hit[key]['alt'] == allele:
                        out['exists'] = True
                        out['metadata'] = {k:hit[k] for k in hit.keys() if not k.startswith('_')}
                        return out
        return out


APP_LIST = [
    (r"/?", BeaconHandler),
    (r"/(.+)/?", BeaconHandler),
]
