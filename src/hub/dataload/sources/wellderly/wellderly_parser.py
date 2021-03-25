import pandas as pd
from collections import namedtuple, Counter
from itertools import combinations_with_replacement as cwr


class Genotype:
    def __init__(self, first_allele, second_allele):
        self.first_allele = first_allele
        self.second_allele = second_allele

    def __str__(self):
        return "{}/{}".format(self.first_allele, self.second_allele)

# (`start`, `end`) can be different from `pos`
# E.g `chr1:g.10429_10433del` with a genotype `CCCTAA/C`, has pos == 10428, start == 10429 and end == 10433
HgvsID = namedtuple('HgvsID', ['_id', 'chrom', 'start', 'end', 'vartype'])


class MyVariantUtil:
    """
    Originally from https://github.com/biothings/biothings_client.py/blob/092ffa1e1e35fbee2c9b7eb5defbee160697e3d8/biothings_client/mixins/variant.py

    Adapted the following two methods to @classmethod's

    Also returned `chrom`, `start`, `end`, `vartype` in `format_hgvs()`
    """

    @classmethod
    def _normalized_vcf(cls, chrom, pos, ref, alt):
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
        # assert not (_ref is None and _alt is None)
        if _ref is None and _alt is None:
            raise ValueError('"ref" and "alt" cannot be the same: {}'.format((chrom, pos, ref, alt)))

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

        return chrom, _pos, _ref, _alt

    @classmethod
    def format_hgvs(cls, chrom, pos, ref, alt):
        """get a valid hgvs name from VCF-style "chrom, pos, ref, alt" data.
        Example:
            >>> MyVariantUtil.format_hgvs("1", 35366, "C", "T")
            >>> MyVariantUtil.format_hgvs("2", 17142, "G", "GA")
            >>> MyVariantUtil.format_hgvs("MT", 8270, "CACCCCCTCT", "C")
            >>> MyVariantUtil.format_hgvs("X", 107930849, "GGA", "C")
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
            return HgvsID(_id=_id, chrom=chrom, start=pos, end=pos, vartype="snp")

        if len(ref) > 1 and len(alt) == 1:
            # this is a deletion:
            if ref[0] == alt:
                start = pos + 1
                end = pos + len(ref) - 1

                if start == end:
                    _id = 'chr{0}:g.{1}del'.format(chrom, start)
                else:
                    _id = 'chr{0}:g.{1}_{2}del'.format(chrom, start, end)
                return HgvsID(_id=_id, chrom=chrom, start=start, end=end, vartype="del")
            else:
                start = pos
                end = start + len(ref) - 1

                _id = 'chr{0}:g.{1}_{2}delins{3}'.format(chrom, start, end, alt)
                return HgvsID(_id=_id, chrom=chrom, start=start, end=end, vartype="delins")

        if len(ref) == 1 and len(alt) > 1:
            # this is an insertion
            if alt[0] == ref:
                start, end = pos, pos + 1
                ins_seq = alt[1:]

                _id = 'chr{0}:g.{1}_{2}ins{3}'.format(chrom, start, end, ins_seq)
                return HgvsID(_id=_id, chrom=chrom, start=start, end=end, vartype="ins")
            else:
                _id = 'chr{0}:g.{1}delins{2}'.format(chrom, pos, alt)
                return HgvsID(_id=_id, chrom=chrom, start=pos, end=pos, vartype="delins")

        if len(ref) > 1 and len(alt) > 1:
            if ref[0] == alt[0]:
                # if ref and alt overlap from the left, trim them first
                _chrom, _pos, _ref, _alt = cls._normalized_vcf(chrom, pos, ref, alt)
                return cls.format_hgvs(_chrom, _pos, _ref, _alt)
            else:
                start, end = pos, pos + len(alt) - 1

                _id = 'chr{0}:g.{1}_{2}delins{3}'.format(chrom, start, end, alt)
                return HgvsID(_id=_id, chrom=chrom, start=start, end=end, vartype="delins")

        raise ValueError("Cannot convert {} into HGVS id.".format((chrom, pos, ref, alt)))


# class HardyWeinbergHelper:
#     def __init__(self, allele_cnt=10):
#         if allele_cnt < 1:
#             raise ValueError("Meaningless count of alleles. Got allele_cnt={}".format(allele_cnt))
#
#         self.allele_cnt = allele_cnt
#         self.hist_of_diploid_genotype_cnt = [self.n_combinations(n, 2, with_replacement=True)
#                                              for n in range(0, allele_cnt + 1)]
#
#     def gc_index(self, nth_alt):
#         """
#         The `GC` column (not VCF-standard) in the Wellderly tsv files seems to represent the count of genotypes in the
#         following patterns.
#
#         Suppose a, b, c, ..., z represent the allele frequencies.
#
#         For n = 2 alleles, the genotype frequencies are expanded as (a+b)^2 = a^2 + 2ab + b^2. Therefore, e.g. given
#         REF = A, ALT = T and GC = "1157,23,1", we have number of genotype AA = 1157, AT = 23 and TT = 1. This splitting
#         pattern must be consistent to the `AC` column (VCF-standard; allele count in genotypes, for each ALT allele,
#         in the same order as listed). E.g. for the above case, the `AC` field for allele T must be 25
#         (23 in AT plus 2 in TT).
#
#         For n = 3 alleles, expanded as (a+b+c)^2 = (a+b)^2 + 2(a+b)c + c^2 = a^2 + 2ab + b^2 + 2ac + 2bc + c^2
#         For n = 4 alleles, expanded as (a+b+c+d)^2 = (a+b+c)^2 + 2(a+b+c)d + d^2 = ...
#         ...
#
#         Therefore, the length of a `GC` field is exactly the number of genotypes for that exact row in a Wallderly tsv
#         file. And no matter how long it is, given a fixed REF allele (whose frequency is 'a')
#
#         - For the 1st ALT allele (whose frequency is 'b'), the genotype counts are GC[0], GC[1] and GC[2]
#         - For the 2nd ALT allele (whose frequency is 'c'), the genotype counts are GC[0], GC[3] and GC[5]
#         - For the 3rd ALT allele (whose frequency is 'd'), the genotype counts are GC[0], GC[6] and GC[9]
#         - ...
#
#         The index of genotype counts in GC for n-th ALT alleles can be computed from the pre-computed
#         `self.hist_of_diploid_genotype_cnt`:
#
#                              nth_alt =        1, 2, 3,  4,  5,  6,  ...
#                           allele_cnt =     1, 2, 3, 4,  5,  6,  7,  ...
#         hist_of_diploid_genotype_cnt = [0, 1, 3, 6, 10, 15, 21, 28, ...]
#         """
#
#         if nth_alt < 1:
#             raise ValueError("Meaningless order of ALT alleles. Got nth_alt={}".format(nth_alt))
#
#         if nth_alt >= self.allele_cnt:
#             # Dynamically expanding the histogram
#             updated_allele_cnt = nth_alt + 1
#             self.hist_of_diploid_genotype_cnt += [self.n_combinations(n, 2, with_replacement=True)
#                                                   for n in range(self.allele_cnt + 1, updated_allele_cnt + 1)]
#             self.allele_cnt = updated_allele_cnt
#
#         return 0, self.hist_of_diploid_genotype_cnt[nth_alt], self.hist_of_diploid_genotype_cnt[nth_alt+1] - 1
#
#     @classmethod
#     def choose(cls, n, k):
#         """
#         A fast way to calculate binomial coefficients.
#
#         Originally from https://stackoverflow.com/a/3025547
#         """
#         if 0 <= k <= n:
#             """
#             Due to the symmetry, (n choose k) == (n choose (n-k)).
#
#             Suppose k is small, after the loop:
#
#             - numerator = n * (n-1) * ... * (n-(k-1))
#             - denominator = k * (k-1) * ... * 2 * 1
#             """
#             numerator = 1
#             denominator = 1
#             for t in range(1, min(k, n - k) + 1):
#                 numerator *= n
#                 denominator *= t
#                 n -= 1
#             return numerator // denominator
#         else:
#             return 0
#
#     @classmethod
#     def n_combinations(cls, n, k, with_replacement=False):
#         """
#         Number of combinations when drawing k items out of n.
#         """
#         if not with_replacement:
#             return cls.choose(n, k)
#         else:
#             return cls.choose(n + k - 1, k)

