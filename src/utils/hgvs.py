import re
import copy
from hashlib import blake2b

"""
Some of the HGVS related functions dated back to 2015, and the recommendations changed a lot nowadays.
The legacy recommendations can be found at https://www.hgvs.org/mutnomen/.
At the time of writing this comment, the latest recommendations are http://varnomen.hgvs.org/.

(We only focus on the "DNA-level" recommendations in this module.)
"""


class HGVSHelper:
    """
    A helper class that collects all the global variables used for HGVS functionality in this module
    """

    _SINGLE_POSITION_PATTERN = 'chr\w+:g\.\d+'
    _DOUBLE_POSITION_PATTERN = 'chr\w+:g\.\d+_\d+'

    """
    Modern (at the time of writing) HGVS formats in our application, 
    as described in http://varnomen.hgvs.org/recommendations/DNA/
    """
    # chr<i>:g.<pos><ref>&gt;<alt>, e.g. chrX:g.123A>G
    SNP_PATTERN = re.compile(f'({_SINGLE_POSITION_PATTERN})(\w)>(\w)')
    # chr<i>:g.<start>_<end>ins<seq>, e.g. chrX:g.123_124insAGC
    INS_PATTERN = re.compile(f'({_DOUBLE_POSITION_PATTERN})ins(\w+)')
    # chr<i>:g.<start>_<end>delins<seq>, e.g. chrX:g.123_127delinsAG
    DELINS_PATTERN = re.compile(f'({_DOUBLE_POSITION_PATTERN})delins(\w+)')
    # chr<i>:g.<start>_<end>del, e.g. chrX:g.123_127del
    # DEL_PATTERN = re.compile(f'({_DOUBLE_POSITION_PATTERN})del')
    # chr<i>:g.<start>_<end>dup, e.g. chrX:g.123_345dup
    # DUP_PATTERN = re.compile(f'({_DOUBLE_POSITION_PATTERN})'dup')

    # UNIQUE REPEAT => chr<i>:g.<pos>_<seq>[<num>], e.g. chrX:g.123CAG[23]
    # MIXED REPEAT  => chr<i>:g.<start>_<end><seq1>[<num1>]<seq2>[<num2>]..., e.g. chrX:g.123_191CAG[19]CAA[4]
    # A stem of a repeated sequence can be either "chr<i>:g.<pos>" or "chr<i>:g.<start>_<end>"
    # This stem pattern is so general that it SHOULD only be used when the HGVS is a repeated sequence.
    REP_SEQ_STEM_PATTERN = re.compile("chr\w+:g\.\d+(_\d+)?")
    INS_STEM_PATTERN = re.compile(_DOUBLE_POSITION_PATTERN + 'ins')
    DELINS_STEM_PATTERN = re.compile(_DOUBLE_POSITION_PATTERN + 'delins')

    """
    To match hgvs IDs like: 'chr19:g.58863869C>-', 'chr10:g.52596077->T'
    Such indels can be converted to insertions or deletions.
    This format must be legacy and I cannot find any document on it.
    """
    LEGACY_MINUS_SIGN_PATTERN = re.compile('(chr\w+:g\.(\d+))([\w-])>([\w-])')
    """
    Patterns for pruning legacy HGVS. E.g.:
    
        c.76_78delACT => c.76_78del
        c.77_79dupCTG => c.77_79dup
        c.112_117delAGGTCAinsTG => c.112_117delinsTG
        
    The above examples are from https://www.hgvs.org/mutnomen/recs-DNA.html#DNA
    """
    LEGACY_DELINS_REDUNDANT_SEQ_PATTERN = re.compile("(.*del)[A-Z]+(ins.*)")
    LEGACY_DEL_REDUNDANT_SEQ_PATTERN = re.compile("(.*del)[A-Z]+$")
    LEGACY_DUP_REDUNDANT_SEQ_PATTERN = re.compile("(.*dup)[A-Z]+$")


