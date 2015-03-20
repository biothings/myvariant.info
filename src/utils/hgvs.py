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
    '''return a complementary version of hgvs_id. works only for SNP variant for now.'''
    pat = '(chr\w+:g\.\d+)(\w)\>(\w)'
    mat = re.match(pat, hgvs_id)
    if mat:
        g = mat.groups()
        return '{}{}>{}'.format(g[0],
                                reverse_complement_seq(g[1]),
                                reverse_complement_seq(g[2]))
    else:
        raise ValueError("Not a SNP variant")
