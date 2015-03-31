import re


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


def get_hgvs_from_vcf(chr, pos, ref, alt):
    '''get a valid hgvs name from VCF-style "chr, pos, ref, alt" data.'''
    if len(ref) == len(alt) == 1:
        # this is a SNP
        hgvs = 'chr{0}:g.{1}{2}>{3}'.format(chr, pos, ref, alt)
    elif len(ref) > 1 and len(alt) == 1:
        # this is a deletion:
        assert ref[0] == alt
        start = pos + 1
        end = pos + len(ref) - 1
        hgvs = 'chr{0}:g.{1}_{2}del'.format(chr, start, end)
    elif len(ref) == 1 and len(alt) > 1:
        # this is a insertion
        assert alt[0] == ref
        hgvs = 'chr{0}:g.{1}_{2}ins'.format(chr, pos, pos + 1)
        ins_seq = alt[1:]
        hgvs += ins_seq
    else:
        raise ValueError("Cannot convert {} into HGVS id.".format((chr, pos, ref, alt)))
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