class SeqHelper:
    """
    A helper class that collects all the global variables used for nucleotide functionality in this module
    """

    COMPLEMENT_MAP = {
        "A": "T",
        "T": "A",
        "C": "G",
        "G": "C"
    }
    SEQ_PATTERN = re.compile('^[ACGTN]+$')


def is_snp(hgvs: str):
    """return True/False if an hgvs id a SNP or not."""
    return HGVSHelper.SNP_PATTERN.match(hgvs) is not None


def reverse_complement_seq(seq: str):
    return ''.join(SeqHelper.COMPLEMENT_MAP[base] for base in reversed(seq))


def reverse_complement_hgvs(hgvs: str):
    # TODO this function is never used and costs time to write tests for it. Can we delete it?
    """
    Return a complementary version of hgvs.
    Works only for SNP, ins, delins variant for now.
    """
    # complement SNP ID
    snp_match = HGVSHelper.SNP_PATTERN.match(hgvs)
    if snp_match:
        g = snp_match.groups()
        return '{}{}>{}'.format(g[0], reverse_complement_seq(g[1]), reverse_complement_seq(g[2]))

    # reverse complement ins ID
    ins_match = HGVSHelper.INS_PATTERN.match(hgvs)
    if ins_match:
        g = ins_match.groups()
        return '{}ins{}'.format(g[0], reverse_complement_seq(g[1]))

    # reverse complement delins ID
    delins_match = HGVSHelper.DELINS_PATTERN.match(hgvs)
    if delins_match:
        g = delins_match.groups()
        return '{}delins{}'.format(g[0], reverse_complement_seq(g[1]))

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

    # _ref/_alt cannot be both None, if so, ref and alt are exactly the same, something is wrong with this VCF record
    # assert not (_ref is None and _alt is None)
    if _ref is None and _alt is None:
        raise ValueError('"ref" and "alt" cannot be the same: {}'.format(
            (chr, pos, ref, alt)
        ))

    _pos = int(pos)
    if _ref is None or _alt is None:
        # if either is None, del or ins types
        _pos = _pos + i - 1
        _ref = ref[i - 1:]
        _alt = alt[i - 1:]
    else:
        # both _ref/_alt are not None
        _pos = _pos + i
        _ref = ref[i:]
        _alt = alt[i:]

    return chr, _pos, _ref, _alt


def get_hgvs_from_vcf(chr, pos, ref, alt, mutant_type=None):
    """get a valid hgvs name from VCF-style "chr, pos, ref, alt" data."""
    if not (SeqHelper.SEQ_PATTERN.match(ref) and SeqHelper.SEQ_PATTERN.match(alt)):
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
        # this is an insertion
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
    """get start,end tuple from VCF-style "chr, pos, ref, alt" data."""
    try:
        pos = int(pos)
    except ValueError:
        raise ValueError("Invalid position %s" % repr(pos))

    if not ref or not alt:
        raise ValueError("Cannot decide start/end from {}.".format((chr, pos, ref, alt)))

    if len(ref) == len(alt) == 1:
        # end is the same as start for snp
        start = end = pos
        return start, end

    if len(ref) > 1 and len(alt) == 1:
        # this is a deletion:
        assert ref[0] == alt

        start = pos + 1
        end = pos + len(ref) - 1
        if start == end:
            # TODO: double-check this is the right convention
            end += 1  # end is start+1 for single nt deletion
        return start, end

    if len(ref) == 1 and len(alt) > 1:
        # this is an insertion
        assert alt[0] == ref

        start = pos
        end = pos + 1
        return start, end

    raise ValueError("Cannot decide start/end from {}.".format((chr, pos, ref, alt)))


def prune_minus_sign(hgvs: str):
    """Fix hgvs id like these:
         'chr19:g.58863869C>-',
         'chr10:g.52596077->T',
         'chr10:g.52596077->T',
         'chr12:g.8998751T>-',
         'chr12:g.9004916C>-',
    """
    new_hgvs = None

    match = HGVSHelper.LEGACY_MINUS_SIGN_PATTERN.match(hgvs)
    if match:
        g = match.groups()
        pos, ref, alt = g[1:]
        if ref == '-':
            # should be insertion
            new_hgvs = '{}ins{}'.format(g[0], alt)
        elif alt == '-':
            # should be deletion
            end = int(pos) + len(ref) - 1
            new_hgvs = '{0}_{1}del'.format(g[0], end)
        else:
            print("Error: either cannot fix or no need to fix: ", hgvs)
    else:
        print("Error: hgvs id not in a fixable format: ", hgvs)

    return new_hgvs


