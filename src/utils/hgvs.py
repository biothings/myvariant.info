import re
import copy
import requests
from hashlib import blake2b


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


def _normalized_vcf(chr, pos, ref, alt):
    """If both ref/alt are > 1 base, and there are overlapping from the left,
       we need to trim off the overlapping bases.

       In the case that ref/alt is like this:
           CTTTT/CT    # with >1 overlapping bases from the left
       ref/alt should be normalized as TTTT/T, more examples:

            TC/TG --> C/G
       and pos should be fixed as well.
    """
    for i in range(max(len(ref), len(alt))):
        _ref = ref[i] if i < len(ref) else None
        _alt = alt[i] if i < len(alt) else None
        if _ref is None or _alt is None or _ref != _alt:
            break

    # _ref/_alt cannot be both None, if so,
    # ref and alt are exactly the same,
    # something is wrong with this VCF record
    assert not (_ref is None and _alt is None)

    _pos = int(pos)
    if _ref is None or _alt is None:
        # if either is None, del or ins types
        _pos = _pos + i - 1
        _ref = ref[i-1:]
        _alt = alt[i-1:]
    else:
        # both _ref/_alt are not None
        _pos = _pos + i
        _ref = ref[i:]
        _alt = alt[i:]

    return (chr, _pos, _ref, _alt)


def get_hgvs_from_vcf(chr, pos, ref, alt, mutant_type=None):
    '''get a valid hgvs name from VCF-style "chr, pos, ref, alt" data.'''
    if not (re.match('^[ACGTN]+$', ref) and re.match('^[ACGTN*]+$', alt)):
        raise ValueError("Cannot convert {} into HGVS id.".format((chr, pos, ref, alt)))
    if len(ref) == len(alt) == 1:
        # this is a SNP
        hgvs = 'chr{0}:g.{1}{2}>{3}'.format(chr, pos, ref, alt)
        var_type = 'snp'
    elif len(ref) > 1 and len(alt) == 1:
        # this is a deletion:
        if ref[0] == alt:
            start = int(pos) + 1
            end = int(pos) + len(ref) - 1
            if start == end:
                hgvs = 'chr{0}:g.{1}del'.format(chr, start)
            else:
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
        if ref[0] == alt[0]:
            # if ref and alt overlap from the left, trim them first
            _chr, _pos, _ref, _alt = _normalized_vcf(chr, pos, ref, alt)
            return get_hgvs_from_vcf(_chr, _pos, _ref, _alt, mutant_type=mutant_type)
        else:
            end = int(pos) + len(ref) - 1
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
    try:
        pos = int(pos)
    except ValueError:
        raise ValueError("Invalid position %s" % repr(pos))
    if not alt:
        raise ValueError("Cannot decide start/end from {}.".format((chr, pos, ref, alt)))
    if len(ref) == len(alt) == 1:
        # end is the same as start for snp
        start = end = pos
    elif len(ref) > 1 and len(alt) == 1:
        # this is a deletion:
        assert ref[0] == alt
        start = pos + 1
        end = pos + len(ref) - 1
        if start == end:
            end += 1    # end is start+1 for single nt deletion     
                        # TODO: double-check this is the right convention
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


def get_hgvs_from_rsid(doc_li, rsid_fn, dbsnp_col, skip_unmatched=False):
    """input doc_li is a list doc with rsid, rsid_fn is a function to return rsid from
       each doc. dbsnp_col is a mongo collection object for dbSNP data
       It will return a generator with the _id as the matching hgvs_id for a given rsid.
       if a rsid matches multiple hgvs ids, it will produce duplicated docs with each hgvs id.
       If rsid_fn returns None, then the original document is yielded
    """
    for doc in doc_li:
        rsid = rsid_fn(doc)
        if rsid is None:
            yield doc
        hits = [d for d in dbsnp_col.find({"dbsnp.rsid":rsid})]
        if hits:
            for hit in hits:
                hgvs_id = hit['_id']
                _doc = copy.copy(doc)
                _doc['_id'] = hgvs_id
                yield _doc
        elif skip_unmatched:
            yield doc

def trim_delseq_from_hgvs(hgvs, remove_ins=False):
    """Remove the deleted nucleotides from hgvs ID
    set remove_ins to be true during snpeff annotation to remove those
    long inserted nucleotides
    """
    re_delins = re.compile("(.*del)[A-Z]+(ins.*)")
    re_ins = re.compile("(.*ins)[A-Z]+$")
    re_del = re.compile("(.*del)[A-Z]+$")
    re_dup = re.compile("(.*dup)[A-Z]+$")
    if re_delins.match(hgvs):
        hgvs = "".join(re_delins.match(hgvs).groups())
    elif remove_ins and re_ins.match(hgvs):
        hgvs = "".join(re_ins.match(hgvs).groups())
    elif re_del.match(hgvs):
        hgvs = "".join(re_del.match(hgvs).groups())
    elif re_dup.match(hgvs):
        hgvs = "".join(re_dup.match(hgvs).groups())
    
    return hgvs

def encode_long_hgvs_id(doc,maxlen=512):
    assert "_id" in doc
    if len(doc["_id"]) > maxlen:
        prefix = trim_delseq_from_hgvs(doc["_id"],remove_ins=True)
        seq = doc["_id"].replace(prefix,"")
        seqshashed = blake2b(seq.encode(), digest_size=16).hexdigest()
        new_id = prefix + "_seqhashed_" + seqshashed
        doc["_id"] = new_id
        doc["_seqhashed"] = {seqshashed : seq}
    return doc

