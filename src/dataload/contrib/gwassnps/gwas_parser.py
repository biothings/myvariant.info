from __future__ import print_function

try:
    import MySQLdb
except:
    pass
import requests

from utils.common import loadobj, is_float


def load_data(step=1000, offset=0, gwas_data_local=None):
    if gwas_data_local:
        gwas_data = loadobj('gwasdata.pyobj')
        for item in gwas_data:
            snp = item
            chrom = snp[1]
            chrom = chrom[3:]
            rsid = snp[4]
            pubMedID = snp[5]
            title = snp[9]
            trait = snp[10]
            region = snp[13]
            gene_name = snp[14]
            riskAllele = snp[15]
            riskAlleleFreq = snp[16]
            if not is_float(riskAlleleFreq):
                riskAlleleFreq = None
            pValue = snp[17]
            pValue_desc = snp[18]
            if not is_float(pValue):
                pValue = None
                pValue_desc = None
            # parse from myvariant.info to get hgvs_id,
            # ref, alt information based on rsid
            url = 'http://localhost:8000/v1/query?q=dbsnp.rsid:'\
                + rsid + '&fields=_id,dbsnp.ref,dbsnp.alt,dbsnp.chrom,dbsnp.hg19'
            r = requests.get(url)
            for hits in r.json()['hits']:
                HGVS = hits['_id']

                one_snp_json = {
                    "_id": HGVS,
                    "gwassnp":
                        {
                            "rsid": rsid,
                            "pubmed": pubMedID,
                            "title": title,
                            "trait": trait,
                            "region": region,
                            "genename": gene_name,
                            "risk_allele": riskAllele,
                            "risk_allele_freq": riskAlleleFreq,
                            "pvalue": pValue,
                            "pvalue_desc": pValue_desc
                        }
                }
                yield one_snp_json
    else:
        MySQLHG19 = MySQLdb.connect('genome-mysql.cse.ucsc.edu',
                                    db='hg19', user='genomep', passwd='password')
        Cursor = MySQLHG19.cursor()

        # get the row number of gwasCatalog
        sql = "SELECT COUNT(*) FROM gwasCatalog"
        Cursor.execute(sql)
        numrows = Cursor.fetchone()[0]
        print(numrows)

        sql = "SELECT * FROM gwasCatalog"
        Cursor.execute(sql)

        for i in range(numrows):
            snp = Cursor.fetchone()
            if i and i % step == 0:
                print(i)

            chrom = snp[1]
            chrom = chrom[3:]
            rsid = snp[4]
            pubMedID = snp[5]
            title = snp[9]
            trait = snp[10]
            region = snp[13]
            gene_name = snp[14]
            riskAllele = snp[15]
            riskAlleleFreq = snp[16]
            if not is_float(riskAlleleFreq):
                riskAlleleFreq = None
            pValue = snp[17]
            pValue_desc = snp[18]
            if not is_float(pValue):
                pValue = None
                pValue_desc = None
            # parse from myvariant.info to get hgvs_id, ref, alt information based on rsid
            url = 'http://localhost:8000/v1/query?q=dbsnp.rsid:'\
                + rsid + '&fields=_id,dbsnp.ref,dbsnp.alt,dbsnp.chrom,dbsnp.hg19'
            r = requests.get(url)
            for hits in r.json()['hits']:
                HGVS = hits['_id']
                one_snp_json = {
                    "_id": HGVS,
                    "gwassnp":
                        {
                            "rsid": rsid,
                            "pubmed": pubMedID,
                            "title": title,
                            "trait": trait,
                            "region": region,
                            "genename": gene_name,
                            "risk_allele": riskAllele,
                            "risk_allele_freq": riskAlleleFreq,
                            "pvalue": pValue,
                            "pvalue_desc": pValue_desc
                        }
                }
                yield one_snp_json