def get_hgvs_from_rsid(doc_li, rsid_fn, dbsnp_col, skip_unmatched=False):
    """input doc_li is a list doc with rsid, rsid_fn is a function to return rsid from
       each doc. dbsnp_col is a mongo collection object for dbSNP data
       It will return a generator with the _id as the matching hgvs for a given rsid.
       if a rsid matches multiple hgvs ids, it will produce duplicated docs with each hgvs id.
       If rsid_fn returns None, then the original document is yielded
    """
    for doc in doc_li:
        rsid = rsid_fn(doc)
        if rsid is None:
            yield doc
            continue

        hits = [d for d in dbsnp_col.find({"dbsnp.rsid": rsid})]
        if hits:
            for hit in hits:
                hgvs_id = hit['_id']
                _doc = copy.copy(doc)
                _doc['_id'] = hgvs_id
                yield _doc
        elif skip_unmatched:
            yield doc


def prune_redundant_seq(hgvs: str):
    """
    Some legacy HGVS have redundant sequences that can be pruned. E.g.:

        c.76_78delACT => c.76_78del  (tailing ACT can be pruned)
        c.77_79dupCTG => c.77_79dup  (tailing CTG can be pruned)
        c.112_117delAGGTCAinsTG => c.112_117delinsTG  (AGGTCA in the middle can be pruned)

    The above examples are from https://www.hgvs.org/mutnomen/recs-DNA.html#DNA
    """
    delins_match = HGVSHelper.LEGACY_DELINS_REDUNDANT_SEQ_PATTERN.match(hgvs)
    if delins_match:
        return "".join(delins_match.groups())

    del_match = HGVSHelper.LEGACY_DEL_REDUNDANT_SEQ_PATTERN.match(hgvs)
    if del_match:
        return "".join(del_match.groups())

    dup_match = HGVSHelper.LEGACY_DUP_REDUNDANT_SEQ_PATTERN.match(hgvs)
    if dup_match:
        return "".join(dup_match.groups())

    return hgvs


def get_hgvs_stem(hgvs: str):
    """
    Trim the input hgvs ID to get a stem.
    A stem is defined as a hgvs ID without its tailing sequences.
    This function is usually used to encode long hgvs IDs.
    """
    if hgvs.endswith("del") or hgvs.endswith("dup"):
        return hgvs

    delins_match = HGVSHelper.DELINS_STEM_PATTERN.match(hgvs)
    if delins_match:
        return delins_match.group()  # no subgroups, return the entire match

    ins_match = HGVSHelper.INS_STEM_PATTERN.match(hgvs)
    if ins_match:
        return ins_match.group()  # no subgroups, return the entire match

    """
    Some repeated sequences' HGVS can be extremely long, like:

        'chr6:g.166253474_166253480TC[2]CAATTCCATCCCGTCTCCAACTCAATTCCCATCTTTATCCTCATCTGCATCTCTATCTCCATTCCCATCCGCAACTCCA
        TCCCCATCTGCATCTCTCTCTCCATTCCCATCCCTATCTCCAACTCCATCCCCATCTTCATCCTCATCTGCATCTCCATCTCCATCTCCAACCTCATCTCCATTCTTATCA
        TCTCCATCCCTGTCTCCATCCGCATCACCATCTCCAGCTCCATCTCCATCTCCAGCCTCATCTCCATTCTTATCTTCATCTCCATCCCCATCTGCATCTCTGTCTTCATCC
        CCATCCTCATCCCCATCCTATCTCCAATTCATCCCATCTCCAACTCAATTCCCATCTTCATCCTCATCTGCATCTCTGTCTCCATCCCCATCTGCATCTCCATCTACAACC
        ACATCTCCATCCCCATCTTCATCTCTCTCTCCATCCCCATCCCCATCTCCAACTCCATCCCCATCCCCCTCTCCAA[1]' (rs1780206073)
    """
    repeated_match = HGVSHelper.REP_SEQ_STEM_PATTERN.match(hgvs)
    if repeated_match:
        return repeated_match.group()  # no subgroups, return the entire match

    return hgvs


