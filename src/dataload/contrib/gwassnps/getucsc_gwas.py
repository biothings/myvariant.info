import os, sys, string, json, gc
import MySQLdb

#This script produces simple JSON from UCSC gwasCatalog table variant data
#Draws from the gwasCatalog
#Sean D. Mooney

limit = 100000
offset = 0

MySQLHG19 = MySQLdb.connect('genome-mysql.cse.ucsc.edu', db='hg19', user='genomep', passwd='password')
Cursor = MySQLHG19.cursor()

#First collect dbSNP

dbSNPdict = {}

while 1:
    Cursor = MySQLHG19.cursor()
    SQLLine = "SELECT * FROM gwasCatalog LIMIT %d OFFSET %d" % (limit, offset)
    Cursor.execute(SQLLine)

    offset += limit

    if Cursor.rowcount == 0:
        sys.stderr.write("DONE")
        break

    sys.stderr.write("%d\n" %(offset))
    sys.stderr.flush()

    while 1:
        snp = Cursor.fetchone()

        sys.stdout.flush()

        if not snp:
            break

        chrom = snp[1]
        chrom = chrom[3:]
        chromStart = int(snp[2])
        chromEnd = int(snp[3])
        rsid = snp[4]
        pubMedID = snp[5]
        trait = snp[9]
        riskAllele = snp[14]
        pValue = snp[16]

        # try:
        Cursor2 = MySQLHG19.cursor()
        SQLLine = "SELECT observed FROM snp138 WHERE name = '%s'" % (rsid)
        Cursor2.execute(SQLLine)
        if Cursor2.rowcount == 0:
            continue
        observed = Cursor2.fetchone()
        observed = observed[0]
        observed = observed.split('/')
        allele1 = observed[0]
        allele2 = observed[1]

        HGVS = "%s:g.%d%s>%s" % (chrom, chromEnd, allele1, allele2)
        dbSNPdict[HGVS] = {"rsid": rsid, "chrom": chrom, "chromStart": chromStart, "chromEnd": chromEnd, "allele1": allele1, "allele2": allele2, "pubmedID": pubMedID, "trait": trait, "_id": HGVS}
        # except:
        #    continue
        pass

    snp_json = json.dumps(dbSNPdict)
    print snp_json
    dbSNPdict = {}

    gc.collect()

    pass
