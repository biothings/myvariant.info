from __future__ import print_function
import time
import pysam
from itertools import groupby
try:
    import itertools.imap as map
except ImportError:
    pass
from utils.dataload import dict_sweep, unlist, value_convert, merge_duplicate_rows
from utils.common import timesofar
from utils.mongo import get_src_db
from utils.hgvs import get_hgvs_from_vcf
# tabix file links from CADD http://cadd.gs.washington.edu/download
# whole genome SNVs including annotations
whole_genome = 'http://krishna.gs.washington.edu/download/CADD/v1.2/whole_genome_SNVs_inclAnno.tsv.gz'
# SNV variants on Illumina Exome BeadChip
exome = '/opt/myvariant.info/load_archive/cadd/HumanExome-12v1-1_A_inclAnno.tsv.gz'
# 1000 Genomes variants SNVs and InDels including all annotations
thousandgp = '/opt/myvariant.info/load_archive/cadd/1000G_inclAnno.tsv.gz'
# Exome Aggreation Consortium variants including all annotations
exac = 'opt/myvariant.info/load_archive/cadd/ExAC.r0.2_inclAnno.tsv.gz'
# ESP6500 variants SNVs and InDels including all annotations
esp = 'opt/myvariant.info/load_archive/cadd/ESP6500SI_inclAnno.tsv.gz'

# number of fields/annotations
VALID_COLUMN_NO = 116


# convert one snp to json
def _map_line_to_json(fields):
    assert len(fields) == VALID_COLUMN_NO
    chrom = fields[0]
    chromStart = fields[1]
    ref = fields[2]
    alt = fields[4]
    HGVS = get_hgvs_from_vcf(chrom, chromStart, ref, alt)

    # load as json data
    if HGVS is None:
        return
    one_snp_json = {
        "_id": HGVS,
        "cadd": {
            'chrom': fields[0],
            'pos': fields[1],
            'ref': fields[2],
            'anc': fields[3],
            'alt': fields[4],
            'type': fields[5],
            'length': fields[6],
            'istv': fields[7],
            'isderived': fields[8],
            'annotype': fields[9],
            'consequence': fields[10],
            'consscore': fields[11],
            'consdetail': fields[12],
            'gc': fields[13],
            'cpg': fields[14],
            'mapability': {
                '20bp': fields[15],
                '35bp': fields[16]
            },
            'scoresegdup': fields[17],
            'phast_cons': {
                'primate': fields[18],
                'mammalian': fields[19],
                'vertebrate': fields[20]
            },
            'phylop': {
                'primate': fields[21],
                'mammalian': fields[22],
                'vertebrate': fields[23]
            },
            'gerp': {
                'n': fields[24],
                's': fields[25],
                'rs': fields[26],
                'rs_pval': fields[27]
            },
            'bstatistic': fields[28],
            'mutindex': fields[29],
            'dna': {
                'helt': fields[30],
                'mgw': fields[31],
                'prot': fields[32],
                'roll': fields[33]
            },
            'mirsvr': {
                'score': fields[34],
                'e': fields[35],
                'aln': fields[36]
            },
            'targetscans': fields[37],
            'fitcons': fields[38],
            'chmm': {
                'tssa': fields[39],
                'tssaflnk': fields[40],
                'txflnk': fields[41],
                'tx': fields[42],
                'txwk': fields[43],
                'enh': fields[44],
                # 'enh': fields[45],
                'znfrpts': fields[46],
                'het': fields[47],
                'tssbiv': fields[48],
                'bivflnk': fields[49],
                'enhbiv': fields[50],
                'reprpc': fields[51],
                'reprpcwk': fields[52],
                'quies': fields[53],
            },
            'encode': {
                'exp': fields[54],
                'h3k27ac': fields[55],
                'h3k4me1': fields[56],
                'h3k4me3': fields[57],
                'nucleo': fields[58],
                'occ': fields[59],
                'p_val': {
                    'comb': fields[60],
                    'dnas': fields[61],
                    'faire': fields[62],
                    'polii': fields[63],
                    'ctcf': fields[64],
                    'mycp': fields[65]
                },
                'sig': {
                    'dnase': fields[66],
                    'faire': fields[67],
                    'polii': fields[68],
                    'ctcf': fields[69],
                    'myc': fields[70]
                },
            },
            'segway': fields[71],
            'motif': {
                'toverlap': fields[72],
                'dist': fields[73],
                'ecount': fields[74],
                'ename': fields[75],
                'ehipos': fields[76],
                'escorechng': fields[77]
            },
            'tf': {
                'bs': fields[78],
                'bs_peaks': fields[79],
                'bs_peaks_max': fields[80]
            },
            'isknownvariant': fields[81],
            'esp': {
                'af': fields[82],
                'afr': fields[83],
                'eur': fields[84]
            },
            '1000g': {
                'af': fields[85],
                'asn': fields[86],
                'amr': fields[87],
                'afr': fields[88],
                'eur': fields[89]
            },
            'min_dist_tss': fields[90],
            'min_dist_tse': fields[91],
            'gene': {
                'gene_id': fields[92],
                'feature_id': fields[93],
                'ccds_id': fields[94],
                'genename': fields[95],
                'cds': {
                    'cdna_pos': fields[96],
                    'rel_cdna_pos': fields[97],
                    'cds_pos': fields[98],
                    'rel_cds_pos': fields[99]
                },
                'prot': {
                    'protpos': fields[100],
                    'rel_prot_pos': fields[101],
                    'domain': fields[102]
                }
            },
            'dst2splice': fields[103],
            'dst2spltype': fields[104],
            'exon': fields[105],
            'intron': fields[106],
            'oaa': fields[107],   # ref aa
            'naa': fields[108],   # alt aa
            'grantham': fields[109],
            'polyphen': {
                'cat': fields[110],
                'val': fields[111]
            },
            'sift': {
                'cat': fields[112],
                'val': fields[113]
            },
            'rawscore': fields[114],    # raw CADD score
            'phred': fields[115]        # log-percentile of raw CADD score
        }
    }

    return dict_sweep(unlist(value_convert(one_snp_json)), ["NA"])


def fetch_generator(tabix, contig):
    fetch = tabix.fetch(contig)
    rows = map(lambda x: x.split('\t'), fetch)
    annos = (row for row in rows if "CodingTranscript" in row[9])
    json_rows = map(_map_line_to_json, annos)
    json_rows = (row for row in json_rows if row)
    row_groups = (it for (key, it) in groupby(json_rows, lambda row: row["_id"]))
    return (merge_duplicate_rows(rg, "cadd") for rg in row_groups)


def load_contig(contig):
    '''save cadd contig into mongodb collection.
       should be an iterable.
    '''
    # if CADD_INPUT == "exome":
    # CADD_INPUT = exome
    tabix = pysam.Tabixfile(whole_genome)
    src_db = get_src_db()
    target_coll = src_db["cadd"]
    t0 = time.time()
    cnt = 0
    docs = (doc for doc in fetch_generator(tabix, contig))
    doc_list = []
    for doc in docs:
        doc_list.append(doc)
        cnt += 1
        if len(doc_list) == 100:
            target_coll.insert(doc_list, manipulate=False, check_keys=False, w=0)
            doc_list = []
        if cnt % 100000 == 0:
            print(cnt, timesofar(t0))
    if doc_list:
        target_coll.insert(doc_list, manipulate=False, check_keys=False, w=0)
    print("successfully loaded cadd chromosome %s into mongodb" % contig)
    print("total docs: {}; total time: {}".format(cnt, timesofar(t0)))
