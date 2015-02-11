from www.helper import BaseHandler
from www.api.es import ESQuery


class WellderlyBeaconHandler(BaseHandler):
    esq = ESQuery()

    def get(self):
        chr = self.get_argument('chr', None)
        pos = self.get_argument('pos', None)
        allele = self.get_argument('allele', None)

        if chr and pos and allele:
            q = 'wellderly.chr:{} AND wellderly.pos:{} AND wellderly.alt:{}'
            q = q.format(chr, pos, allele)
            res = self.esq.query(q, fields=None)
            if res and res.get('total') >= 1:
                out = {'exist': True}
            else:
                out = {'exist': False}
        else:
            out = {'success': False, 'error': "Missing required parameters."}
        self.return_json(out)


APP_LIST = [
    (r"/wellderly/?", WellderlyBeaconHandler),
]
