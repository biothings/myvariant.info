'''
Parsing dbSNP VCF file into variant document

requires pyVCF module

Chunlei Wu
'''
from collections import OrderedDict
import copy
import time

from vcf import Reader

from utils.common import timesofar

# the key name for the pos in var_doc
POS_KEY = 'hg19'


def get_hgvs_name(record, as_list=False):
    """construct the valid HGVS name as the _id field"""
    _id_list = []
    _alt_list = []
    _pos_list = []

    chrom = record.CHROM
    for alt in record.ALT:
        alt = str(alt)
        _id = None
        if record.is_snp:
            assert record.POS == record.INFO['RSPOS']
            # make a HGVS id
            _id = 'chr{}:g.{}{}>{}'.format(chrom,
                                           record.POS,
                                           record.REF,
                                           alt)
            _alt_list.append(alt)
            _pos_list.append(OrderedDict(start=record.POS, end=record.POS + 1))   # end is start+1 for snp

        elif record.is_indel:
            if record.is_deletion:
                if len(record.ALT) == 1 and len(alt) == 1:
                    # only if ALT is a single allele, that is a simple deletion
                    assert alt == record.REF[0]
                    if record.POS + 1 == record.INFO['RSPOS']:
                        if len(record.REF) == 2:
                            # this is a single nt deletion
                            pos = record.INFO['RSPOS']
                            _pos_list.append(OrderedDict(start=pos, end=pos + 1))   # end is start+1 for single nt deletion
                        else:
                            # this is a multiple nt deletion
                            end = record.INFO['RSPOS'] + len(record.REF) - 2
                            pos = '{}_{}'.format(record.INFO['RSPOS'], end)
                            _pos_list.append(OrderedDict(start=record.INFO['RSPOS'], end=end))
                        _id = 'chr{}:g.{}del'.format(chrom, pos)
                        _alt_list.append(alt)
                    else:
                        # record.POS and RSPOS does not match
                        # something ambigious here
                        pass
                else:
                    # other cases of deletion currently been ignored
                    # e.g. rs369371434, rs386822484
                    pass
            else:
                # insertion
                if len(record.REF) == 1 and alt[0] == record.REF:
                    # simple insertion cases
                    if record.POS == record.INFO['RSPOS']:
                        pos = '{}_{}'.format(record.POS, record.POS + 1)
                        _id = 'chr{}:g.{}ins{}'.format(chrom, pos, alt[1:])
                        _alt_list.append(alt)
                        _pos_list.append(OrderedDict(start=record.POS, end=record.POS + 1))
                    else:
                        # record.POS and RSPOS does not match
                        # something ambigious here
                        pass
                else:
                    # other cases of insertion currently been ignored
                    # e.g. rs398121698, rs71320640
                    pass
        if _id:
            _id_list.append(_id)

    if not as_list and len(_id_list) == 1:
        _id_list = _id_list[0]
        _alt_list = _alt_list[0]
        _pos_list = _pos_list[0]

    return _id_list, _alt_list, _pos_list


def parse_one_rec(record):
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
    snp[POS_KEY] = _pos_list
    snp['_id'] = _id_list

    return snp


def parse_vcf(vcf_infile, compressed=True, verbose=True, by_id=True, **tabix_params):
    t0 = time.time()
    compressed == vcf_infile.endswith('.gz')
    vcf_r = Reader(filename=vcf_infile, compressed=compressed)
    vcf_r.fetch('1', 1)   # call a dummy fetch to initialize vcf_r._tabix
    if tabix_params:
        vcf_r.reader = vcf_r._tabix.fetch(**tabix_params)
    cnt_1, cnt_2, cnt_3 = 0, 0, 0
    for rec in vcf_r:
        doc = parse_one_rec(rec)
        if by_id:
            # one hgvs id, one doc
            if doc['_id']:
                if isinstance(doc['_id'], list):
                    for i, _id in enumerate(doc['_id']):
                        _doc = copy.copy(doc)
                        _doc['alt'] = doc['alt'][i]
                        _doc[POS_KEY] = doc[POS_KEY][i]
                        _doc['_id'] = _id
                        yield _doc
                        cnt_2 += 1
                        if verbose:
                            print(_doc['rsid'], '\t', _doc['_id'])

                else:
                    yield doc
                    cnt_2 += 1
                    if verbose:
                        print(doc['rsid'], '\t', doc['_id'])
            else:
                cnt_3 += 1
        else:
            # one rsid, one doc
            if doc['_id']:
                yield doc
                cnt_2 += 1
                if verbose:
                    print(doc['rsid'], '\t', doc['_id'])
            else:
                cnt_3 += 1
        cnt_1 += 1
    print("Done. [{}]".format(timesofar(t0)))
    print("Total rs: {}; total docs: {}; skipped rs: {}".format(cnt_1, cnt_2, cnt_3))
