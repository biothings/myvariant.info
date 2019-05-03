'''
Parsing dbSNP VCF file into variant document

requires pyVCF module

Chunlei Wu
'''
from collections import OrderedDict
import copy, os
import time
import glob

from vcf import Reader

from biothings.utils.common import timesofar
from utils.hgvs import get_hgvs_from_vcf, get_pos_start_end
from biothings.utils.dataload import dict_sweep, unlist, value_convert_to_number
#from config import logger as logging
import logging


def get_hgvs_name(record, as_list=False):
    """construct the valid HGVS name as the _id field"""
    chrom = record.CHROM
    chromStart = record.POS
    ref = record.REF
    _alt_list = []

    _id_list = []
    _pos_list = []
    for alt in record.ALT:
        if alt:
            alt = str(alt)
        _alt_list.append(alt)
        try:
            # NOTE: current get_pos_start_end doesn't handle ALT=None case
            # TODO: need to remove str(alt) when get_pos_start_end can
            # handle ALT=None case
            (start, end) = get_pos_start_end(chrom, chromStart, ref, alt)
            _pos_list.append(OrderedDict(start=start, end=end))
        # handle cases where start & end position could not be
        # inferred from VCF
        except ValueError:
            _pos_list.append(OrderedDict(start=None, end=None))
        try:
            HGVS = get_hgvs_from_vcf(chrom,
                                     chromStart,
                                     ref,
                                     alt,
                                     mutant_type=False)
            _id_list.append(HGVS)
        # handle cases where hgvs id could not be inferred from vcf
        except ValueError:
            pass
    return _id_list, _alt_list, _pos_list


def parse_one_rec(assembly, record):
    snp = OrderedDict()
    snp['rsid'] = record.ID
    snp['vartype'] = record.var_type
    snp['var_subtype'] = record.var_subtype

    info = record.INFO
    snp['dbsnp_build'] = info['dbSNPBuildID']
    if 'GENEINFO' in info:
        snp['gene'] = [dict(zip(('symbol', 'geneid'), x.split(':'))) for x in info['GENEINFO'].split('|')]
        if len(snp['gene']) == 1:
            snp['gene'] = snp['gene'][0]
    if 'SAO' in info:
        _d = {
            0: 'unspecified',
            1: 'germline',
            2: 'somatic',
            3: 'both'
        }
        snp['allele_origin'] = _d[info['SAO']]
    if 'VC' in info:
        # ref http://www.ncbi.nlm.nih.gov/projects/SNP/snp_legend.cgi?legend=snpClass
        snp['class'] = info['VC']
    snp['validated'] = info.get('VLD', None) is True
    # flags
    flags_included = [
        # reverse
        'RV',
        # functional
        'PM', 'TPA', 'PMC', 'S3D', 'SLO', 'NSF', 'NSM', 'NSN', 'REF', 'SYN',
        'U3', 'U5', 'ASS', 'DSS', 'INT', 'R3', 'R5', 'MUT', 'CDA', 'MTP', 'OM'
        # mapping:
        'OTH', 'CFL', 'ASP', 'LSD', 'NOC', 'WTD', 'NOV',
        # freqs:
        'G5A', 'G5', 'HD', 'GNO', 'KGPhase1', 'KGPhase3'
    ]
    flags = [f for f in flags_included if info.get(f, False)]
    if flags:
        snp['flags'] = sorted(flags)

    # CAF and alleles
    snp['alleles'] = [{"allele": str(a)} for a in record.alleles]
    if 'CAF' in info:
        assert len(info['CAF']) == len(snp['alleles'])
        for i, freq in enumerate(info['CAF']):
            if freq:
                snp['alleles'][i]['freq'] = float(freq)
        # GMAF: The minor allele is the second largest value in the list,
        # and was previuosly reported in VCF as the GMAF.
        # This is the GMAF reported on the RefSNP and EntrezSNP pages and
        # VariationReporter
        freq_list = [float(x) for x in info['CAF'] if x]
        if len(freq_list) >= 2:
            snp['gmaf'] = freq_list[1]

    # INFO field skipped: SSR, COMMON

    snp['chrom'] = record.CHROM
    snp['ref'] = record.REF
    _id_list, _alt_list, _pos_list = get_hgvs_name(record)
    snp['alt'] = _alt_list
    snp[assembly] = _pos_list
    snp['_id'] = _id_list

    return snp


def parse_vcf(assembly, vcf_infile, compressed=True, verbose=True, by_id=True, **tabix_params):
    t0 = time.time()
    compressed == vcf_infile.endswith('.gz')
    vcf_r = Reader(filename=vcf_infile, compressed=compressed)
    vcf_r.fetch('1', 1)   # call a dummy fetch to initialize vcf_r._tabix
    if tabix_params:
        vcf_r.reader = vcf_r._tabix.fetch(**tabix_params)
    cnt_1, cnt_2, cnt_3 = 0, 0, 0
    for rec in vcf_r:
        doc = parse_one_rec(assembly, rec)
        if by_id:
            # one hgvs id, one doc
            if doc['_id']:
                if isinstance(doc['_id'], list):
                    for i, _id in enumerate(doc['_id']):
                        _doc = copy.copy(doc)
                        _doc['alt'] = doc['alt'][i]
                        _doc[assembly] = doc[assembly][i]
                        _doc['_id'] = _id
                        yield _doc
                        cnt_2 += 1
                        if verbose:
                            logging.info("%s\t%s" % (_doc['rsid'], _doc['_id']))

                else:
                    yield doc
                    cnt_2 += 1
                    if verbose:
                        logging.info("%s\t%s" % (doc['rsid'], doc['_id']))
            else:
                cnt_3 += 1
        else:
            # one rsid, one doc
            if doc['_id']:
                yield doc
                cnt_2 += 1
                if verbose:
                    logging.info("%s\t%s" % (doc['rsid'], doc['_id']))
            else:
                cnt_3 += 1
        cnt_1 += 1
    logging.info("Done. [{}]".format(timesofar(t0)))
    logging.info("Total rs: {}; total docs: {}; skipped rs: {}".format(cnt_1, cnt_2, cnt_3))


def load_data(assembly, input_file, chrom):
    import logging as loggingmod
    global logging
    logging = loggingmod.getLogger("dbsnp_upload")
    logging.info("Processing chr{}...".format(chrom))
    snpdoc_iter = parse_vcf(assembly, input_file, compressed=True, verbose=False, by_id=True, reference=chrom)
    for doc in snpdoc_iter:
        _doc = {'dbsnp': doc}
        _doc['_id'] = doc['_id']
        del doc['_id']
        yield (dict_sweep(unlist(value_convert_to_number(_doc)),
                                                         [None]))

