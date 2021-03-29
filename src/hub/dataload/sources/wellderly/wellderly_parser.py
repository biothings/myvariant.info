import pandas as pd
from collections import namedtuple, Counter
from itertools import combinations_with_replacement as cwr
from utils.hgvs import _normalized_vcf

# (`start`, `end`) can be different from `pos`
# E.g `chr1:g.10429_10433del` with a genotype `CCCTAA/C`, has pos == 10428, start == 10429 and end == 10433
HgvsID = namedtuple('HgvsID', ['id', 'chrom', 'start', 'end', 'vartype'])


def format_hgvs(chrom, pos, ref, alt):
    """
    Get a valid hgvs name from VCF-style "chrom, pos, ref, alt" data.

    This function is adapted from utils.hgvs.format_hgvs.

    TODO: if utils.hgvs.format_hgvs is refactored to return (start, end), delete this and use that function instead
    See https://github.com/biothings/myvariant.info/issues/111
    """
    chrom, pos = str(chrom), int(pos)
    if chrom.lower().startswith('chr'):
        # trim off leading "chr" if any
        chrom = chrom[3:]

    # python integer range is from -2,147,483,648 to 2,147,483,647
    # The max sequence length is on chr1 (GRCh37.p13), 249,250,621
    pos = int(pos)

    if len(ref) == len(alt) == 1:
        # this is a SNP
        _id = 'chr{0}:g.{1}{2}>{3}'.format(chrom, pos, ref, alt)
        return HgvsID(id=_id, chrom=chrom, start=pos, end=pos, vartype="snp")

    if len(ref) > 1 and len(alt) == 1:
        # this is a deletion:
        if ref[0] == alt:
            start = pos + 1
            end = pos + len(ref) - 1

            if start == end:
                _id = 'chr{0}:g.{1}del'.format(chrom, start)
            else:
                _id = 'chr{0}:g.{1}_{2}del'.format(chrom, start, end)
            return HgvsID(id=_id, chrom=chrom, start=start, end=end, vartype="del")
        else:
            start = pos
            end = start + len(ref) - 1

            _id = 'chr{0}:g.{1}_{2}delins{3}'.format(chrom, start, end, alt)
            return HgvsID(id=_id, chrom=chrom, start=start, end=end, vartype="delins")

    if len(ref) == 1 and len(alt) > 1:
        # this is an insertion
        if alt[0] == ref:
            start, end = pos, pos + 1
            ins_seq = alt[1:]

            _id = 'chr{0}:g.{1}_{2}ins{3}'.format(chrom, start, end, ins_seq)
            return HgvsID(id=_id, chrom=chrom, start=start, end=end, vartype="ins")
        else:
            _id = 'chr{0}:g.{1}delins{2}'.format(chrom, pos, alt)
            return HgvsID(id=_id, chrom=chrom, start=pos, end=pos, vartype="delins")

    if len(ref) > 1 and len(alt) > 1:
        if ref[0] == alt[0]:
            # if ref and alt overlap from the left, trim them first
            _chrom, _pos, _ref, _alt = _normalized_vcf(chrom, pos, ref, alt)
            return format_hgvs(_chrom, _pos, _ref, _alt)
        else:
            start, end = pos, pos + len(ref) - 1

            _id = 'chr{0}:g.{1}_{2}delins{3}'.format(chrom, start, end, alt)
            return HgvsID(id=_id, chrom=chrom, start=start, end=end, vartype="delins")

    raise ValueError("Cannot convert {} into HGVS id.".format((chrom, pos, ref, alt)))


class Genotype:
    def __init__(self, first_allele, second_allele):
        self.first_allele = first_allele
        self.second_allele = second_allele

    def __str__(self):
        return "{}/{}".format(self.first_allele, self.second_allele)


def genotype_combinations(ref: str, alt_list: list) -> list:
    """
    The `GC` column (not VCF-standard) in the Wellderly tsv files represents the count of genotypes in the
    following patterns.

    Suppose a, b, c, ..., z represent the allele frequencies.

    For n = 2 alleles, the genotype frequencies are expanded as (a+b)^2 = a^2 + 2ab + b^2.
    For n = 3 alleles, (a+b+c)^2 = (a+b)^2 + 2(a+b)c + c^2 = a^2 + 2ab + b^2 + 2ac + 2bc + c^2
    For n = 4 alleles, (a+b+c+d)^2 = (a+b+c)^2 + 2(a+b+c)d + d^2 = ...

    Therefore, the genotype combinations (i.e. the order of the `GC` column) would be
    0/0, 0/1, 1/1, 0/2, 1/2, 2/2, 0/3, 1/3, 2/3, 3/3, ...
    ...

    Note that this expanding scheme seems only apply to the Wellderly tsv files.

    For n alleles, there would be {(n+1) choose 2} genotypes regardless of the combination order.
    """
    # The REF must be the first allele in the list
    allele_list = [ref] + alt_list
    genotype_list = [Genotype(first_allele=q, second_allele=p) for (p, q) in cwr(reversed(allele_list), 2)]
    genotype_list.reverse()
    return genotype_list


class WellderlyTsvReader:
    @classmethod
    def generate_document(cls, row: pd.Series, assembly="hg19"):
        # Read REF and ALT alleles
        ref = row["REF"]

        alt_list = row["ALT"].split(",")
        alt_cnt = [int(ac) for ac in row["AC"].split(",")]
        alt_freq = [float(af) for af in row["AF"].split(",")]
        if not len(alt_list) == len(alt_cnt) == len(alt_freq):
            raise ValueError("Inconsistent length between ALT, AC and AF fields. Got row={}".format(row.to_str()))

        # Collect all alleles (REF + ALT)
        allele_list = alt_list + [ref]
        allele_freq = alt_freq + [1 - sum(alt_freq)]  # the `AF` column does not have the `REF` allele frequencies
        allele_json = [{"allele": allele, "freq": freq} for (allele, freq) in zip(allele_list, allele_freq)]

        # Collect all genotypes
        genotype_cnt = [int(gc) for gc in row["GC"].split(",")]
        genotype_list = genotype_combinations(ref=ref, alt_list=alt_list)

        genotype_total = sum(genotype_cnt)
        if genotype_total > 0:
            genotype_freq = [cnt / genotype_total for cnt in genotype_cnt]
        else:  # In some rare cases, `GC` can be nothing but 0's
            genotype_freq = [0 for _ in genotype_cnt]
        genotype_json = [{"count": cnt, "freq": freq, 'genotype': str(gt)} for (cnt, freq, gt)
                         in zip(genotype_cnt, genotype_freq, genotype_list) if cnt > 0]

        # Generate ID and document for each (REF, ALT) pair
        chrom, pos = row["CHROM:POS"].split(":")
        for alt in alt_list:
            hgvsID = format_hgvs(chrom, pos, ref, alt)

            document = {
                '_id': hgvsID.id,
                'wellderly': {
                    'chrom': hgvsID.chrom,
                    'pos': pos, 'ref': ref, 'alt': alt,
                    assembly: {'start': hgvsID.start, 'end': hgvsID.end},
                    'vartype': hgvsID.vartype,
                    'alleles': allele_json,
                    'genotypes': genotype_json
                }
            }

            yield document

    @classmethod
    def load_data(cls, file, assembly="hg19"):
        # Skip 'AN' column
        data_types = {"CHROM:POS": str, "REF": str, "ALT": str, "AC": str, "GC": str, "AF": str}
        df = pd.read_csv(file, sep="\t", usecols=data_types.keys(), dtype=data_types)
        for _, row in df.iterrows():
            yield from cls.generate_document(row, assembly)
