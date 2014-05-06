import MySQLdb

# This script produces simple JSON from UCSC variant data
# Draws from the cosmicRaw database directly
# Sean D. Mooney

Meta = {
    "maintainer": "Sean Mooney",
    "requirements": [
        "MySQL-python>=1.2.5",
    ]
}


def loaddata():

    limit = 10000
    offset = 0

    MySQLHG19 = MySQLdb.connect('genome-mysql.cse.ucsc.edu', db='hg19', user='genomep', passwd='password')

    Cursor = MySQLHG19.cursor()

    while 1:
        Cursor = MySQLHG19.cursor()
        SQLLine = "SELECT * FROM cosmicRaw LIMIT %d OFFSET %d" % (limit, offset)
        Cursor.execute(SQLLine)

        offset += limit

        if Cursor.rowcount == 0:
            print "DONE"
            break

        print "%d" % offset

        while 1:
            snp = Cursor.fetchone()

            if not snp:
                break

            cosmicid = snp[1]
            chrom = snp[7]
            chromStart = int(snp[8])
            chromEnd = int(snp[9])
            tumor_site = snp[12]
            mut_nt = snp[10]
            mut_freq = snp[-1]

            mut_nt = mut_nt.upper()
            alleles = mut_nt.split('>')

            if len(alleles) < 2:
                continue

            allele1 = alleles[0]
            allele2 = alleles[1]

            if len(allele1) > 1 or len(allele2) > 1:
                continue

            HGVS = "%s:g.%d%s>%s" % (chrom, chromEnd, allele1, allele2)
            one_snp_json = {
                "chrom": chrom,
                "chromStart": chromStart,
                "chromEnd": chromEnd,
                "tumor_site": tumor_site,
                "cosmic_id": cosmicid,
                "mut_nt": mut_nt,
                "mut_freq": mut_freq,
                "allele1": allele1,
                "allele2": allele2,
                "_id": HGVS
            }
            yield one_snp_json

mapping = {}
