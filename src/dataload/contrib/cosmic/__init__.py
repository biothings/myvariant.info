from __future__ import print_function
try:
    import MySQLdb
except:
    pass


__METADATA__ = {
    "requirements": [
        "MySQL-python>=1.2.5",
    ],
    "src_name": 'COSMIC',
    "src_url": 'http://cancer.sanger.ac.uk/cosmic',
    "version": '68',
    "field": "cosmic"

}


def load_data(step=1000, offset=0):

    MySQLHG19 = MySQLdb.connect('genome-mysql.cse.ucsc.edu', db='hg19', user='genomep', passwd='password')

    cursor = MySQLHG19.cursor()

    # while 1:
    #     Cursor = MySQLHG19.cursor()
    #     SQLLine = "SELECT * FROM cosmicRaw LIMIT %d OFFSET %d" % (limit, offset)
    #     Cursor.execute(SQLLine)

    #     offset += limit

    #     if Cursor.rowcount == 0:
    #         print "DONE"
    #         break

    #     print "%d" % offset

    #     while 1:
    #         snp = Cursor.fetchone()

    #         if not snp:
    #             break

    sql = "SELECT COUNT(*) FROM cosmicRaw"
    cursor.execute(sql)
    numrows = cursor.fetchone()[0]
    print(numrows)

    sql = "SELECT * FROM cosmicRaw"
    cursor.execute(sql)

    for i in range(numrows):
        snp = cursor.fetchone()
        if i and i % step == 0:
            print(i)

        cosmicid = snp[1]
        chrom = snp[7]
        if chrom == '23':
            chrom = 'X'
        elif chrom == '24':
            chrom = 'Y'
        elif chrom == '25':
            chrom = 'MT'

        chromStart = int(snp[8])
        chromEnd = int(snp[9])
        tumor_site = snp[12]
        mut_nt = snp[10]
        mut_freq = float(snp[-1])

        mut_nt = mut_nt.upper()
        alleles = mut_nt.split('>')

        if len(alleles) < 2:
            continue

        allele1 = alleles[0]
        allele2 = alleles[1]

        if len(allele1) > 1 or len(allele2) > 1:
            continue

        HGVS = "chr%s:g.%d%s>%s" % (chrom, chromEnd, allele1, allele2)
        one_snp_json = {
            "_id": HGVS,
            "cosmic": {
                "chrom": chrom,
                "hg19": {
                    "start": chromStart,
                    "end": chromEnd
                },
                "tumor_site": tumor_site,
                "cosmic_id": cosmicid,
                "mut_nt": mut_nt,
                "mut_freq": mut_freq,
                "ref": allele1,
                "alt": allele2
            }
        }
        yield one_snp_json


def get_mapping():
    mapping = {
        "cosmic": {
            "properties": {
                "chrom": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "hg19": {
                    "properties": {
                        "start": {
                            "type": "long"
                        },
                        "end": {
                            "type": "long"
                        }
                    }
                },
                "tumor_site": {
                    "type": "string"
                },
                "cosmic_id": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "mut_nt": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "mut_freq": {
                    "type": "float"
                },
                "ref": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "alt": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                }
            }
        }
    }
    return mapping