class DocEncoder:
    KEY_ID = "_id"
    KEY_SEQ_MAP = "_seqhashed"  # doc["_seqhashed"] saves all <seq_hashed : seq> mapping
    KEY_REF = "ref"
    KEY_ALT = "alt"

    ID_INFIX = "seqhashed"
    SEQ_INFIX = "fullseqhashed"

    @classmethod
    def __save_seq_map(cls, doc, seq_hashed, seq):
        """
        `seq_hashed` is the blake2b-encoded `seq`
        A dictionary or entry of <seq_hashed, seq> will be inserted into `doc["_seqhashed"]`
        """
        if cls.KEY_SEQ_MAP in doc:
            doc[cls.KEY_SEQ_MAP][seq_hashed] = seq
        else:
            doc[cls.KEY_SEQ_MAP] = {seq_hashed: seq}

        return doc

    @classmethod
    def __new_id(cls, prefix, seq_hashed):
        # the encoded id will have a pattern of `<prefix>_<infix>_<seq_hashed>`
        new_id = "{prefix}_{infix}_{seq_hashed}".format(prefix=prefix, infix=cls.ID_INFIX, seq_hashed=seq_hashed)
        return new_id

    @classmethod
    def __new_seq(cls, seq_hashed, seq, max_len):
        # the encoded seq will have a pattern of `<prefix>_<infix>_<seq_hashed>`

        # make sure the length of the `<prefix>_<infix>_<seq_hashed>` string is max_len
        prefix_length = max_len - len(seq_hashed) - len(cls.SEQ_INFIX) - 2
        prefix = seq[0: prefix_length]

        new_seq = "{prefix}_{infix}_{seq_hashed}".format(prefix=prefix, infix=cls.SEQ_INFIX, seq_hashed=seq_hashed)
        return new_seq

    @classmethod
    def encode_long_hgvs_id(cls, doc, max_len=512):
        """
        Encode long `doc["_id"]` whose length exceed `max_len`.
        """
        assert cls.KEY_ID in doc

        encoded = False
        if len(doc[cls.KEY_ID]) > max_len:
            prefix = get_hgvs_stem(doc[cls.KEY_ID])
            seq = doc[cls.KEY_ID].replace(prefix, "")
            seq_hashed = blake2b(seq.encode(), digest_size=16).hexdigest()

            doc[cls.KEY_ID] = cls.__new_id(prefix, seq_hashed)
            doc = cls.__save_seq_map(doc, seq_hashed, seq)

            encoded = True

        return encoded, doc

    @classmethod
    def encode_long_ref_alt_seq(cls, doc, key, max_len=1000):
        """
        Encode "ref" and "alt" sequences whose length exceed `max_len` inside `doc[key]` field.
        This method assumes that `doc[key]` is a dict.

        Suppose we have the following structure for `doc`:

            {
                "_id": xxx,
                "_seqhashed": {...},

                "<source-name>": {
                    "alt": xxx
                    "ref": xxx
                    ...
                },
            }

        Then the `key` of interest is the `<source-name>`.
        """
        assert key in doc

        encoded = False
        for seq_key in [cls.KEY_REF, cls.KEY_ALT]:
            seq = doc[key].get(seq_key, None)
            if seq and len(seq) > max_len:
                seq_hashed = blake2b(seq.encode(), digest_size=16).hexdigest()

                doc[key][seq_key] = cls.__new_seq(seq_hashed, seq, max_len)
                doc = cls.__save_seq_map(doc, seq_hashed, seq)

                encoded = True

        return encoded, doc
