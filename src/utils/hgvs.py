import re
import copy
import requests


def is_snp(hgvs_id):
    '''return True/False if a hgvs id a SNP or not.'''
    pat = 'chr(\w+):g\.(\d+)(\w)\>(\w)'
    mat = re.match(pat, hgvs_id)
    return mat is not None


def reverse_complement_seq(seq):
    seq_d = {
        "A": "T",
        "T": "A",
        "C": "G",
        "G": "C"
    }
    for k in seq_d.keys():
        seq_d[k.lower()] = seq_d[k].lower()
    return ''.join(seq_d[base] for base in reversed(seq))


def reverse_complement_hgvs(hgvs_id):
    '''return a complementary version of hgvs_id.
    works only for SNP, ins, delins variant for now.'''
    pat_snp = '(chr\w+:g\.\d+)(\w)\>(\w)'
    pat_ins = '(chr\w+:g\.\d+_\d+)ins(\w+)'
    pat_del_ins = '(chr\w+:g\.\d+_\d+)delins(\w+)'
    # complement SNP ID
    if re.match(pat_snp, hgvs_id):
        g = re.match(pat_snp, hgvs_id).groups()
        return '{}{}>{}'.format(g[0],
                                reverse_complement_seq(g[1]),
                                reverse_complement_seq(g[2]))
    # reverse complement ins ID
    elif re.match(pat_ins, hgvs_id):
        g = re.match(pat_ins, hgvs_id).groups()
        return '{}ins{}'.format(g[0],
                                reverse_complement_seq(g[1]))
    # reverse complement del_ins ID
    elif re.match(pat_del_ins, hgvs_id):
        g = re.match(pat_del_ins, hgvs_id).groups()
        return '{}delins{}'.format(g[0],
                                   reverse_complement_seq(g[1]))
    else:
        raise ValueError("Not a Valid HGVS ID")


def get_hgvs_from_vcf(chr, pos, ref, alt, mutant_type=None):
    '''get a valid hgvs name from VCF-style "chr, pos, ref, alt" data.'''
    if len(ref) == len(alt) == 1:
        # this is a SNP
        hgvs = 'chr{0}:g.{1}{2}>{3}'.format(chr, pos, ref, alt)
        var_type = 'snp'
    elif len(ref) > 1 and len(alt) == 1:
        # this is a deletion:
        if ref[0] == alt:
            start = int(pos) + 1
            end = int(pos) + len(ref) - 1
            hgvs = 'chr{0}:g.{1}_{2}del'.format(chr, start, end)
            var_type = 'del'
        else:
            end = int(pos) + len(ref) - 1
            hgvs = 'chr{0}:g.{1}_{2}delins{3}'.format(chr, pos, end, alt)
            var_type = 'delins'
    elif len(ref) == 1 and len(alt) > 1:
        # this is a insertion
        if alt[0] == ref:
            hgvs = 'chr{0}:g.{1}_{2}ins'.format(chr, pos, int(pos) + 1)
            ins_seq = alt[1:]
            hgvs += ins_seq
            var_type = 'ins'
        else:
            hgvs = 'chr{0}:g.{1}delins{2}'.format(chr, pos, alt)
            var_type = 'delins'
    elif len(ref) > 1 and len(alt) > 1:
        end = int(pos) + len(alt) - 1
        hgvs = 'chr{0}:g.{1}_{2}delins{3}'.format(chr, pos, end, alt)
        var_type = 'delins'
    else:
        raise ValueError("Cannot convert {} into HGVS id.".format((chr, pos, ref, alt)))
    if mutant_type:
        return hgvs, var_type
    else:
        return hgvs


def get_pos_start_end(chr, pos, ref, alt):
    '''get start,end tuple from VCF-style "chr, pos, ref, alt" data.'''
    if len(ref) == len(alt) == 1:
        # this is a SNP
        start = end = pos
    elif len(ref) > 1 and len(alt) == 1:
        # this is a deletion:
        assert ref[0] == alt
        start = pos + 1
        end = pos + len(ref) - 1
    elif len(ref) == 1 and len(alt) > 1:
        # this is a insertion
        assert alt[0] == ref
        start = pos
        end = pos + 1
    else:
        raise ValueError("Cannot decide start/end from {}.".format((chr, pos, ref, alt)))
    return start, end


def fix_hgvs_indel(hgvs_id):
    """Fix hgvs id like these:
         'chr19:g.58863869C>-',
         'chr10:g.52596077->T',
         'chr10:g.52596077->T',
         'chr12:g.8998751T>-',
         'chr12:g.9004916C>-',
    """
    _hgvs_id = None
    pat_snp = '(chr\w+:g\.(\d+))([\w-])\>([\w-])'
    if re.match(pat_snp, hgvs_id):
        g = re.match(pat_snp, hgvs_id).groups()
        pos, ref, alt = g[1:]
        if ref == '-':
            # should be insertion
            _hgvs_id = '{}ins{}'.format(g[0], alt)
        elif alt == '-':
            # should be deletion
            end = int(pos) + len(ref) - 1
            _hgvs_id = '{0}_{1}del'.format(g[0], end)
        else:
            print("Error: either cannot fix or no need to fix: ", hgvs_id)
    else:
        print("Error: hgvs id not in a fixable format: ", hgvs_id)
    return _hgvs_id


def get_hgvs_from_rsid(doc_li, rsid_fn, api_host='http://localhost:8000'):
    """input doc_li is a list doc with rsid, rsid_fn is a function to return rsid from
       each doc.
       It will return a generator with the _id as the matching hgvs_id for a given rsid.
       if a rsid matches multiple hgvs ids, it will produce duplicated docs with each hgvs id.
    """
    for doc in doc_li:
        rsid = rsid_fn(doc)
        # parse from myvariant.info to get hgvs_id, ref, alt information based on rsid
        url = api_host + '/v1/query?q=dbsnp.rsid:' + rsid +\
            '&fields=_id,dbsnp.ref,dbsnp.alt,dbsnp.chrom,dbsnp.hg19'
        r = requests.get(url)
        for hits in r.json()['hits']:
            hgvs_id = hits['_id']
            _doc = copy.copy(doc)
            _doc['_id'] = hgvs_id
            yield _doc
