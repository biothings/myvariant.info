import unittest
from utils.hgvs import DocEncoder


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
