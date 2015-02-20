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
            q = 'wellderly.chr:{} AND wellderly.pos:{} AND wellderly.alt:{}'
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


APP_LIST = [
    (r"/wellderly/?", WellderlyBeaconHandler),
]
