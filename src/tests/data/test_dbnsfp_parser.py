"""
Unit tests for issue #179: report all REVEL scores from dbNSFP.
https://github.com/biothings/myvariant.info/issues/179

Root cause: dbNSFP stores one row per transcript per variant. The v1 parser
merged duplicate-ID rows by only extending the `aa` field, silently discarding
all other per-transcript scores (REVEL, SIFT, AlphaMissense, etc.) from rows 2+.

The v2 parser fixes this by storing all transcript-specific annotations under
`dbnsfp.protein` (a list, one entry per transcript), so all REVEL scores are
preserved.

Variant under test: chrX:g.153693944C>A (ClinGen CAID: CA415086302, gene SLC6A8)
dbNSFP provides REVEL scores for at least 3 transcripts: 0.173, 0.653, 0.177.
"""
import os
import sys
import unittest

# Ensure src/ is on the path so hub modules are importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import importlib.util

# Load the v2 parser directly to avoid triggering biothings hub initialisation
# (which requires a running config) via the dbnsfp __init__.py.
_PARSER_PATH = os.path.join(
    os.path.dirname(__file__),
    "..", "..", "hub", "dataload", "sources", "dbnsfp", "dbnsfp_parser_48a_v2.py"
)
_spec = importlib.util.spec_from_file_location("dbnsfp_parser_48a_v2", _PARSER_PATH)
_v2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_v2)

COLUMNS = _v2.COLUMNS
construct_hg38_doc = _v2.construct_hg38_doc
construct_hg19_doc = _v2.construct_hg19_doc
NA_VALUES = _v2.NA_VALUES


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _base_row():
    """Return a row dict with every parsed column set to NA ('.')."""
    return {col.name: "." for col in COLUMNS}


def _slc6a8_row(transcriptid, proteinid, aapos, revel_score, revel_rankscore):
    """
    Build a minimal dbNSFP row dict for chrX:g.153693944C>A (hg38),
    parameterised by per-transcript fields.

    All columns not supplied are set to '.' (NA) so the parser skips them.
    Non-transcript-specific columns (chrom, pos, ref, alt, etc.) are fixed
    to the real values of this variant.
    """
    row = _base_row()
    row.update({
        # Genomic coordinates (hg38)
        "#chr": "X",
        "pos(1-based)": "153693944",
        "ref": "C",
        "alt": "A",
        # Genomic coordinates (hg19 / hg18)
        "hg19_chr": "X",
        "hg19_pos(1-based)": "152959399",
        "hg18_pos(1-based)": "152612593",
        # Per-transcript fields
        "aapos": str(aapos),
        "genename": "SLC6A8",
        "Ensembl_geneid": "ENSG00000130821",
        "Ensembl_transcriptid": transcriptid,
        "Ensembl_proteinid": proteinid,
        "Uniprot_acc": "H7C0F5",
        "Uniprot_entry": "H7C0F5_HUMAN",
        "cds_strand": "+",
        "Reliability_index": "6",
        # REVEL scores (transcript-specific since dbNSFP 4.2a)
        "REVEL_score": str(revel_score),
        "REVEL_rankscore": str(revel_rankscore),
    })
    return row


# Three real dbNSFP transcript rows for chrX:g.153693944C>A (CA415086302).
# REVEL scores taken from the dbNSFP 4.3a data referenced in issue #179.
_ROW_T1 = lambda: _slc6a8_row("ENST00000457723", "ENSP00000394742", 55,  0.173, 0.43840)
_ROW_T2 = lambda: _slc6a8_row("ENST00000611849", "ENSP00000484575", 394, 0.653, 0.72000)
_ROW_T3 = lambda: _slc6a8_row("ENST00000612104", "ENSP00000480772", 279, 0.177, 0.45000)


def _merge_docs_hg38(rows):
    """
    Mirror the merge logic in v2 load_file for hg38.
    Rows with the same HGVS id have their `protein` lists extended.
    After merging, a single-protein list is collapsed to a dict (as load_file does).
    """
    last_doc = None
    for row in rows:
        curr_doc = construct_hg38_doc(row)
        if curr_doc is None:
            continue
        if last_doc is None:
            last_doc = curr_doc
            continue
        if curr_doc["_id"] == last_doc["_id"]:
            last_doc["dbnsfp"]["protein"].extend(curr_doc["dbnsfp"]["protein"])
        else:
            raise AssertionError(
                "Unexpected distinct variant IDs in test rows: "
                f"{last_doc['_id']} vs {curr_doc['_id']}"
            )
    if last_doc is None:
        return None
    if len(last_doc["dbnsfp"]["protein"]) == 1:
        last_doc["dbnsfp"]["protein"] = last_doc["dbnsfp"]["protein"][0]
    return last_doc


# ---------------------------------------------------------------------------
# Tests: single-transcript variant behaviour
# ---------------------------------------------------------------------------

