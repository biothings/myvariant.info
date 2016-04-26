from www.helper import BaseHandler
from www.api.es import ESQuery


class WellderlyBeaconHandler(BaseHandler):
    esq = ESQuery()

    def get(self):
        chrom = self.get_argument('chrom', None)
        pos = self.get_argument('pos', None)
        allele = self.get_argument('allele', None)
        ref = self.get_argument('ref', None)

        if chrom and pos and allele:
            q = 'wellderly.chrom:"{}" AND wellderly.pos:{} AND wellderly.alt:{}'
            q = q.format(chrom, pos, allele)
            if ref:
                q += ' AND wellderly.ref:{}'.format(ref)
            res = self.esq.query(q, fields=None)
            if res and res.get('total') >= 1:
                # out = {'exist': True}
                out = 'YES'
            else:
                # out = {'exist': False}
                out = 'NO'
        else:
            # out = {'success': False, 'error': "Missing required parameters."}
            out = 'NULL'
        #self.return_json(out)
        self.write(out)


class WellderlyBeaconHandler_v2(BaseHandler):
    esq = ESQuery()
    
    def get(self):
        chrom = self.get_argument('chrom', None)
        pos = self.get_argument('pos', None)
        allele = self.get_argument('allele', None)
        assembly = self.get_argument('assembly', default='GRCh37')
                
        #Initialize Output
        out = {'exists':False, 'metadata':None}        

        # check if assembly is in GRCh37 or GRCh38
        if chrom and pos and allele and assembly in ['GRCh37', 'GRCh38']:
            q = 'wellderly.chrom:"{}" AND wellderly.pos:{} AND wellderly.alt:{}'
            q = q.format(chrom, pos, allele)
            res = self.esq.query(q)
            if res and res.get('total') > 0:
                out['exists'] = True
                out['metadata'] = [hit['wellderly'] for hit in res.get('hits')]
            
        self.return_json(out)
                

APP_LIST = [
    (r"/wellderly/?", WellderlyBeaconHandler),
    (r"/wellderly2/?", WellderlyBeaconHandler_v2),
]