class HardyWeinbergHelper:
    @classmethod
    def genotype_combinations(cls, ref: str, alt_list: list) -> list:
        """
        The `GC` column (not VCF-standard) in the Wellderly tsv files seems to represent the count of genotypes in the
        following patterns.

        Suppose a, b, c, ..., z represent the allele frequencies.

        For n = 2 alleles, the genotype frequencies are expanded as (a+b)^2 = a^2 + 2ab + b^2. Therefore, e.g. given
        REF = A, ALT = T and GC = "1157,23,1", we have number of genotype AA = 1157, AT = 23 and TT = 1. This splitting
        pattern must be consistent to the `AC` column (VCF-standard; allele count in genotypes, for each ALT allele,
        in the same order as listed). E.g. for the above case, the `AC` field for allele T must be 25
        (23 in AT plus 2 in TT).

        For n = 3 alleles, expanded as (a+b+c)^2 = (a+b)^2 + 2(a+b)c + c^2 = a^2 + 2ab + b^2 + 2ac + 2bc + c^2
        For n = 4 alleles, expanded as (a+b+c+d)^2 = (a+b+c)^2 + 2(a+b+c)d + d^2 = ...
        ...

        Note that this expanding scheme seems only apply to the Wellderly tsv files.

        For n alleles, there would be {(n+1) choose 2} genotypes regardless of the combination order.
        """
        # The REF must be the first allele in the list
        allele_list = [ref] + alt_list
        genotype_list = [Genotype(first_allele=q, second_allele=p) for (p, q) in cwr(reversed(allele_list), 2)]
        genotype_list.reverse()
        return genotype_list

    @classmethod
    def check_count_constraint(cls, genotype_list: list, genotype_cnt: list, alt_list: list, alt_cnt: list,
                               check_genotype_length=False, check_alt_length=False):
        """
        Check if the `GC` and `AC` columns are consistent with the genotype combination

        `genotype_cnt`, `alt_list` and `alt_cnt` are directly parsed from the `GC`, `ALT` and `AC` columns respectively.

        - GC is not a VCF-standard field
        - ALT - VCF-standard; alternate base(s): comma-separated list of alternate non-reference alleles.
        - AC - VCF-standard; allele count in genotypes, for each ALT allele, in the same order as listed

        See https://samtools.github.io/hts-specs/VCFv4.3.pdf for more information about these two fields

        `genotype_list` and `genotype_cnt` should be of the same length;
        `alt_list` and `alt_cnt` must be of the same length by definition.

        E.g. given REF = C, ALT = [G, T], AC = [3, 2], GC = [78, 3, 0, 0, 0, 1], the genotype combinations must be
        ['C/C', 'C/G', 'G/G', 'C/T', 'G/T', 'T/T'] and the AC numbers constraint must be met.

        | Genotype | GC | num of 'G' | num of 'T' |
        |:--------:|:--:|:----------:|:----------:|
        |    C/C   | 78 |      0     |      0     |
        |    C/G   |  3 |      3     |      0     |
        |    G/G   |  0 |      0     |      0     |
        |    C/T   |  0 |      0     |      0     |
        |    G/T   |  0 |      0     |      0     |
        |    T/T   |  1 |      0     |      2     |
        |    ---   |  - |      -     |      -     |
        |    AC    |  - |      3     |      2     |
        """

        if check_genotype_length:
            if len(genotype_list) != len(genotype_cnt):
                raise ValueError("Inconsistent genotype lengths. Got genotype_list={}, genotype_cnt={}".
                                 format(genotype_list, genotype_cnt))

        if check_alt_length:
            if len(alt_list) != len(alt_cnt):
                raise ValueError("Inconsistent ALT lengths. Got alt_list={}, alt_cnt={}".
                                 format(alt_list, alt_cnt))

        allele_counter = Counter()
        for gt, cnt in zip(genotype_list, genotype_cnt):
            allele_counter[gt.first_allele] += cnt
            allele_counter[gt.second_allele] += cnt

        for i in range(len(alt_list)):
            if allele_counter(alt_list[i]) != alt_cnt[i]:
                raise ValueError("Inconsistent AC value for ALT {}. "
                                 "Got genotype_list={}, genotype_cnt={}, "
                                 "alt_list={}, alt_cnt={}".
                                 format(alt_list[i], genotype_list, genotype_cnt, alt_list, alt_cnt))

        # return nothing if every constraint is met
        pass


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
        genotype_list = HardyWeinbergHelper.genotype_combinations(ref=ref, alt_list=alt_list)
        HardyWeinbergHelper.check_count_constraint(genotype_list, genotype_cnt, alt_list, alt_cnt,
                                                   check_genotype_length=True, check_alt_length=False)
        genotype_total = sum(genotype_cnt)
        genotype_freq = [cnt / genotype_total for cnt in genotype_cnt]
        genotype_json = [{"count": cnt, "freq": freq, 'genotype': str(gt)} for (cnt, freq, gt)
                         in zip(genotype_cnt, genotype_freq, genotype_list) if cnt > 0]

        # Generate ID and document for each (REF, ALT) pair
        chrom, pos = row["CHROM:POS"].split(":")
        for alt in alt_list:
            hgvsID = MyVariantUtil.format_hgvs(chrom, pos, ref, alt)

            document = {'_id': hgvsID._id, 'chrom': hgvsID.chrom,
                        'pos': pos, 'ref': ref, 'alt': alt,
                        assembly: {'start': hgvsID.start, 'end': hgvsID.end},
                        'vartype': hgvsID.vartype,
                        'alleles': allele_json,
                        'genotypes': genotype_json}

            yield document

    @classmethod
    def load_data(cls, file, assembly="hg19"):
        # Skip 'AN' column
        data_types = {"CHROM:POS": str, "REF": str, "ALT": str, "AC": str, "GC": str, "AF": str}
        df = pd.read_csv(file, sep="\t", usecols=data_types.keys(), dtype=data_types)
        for _, row in df.iterrows():
            yield from cls.generate_document(row, assembly)
