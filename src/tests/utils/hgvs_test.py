import unittest
from utils.hgvs import *
from utils.hgvs import _normalized_vcf


class TestFunctions(unittest.TestCase):
    def test_is_snp(self):
        hgvs = "chrY:g.1885021C>A"
        self.assertTrue(is_snp(hgvs))

        hgvs = "chrY:g.21733168del"
        self.assertFalse(is_snp(hgvs))

        hgvs = "chrMT:m.8279_8280del"
        self.assertFalse(is_snp(hgvs))

        hgvs = "chrMT:m.15452_15453delinsAC"
        self.assertFalse(is_snp(hgvs))

        hgvs = "chrY:g.21878072_21878073insT"
        self.assertFalse(is_snp(hgvs))

        hgvs = "chrY:g.21724699_21724700delinsTTGTACAGAGA"
        self.assertFalse(is_snp(hgvs))

    def test_reverse_complement_seq(self):
        pass
        # TODO fix bug

    def test_reverse_complement_hgvs(self):
        pass
        # TODO it uses the buggy `test_reverse_complement_seq`

    def test_normalized_vcf(self):
        # TODO rename `_normalized_vcf` to make it non-private

        input_vcf = ("X", 100, "CTTTT", "CT")
        output_vcf = ('X', 101, 'TTTT', 'T')
        self.assertEqual(output_vcf, _normalized_vcf(*input_vcf))

        input_vcf = ("X", 100, "TC", "TG")
        output_vcf = ('X', 101, 'C', 'G')
        self.assertEqual(output_vcf, _normalized_vcf(*input_vcf))

        input_vcf = ("X", 123, "T", "C")
        output_vcf = ('X', 123, 'T', 'C')
        self.assertEqual(output_vcf, _normalized_vcf(*input_vcf))

        input_vcf = ("X", 123, "CC", "CCT")
        output_vcf = ('X', 124, 'C', 'CT')
        self.assertEqual(output_vcf, _normalized_vcf(*input_vcf))

        # TODO failed
        # input_vcf = ("X", 123, "TCCCCT", "CCCCT")
        # output_vcf = ('X', 123, 'TC', 'C')
        # self.assertEqual(output_vcf, _normalized_vcf(*input_vcf))

        input_vcf = ("X", 123, "TCCCCTA", "CCCCT")
        output_vcf = ('X', 123, 'TCCCCTA', 'CCCCT')
        self.assertEqual(output_vcf, _normalized_vcf(*input_vcf))

        # TODO failed
        # input_vcf = ("X", 123, 'AAATCCCCTA', 'AAACCCCTA')
        # output_vcf = ('X', 125, 'AT', 'A')
        # self.assertEqual(output_vcf, _normalized_vcf(*input_vcf))

        input_vcf = ("X", 123, 'CAAATCCCCTAG', 'AAACCCCTA')
        output_vcf = ('X', 123, 'CAAATCCCCTAG', 'AAACCCCTA')
        self.assertEqual(output_vcf, _normalized_vcf(*input_vcf))

    def test_get_hgvs_from_vcf(self):
        input_vcf = ("X", 100, "A", "C")
        output_hgvs, output_vartype = get_hgvs_from_vcf(*input_vcf, mutant_type=True)
        expected_hgvs, expected_vartype = "chrX:g.100A>C", "snp"
        self.assertEqual(expected_hgvs, output_hgvs)
        self.assertEqual(expected_vartype, output_vartype)

        input_vcf = ("X", 100, "CT", "C")
        output_hgvs, output_vartype = get_hgvs_from_vcf(*input_vcf, mutant_type=True)
        expected_hgvs, expected_vartype = "chrX:g.101del", "del"
        self.assertEqual(expected_hgvs, output_hgvs)
        self.assertEqual(expected_vartype, output_vartype)

        input_vcf = ("X", 100, "CTTTT", "CT")
        output_hgvs, output_vartype = get_hgvs_from_vcf(*input_vcf, mutant_type=True)
        expected_hgvs, expected_vartype = "chrX:g.102_104del", "del"
        self.assertEqual(expected_hgvs, output_hgvs)
        self.assertEqual(expected_vartype, output_vartype)

        input_vcf = ("X", 100, "CT", "A")
        output_hgvs, output_vartype = get_hgvs_from_vcf(*input_vcf, mutant_type=True)
        expected_hgvs, expected_vartype = "chrX:g.100_101delinsA", "delins"
        self.assertEqual(expected_hgvs, output_hgvs)
        self.assertEqual(expected_vartype, output_vartype)

        input_vcf = ("X", 100, "A", "AT")
        output_hgvs, output_vartype = get_hgvs_from_vcf(*input_vcf, mutant_type=True)
        expected_hgvs, expected_vartype = "chrX:g.100_101insT", "ins"
        self.assertEqual(expected_hgvs, output_hgvs)
        self.assertEqual(expected_vartype, output_vartype)

        input_vcf = ("X", 100, "A", "CT")
        output_hgvs, output_vartype = get_hgvs_from_vcf(*input_vcf, mutant_type=True)
        expected_hgvs, expected_vartype = "chrX:g.100delinsCT", "delins"
        self.assertEqual(expected_hgvs, output_hgvs)
        self.assertEqual(expected_vartype, output_vartype)

        input_vcf = ("X", 100, "CT", "CTTTT")
        output_hgvs, output_vartype = get_hgvs_from_vcf(*input_vcf, mutant_type=True)
        expected_hgvs, expected_vartype = "chrX:g.101_102insTTT", "ins"
        self.assertEqual(expected_hgvs, output_hgvs)
        self.assertEqual(expected_vartype, output_vartype)

        input_vcf = ("X", 100, "", "CTTTT")
        self.assertRaises(ValueError, get_hgvs_from_vcf, *input_vcf, True)

        input_vcf = ("X", 100, "GENE", "SEQ")
        self.assertRaises(ValueError, get_hgvs_from_vcf, *input_vcf, True)

        input_vcf = ("X", 100, "SEQ", "GENE")
        self.assertRaises(ValueError, get_hgvs_from_vcf, *input_vcf, True)

    def test_get_pos_start_end(self):
        input_vcf = ("X", "one-hundred", "A", "C")
        self.assertRaises(ValueError, get_pos_start_end, *input_vcf)

        input_vcf = ("X", "100", "A", "")
        self.assertRaises(ValueError, get_pos_start_end, *input_vcf)

        input_vcf = ("X", "100", "", "C")
        self.assertRaises(ValueError, get_pos_start_end, *input_vcf)

        input_vcf = ("X", "100", "A", "C")
        output_start, output_end = get_pos_start_end(*input_vcf)
        expected_start, expected_end = 100, 100
        self.assertEqual(expected_start, output_start)
        self.assertEqual(expected_end, output_end)

        input_vcf = ("X", "100", "CT", "C")
        output_start, output_end = get_pos_start_end(*input_vcf)
        expected_start, expected_end = 101, 102
        self.assertEqual(expected_start, output_start)
        self.assertEqual(expected_end, output_end)

        # TODO https://github.com/biothings/myvariant.info/issues/111
        # input_vcf = ("X", "100", "CT", "A")
        # output_start, output_end = get_pos_start_end(*input_vcf)
        # expected_start, expected_end = 100, 101
        # self.assertEqual(expected_start, output_start)
        # self.assertEqual(expected_end, output_end)

        input_vcf = ("X", "100", "C", "CT")
        output_start, output_end = get_pos_start_end(*input_vcf)
        expected_start, expected_end = 100, 101
        self.assertEqual(expected_start, output_start)
        self.assertEqual(expected_end, output_end)

        # TODO https://github.com/biothings/myvariant.info/issues/111
        # input_vcf = ("X", "100", "A", "CT")
        # output_start, output_end = get_pos_start_end(*input_vcf)
        # expected_start, expected_end = 100, 100
        # self.assertEqual(expected_start, output_start)
        # self.assertEqual(expected_end, output_end)

        input_vcf = ("X", "100", "AC", "GT")
        self.assertRaises(ValueError, get_pos_start_end, *input_vcf)

    def test_fix_hgvs_indel(self):
        input_hgvs = "chr19:g.58863869C>-"
        expected_hgvs = "chr19:g.58863869_58863869del"
        self.assertEqual(expected_hgvs, fix_hgvs_indel(input_hgvs))

        input_hgvs = "chr10:g.52596077->T"
        expected_hgvs = "chr10:g.52596077insT"
        self.assertEqual(expected_hgvs, fix_hgvs_indel(input_hgvs))

        input_hgvs = "chr19:g.58863869A>C"
        expected_hgvs = None
        self.assertEqual(expected_hgvs, fix_hgvs_indel(input_hgvs))

    def test_trim_delseq_from_hgvs(self):
        input_hgvs = "chrX:g.100_101delinsA"
        expected_prefix = "chrX:g.100_101delins"
        self.assertEqual(expected_prefix, trim_delseq_from_hgvs(input_hgvs, True))

        input_hgvs = "chrX:g.100_101insT"
        expected_prefix = "chrX:g.100_101ins"
        self.assertEqual(expected_prefix, trim_delseq_from_hgvs(input_hgvs, True))

        input_hgvs = "chrX:g.102_104del"
        expected_prefix = "chrX:g.102_104del"
        self.assertEqual(expected_prefix, trim_delseq_from_hgvs(input_hgvs, True))

        input_hgvs = "chrX:g.102_104dup"
        expected_prefix = "chrX:g.102_104dup"
        self.assertEqual(expected_prefix, trim_delseq_from_hgvs(input_hgvs, True))

        input_hgvs = "chrX:g.102_104dup"
        expected_prefix = "chrX:g.102_104dup"
        self.assertEqual(expected_prefix, trim_delseq_from_hgvs(input_hgvs, True))