class TestV2SingleTranscript(unittest.TestCase):
    """Sanity checks for a single-transcript variant using the v2 parser."""

    def setUp(self):
        self.doc = construct_hg38_doc(_ROW_T1())

    def test_doc_is_not_none(self):
        self.assertIsNotNone(self.doc)

    def test_hgvs_id_hg38(self):
        self.assertEqual(self.doc["_id"], "chrX:g.153693944C>A")

    def test_protein_is_list_before_collapse(self):
        """construct_hg38_doc always returns protein as a list (collapse happens in load_file)."""
        self.assertIsInstance(self.doc["dbnsfp"]["protein"], list)
        self.assertEqual(len(self.doc["dbnsfp"]["protein"]), 1)

    def test_revel_score_stored_under_protein(self):
        """REVEL score is under dbnsfp.protein[0].revel.score in v2."""
        protein = self.doc["dbnsfp"]["protein"][0]
        self.assertIn("revel", protein)
        self.assertEqual(protein["revel"]["score"], 0.173)

    def test_transcript_stored_under_protein(self):
        protein = self.doc["dbnsfp"]["protein"][0]
        self.assertEqual(protein["transcriptid"], "ENST00000457723")

    def test_hg19_id(self):
        doc = construct_hg19_doc(_ROW_T1())
        self.assertIsNotNone(doc)
        self.assertEqual(doc["_id"], "chrX:g.152959399C>A")


# ---------------------------------------------------------------------------
# Tests: multi-transcript merge — the core fix for issue #179
# ---------------------------------------------------------------------------

class TestV2MultipleTranscriptsREVEL(unittest.TestCase):
    """
    Tests for issue #179: all per-transcript REVEL scores must be preserved.

    In dbNSFP, the same genomic variant (identical chr/pos/ref/alt) has one row
    per transcript.  The v2 parser merges these into a single document with a
    `protein` list.  All REVEL scores must appear in that list.
    """

    def setUp(self):
        self.doc = _merge_docs_hg38([_ROW_T1(), _ROW_T2(), _ROW_T3()])

    def test_protein_is_list_for_multi_transcript(self):
        """dbnsfp.protein must be a list when multiple transcripts are present."""
        self.assertIsInstance(
            self.doc["dbnsfp"]["protein"], list,
            "dbnsfp.protein must be a list for multi-transcript variants "
            "(regression: v1 only kept data from the first row)",
        )

    def test_protein_list_has_one_entry_per_transcript(self):
        self.assertEqual(len(self.doc["dbnsfp"]["protein"]), 3)

    def test_all_revel_scores_are_present(self):
        """
        Issue #179: all three REVEL scores (0.173, 0.653, 0.177) must be present.
        The v1 parser would only have returned 0.173 (the first row's score).
        """
        protein = self.doc["dbnsfp"]["protein"]
        revel_scores = [
            p["revel"]["score"] for p in protein if "revel" in p
        ]
        self.assertIn(0.173, revel_scores, "REVEL 0.173 (ENST00000457723) missing")
        self.assertIn(0.653, revel_scores, "REVEL 0.653 (ENST00000611849) missing")
        self.assertIn(0.177, revel_scores, "REVEL 0.177 (ENST00000612104) missing")

    def test_revel_scores_linked_to_correct_transcripts(self):
        """Each REVEL score is paired with its originating transcript."""
        protein = self.doc["dbnsfp"]["protein"]
        revel_by_transcript = {
            p["transcriptid"]: p["revel"]["score"]
            for p in protein
            if "revel" in p and "transcriptid" in p
        }
        self.assertEqual(revel_by_transcript.get("ENST00000457723"), 0.173)
        self.assertEqual(revel_by_transcript.get("ENST00000611849"), 0.653)
        self.assertEqual(revel_by_transcript.get("ENST00000612104"), 0.177)

    def test_same_hgvs_id_across_all_rows(self):
        """All transcript rows must produce the same HGVS ID (same genomic position)."""
        for row_fn in [_ROW_T1, _ROW_T2, _ROW_T3]:
            doc = construct_hg38_doc(row_fn())
            self.assertEqual(doc["_id"], "chrX:g.153693944C>A")


# ---------------------------------------------------------------------------
# Tests: regression — v1 behaviour comparison
# ---------------------------------------------------------------------------

class TestV2RegressionVsV1(unittest.TestCase):
    """
    Confirm that the v2 merge logic does not repeat the v1 mistake of
    discarding REVEL scores from transcript rows 2 and beyond.
    """

    def test_second_transcript_revel_not_discarded(self):
        """
        v1 only extended the `aa` field when merging same-ID rows; everything
        else from row 2 was lost.  v2 must preserve REVEL from row 2.
        """
        doc = _merge_docs_hg38([_ROW_T1(), _ROW_T2()])
        protein = doc["dbnsfp"]["protein"]

        # v1 would produce a single dict here (not a list); v2 must produce a list
        self.assertIsInstance(protein, list,
            "v2 must not collapse multi-transcript protein to a single dict")

        revel_scores = [p["revel"]["score"] for p in protein if "revel" in p]
        self.assertIn(0.653, revel_scores,
            "REVEL score 0.653 from the second transcript row must not be discarded")

    def test_first_transcript_revel_still_present(self):
        """The first-row REVEL score must still be present after merging."""
        doc = _merge_docs_hg38([_ROW_T1(), _ROW_T2(), _ROW_T3()])
        protein = doc["dbnsfp"]["protein"]
        revel_scores = [p["revel"]["score"] for p in protein if "revel" in p]
        self.assertIn(0.173, revel_scores)


if __name__ == "__main__":
    unittest.main()
