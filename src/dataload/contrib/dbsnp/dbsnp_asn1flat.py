"""
Parsing ASN1_flat format files from dbSNP

Currently no used for loading dbsnp data, using dbsnp_vcf_parser instead.

Chunlei Wu
"""
from __future__ import print_function
import re
import glob
import os.path

from utils.common import anyfile
from utils.dataload import rec_handler

assembly_d = {
    'GRCh38': 'hg38',
    'GRCh37': 'hg19'
}

loctype_d = {
    '1': 'insertion',
    '2': 'exact',
    '3': 'deletion',
    '4': 'range-insertion',
    '5': 'range-exact',
    '6': 'range-deletion'
}


class ParsingError(Exception):
    pass


class dbSNPASN1FlatParser:
    '''Parsing dbSNP ASN1_flat file.'''

    def __init__(self, verbose=True):
        self.verbose = verbose

    def parse(self, infile):
        print(os.path.split(infile)[1])
        cnt = 0
        err_d = {}
        _f = anyfile(infile)
        ff = rec_handler(_f)
        for rec in ff:
            if not rec.startswith('rs'):
                continue
            doc = self.parse_one_record(rec)
            if isinstance(doc, dict):
                cnt += 1
                yield doc
            else:
                if doc in err_d:
                    err_d[doc] += 1
                else:
                    err_d[doc] = 1
        print(cnt, err_d)

    def test(self, infile):
        _f = anyfile(infile)
        ff = rec_handler(_f)
        gd = []
        err_cnt = 0
        for rec in ff:
            if not rec.startswith('rs'):
                continue
            lines = rec.strip().split('\n')
            self._parse_rsline(lines)
            d = self._parse_GMAF(lines)
            if not d:
                err_cnt += 1
            gd.append(d)
        print(err_cnt)
        return gd

    def parse_one_record(self, record):
        snp_d = {}
        lines = record.strip().split('\n')
        snp_d.update(self._parse_rsline(lines) or {})
        snp_d.update(self._parse_SNP(lines) or {})
        snp_d.update(self._parse_VAL(lines) or {})
        snp_d.update(self._parse_GMAF(lines) or {})
        snp_d.update(self._parse_CTG(lines) or {})
        return snp_d

    def _parse_rsline(self, rec_lines):
        '''parsing RS line'''
        snp_d = {}
        rs_line = rec_lines[0].split(' | ')
        rsid = rs_line[0]
        self.current_rsid = rsid
        snp_d['rsid'] = rsid
        assert re.match('rs\d+', rsid)
        snp_d['snpclass'] = rs_line[3]
        snp_d['genotype'] = rs_line[4] == 'YES'
        return snp_d

    def _parse_SNP(self, rec_lines):
        '''Parsing SNP line from one ASN1_Flat record.'''
        snp_d = {}
        snp_line = [line for line in rec_lines if line.startswith('SNP')][0]
        snp_line = [x.split('=') for x in snp_line.split(' | ')]
        allele_li = snp_line[1][1].strip("'").split('/')
        if len(allele_li) == 2:
            allele1, allele2 = allele_li
            snp_d.update({
                'allele1': allele1,
                'allele2': allele2
            })
        else:
            # here we ignore those with > 2 alleles
            if self.verbose:
                print(self.current_rsid, snp_line[1][1])
            return    # -1

        if snp_line[2][1] != '?':
            het = float(snp_line[2][1])
            het_se = float(snp_line[3][1])
            snp_d['het'] = {
                'value': het,
                'se': het_se
            }
        if len(snp_line) == 5:
            allele_origin = snp_line[4][1]
            # pat = "(.+)\((.+)\)/(.+)\((.+)\)"
            # grp = re.match(pat, allele_orgin).groups()
            # assert len(grp) == 4
            pat = "(.*)\((.+)\)"
            d = []
            for x in allele_origin.split('/'):
                mat = re.match(pat, x)
                if mat:
                    d.append(mat.groups())
                else:
                    if self.verbose:
                        print(self.current_rsid, allele_origin)
                    return   # -2
            d = dict(d)
            if '' in d:
                d['-'] = d['']
                del d['']
            snp_d['allele_origin'] = d
        return snp_d

    def _parse_VAL(self, rec_lines):
        """parsing VAL line, should have one line in one record."""
        snp_d = {}
        val_line = [line for line in rec_lines if line.startswith('VAL')][0]
        k, v = val_line.split(' | ')[1].split('=')
        assert k == 'validated'
        assert (v == 'YES' or v == 'NO')
        snp_d['validated'] = v == 'YES'
        return snp_d

    def _parse_GMAF(self, rec_lines):
        '''GMAF line is optional, and can be multi-lines.'''
        snp_d = {}
        gmaf_lines = [line for line in rec_lines if line.startswith('GMAF')]
        if len(gmaf_lines) > 0:
            _gmaf = []
            for gmaf_line in gmaf_lines:
                gmaf_line = [x.split('=') for x in gmaf_line.split(' | ')]
                _gmaf.append({
                    "allele": gmaf_line[1][1],
                    "count": gmaf_line[2][1],
                    "freq": gmaf_line[3][1]
                })
            snp_d['gmaf'] = _gmaf
        return snp_d

    def _parse_CTG(self, rec_lines):
        '''parsing CTG lines, can have multiple lines'''
        snp_d = {}
        ctg_line = [line for line in rec_lines if line.startswith('CTG')]
        if ctg_line:
            ctg_line = ctg_line[0]
        else:
            if self.verbose:
                print(self.current_rsid, "missing CTG line")
            return    # -4
        ctg_line = [x.split('=') for x in ctg_line.split(' | ')]
        assembly_key = assembly_d[ctg_line[1][1].split('.')[0]]
        chrom = ctg_line[2][1]
        pos = ctg_line[3][1]
        if pos != '?':
            pos = int(pos)
        else:
            if self.verbose:
                print(self.current_rsid, 'pos=?')
            return   # -3
        pos_d = {
            assembly_key: {
                'start': pos,
                'end': pos + 1
            }
        }
        ctg_d = {
            'contig': {
                'accession': ctg_line[4][0],
                'start': int(ctg_line[5][1]),
                'end': int(ctg_line[6][1])
            }
        }
        loctype = loctype_d[ctg_line[7][1]]
        strand = ctg_line[8][1]
        snp_d.update(pos_d)
        snp_d.update(ctg_d)
        snp_d.update({
            'chrom': chrom,
            'strand': strand,
            'loctype': loctype
        })
        return snp_d


def load_data(path):
    parser = dbSNPASN1FlatParser()
    for fn in glob.glob(path):
        print(os.path.split(fn)[1])
        for doc in parser.parse(fn):
            yield doc