class TestDocEncoder(unittest.TestCase):
    def setUp(self):
        self.fake_prefix = "chr1:g.100_103delins"
        self.fake_seq = "CTAACTAACTAA"
        self.fake_id = self.fake_prefix + self.fake_seq
        self.fake_doc = {
            DocEncoder.KEY_ID: self.fake_id
        }

    def test_encode_long_hgvs_id_with_no_change(self):
        max_len = len(self.fake_id) + 1  # Ensure it not to be encoded
        encoded, doc = DocEncoder.encode_long_hgvs_id(self.fake_doc, max_len=max_len)

        self.assertFalse(encoded, "Must have not been encoded")
        self.assertEqual(self.fake_doc, doc, "No change should be made if not encoded")

    def test_encode_long_hgvs_id_with_assertion_error(self):
        with self.assertRaises(AssertionError, msg="Expect an AssertionError if '_id' not in doc"):
            DocEncoder.encode_long_hgvs_id({}, max_len=42)

    def test_encode_long_hgvs_id_without_seq_map_key(self):
        max_len = len(self.fake_id) // 2  # Ensure it to be encoded
        encoded, doc = DocEncoder.encode_long_hgvs_id(self.fake_doc, max_len=max_len)

        self.assertTrue(encoded, "Must have been encoded")
        self.assertTrue(doc[DocEncoder.KEY_ID].startswith(self.fake_prefix),
                        "New ID must starts with the orig prefix")
        self.assertTrue(DocEncoder.KEY_SEQ_MAP in doc, "Must have the seq mapping key")
        self.assertEqual(len(doc[DocEncoder.KEY_SEQ_MAP]), 1, "Seq mapping must have only 1 element here")
        self.assertEqual(list(doc[DocEncoder.KEY_SEQ_MAP].values())[0], self.fake_seq,
                         "Seq mapping must contain the orig sequence")

    def test_encode_long_hgvs_id_with_seq_map_key(self):
        self.fake_doc[DocEncoder.KEY_SEQ_MAP] = {"foo": "bar"}

        max_len = len(self.fake_id) // 2  # Ensure it to be encoded
        encoded, doc = DocEncoder.encode_long_hgvs_id(self.fake_doc, max_len=max_len)

        self.assertTrue(encoded, "Must have been encoded")
        self.assertTrue(doc[DocEncoder.KEY_ID].startswith(self.fake_prefix),
                        "New ID must starts with the orig prefix")
        self.assertEqual(len(doc[DocEncoder.KEY_SEQ_MAP]), 2, "Seq mapping must have only 2 elements here")

        for key, value in doc[DocEncoder.KEY_SEQ_MAP].items():
            if key != "foo":
                self.assertEqual(value, self.fake_seq, "Seq mapping must contain the orig sequence")

    def test_encode_long_ref_alt_seq_with_assertion_error(self):
        with self.assertRaises(AssertionError, msg="Expect an AssertionError if key not in doc"):
            DocEncoder.encode_long_ref_alt_seq({}, key="WhatEver", max_len=42)

    def test_encode_long_ref_alt_seq(self):
        fake_ref_seq = "CTAACTAACTAACTAACTAACTAACTAACTAACTAACTAACTAACTAACTAACTAACTAACTAACTAACTAACTAACTAACTAACTAACTAACTA"
        fake_alt_seq = "ACCCCCCCCCCCACCCCCCCCCCCACCCCCCCCCCCACCCCCCCCCCCACCCCCCCCCCCACCCCCCCCCCCACCCCCCCCCCCACCCCCCCCCC"
        fake_source_key = "wellderly"
        self.fake_doc[fake_source_key] = {"ref": fake_ref_seq, "alt": fake_alt_seq}

        max_len = max(len(fake_ref_seq), len(fake_alt_seq)) - 20  # Ensure it to be encoded
        encoded, doc = DocEncoder.encode_long_ref_alt_seq(self.fake_doc, key=fake_source_key, max_len=max_len)

        self.assertTrue(encoded, "Must have been encoded")
        self.assertTrue(DocEncoder.KEY_SEQ_MAP in doc, "Must have the seq mapping key")
        self.assertEqual(len(doc[DocEncoder.KEY_SEQ_MAP]), 2, "Seq mapping must have only 2 element here")

        seqs = doc[DocEncoder.KEY_SEQ_MAP].values()
        self.assertIn(fake_ref_seq, seqs, "ref seq must in the seq mapping")
        self.assertIn(fake_alt_seq, seqs, "alt seq must in the seq mapping")

    def test_encode_long_ref_alt_seq_without_seq(self):
        fake_source_key = "wellderly"
        self.fake_doc[fake_source_key] = {}

        encoded, doc = DocEncoder.encode_long_ref_alt_seq(self.fake_doc, key=fake_source_key, max_len=42)

        self.assertFalse(encoded, "Must have not been encoded")
        self.assertEqual(self.fake_doc, doc, "No change should be made if not encoded")


if __name__ == '__main__':
    unittest.main()
