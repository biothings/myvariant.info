"""
Unit tests for the dbNSFP 5.3.1a parser (v1 and v2).

Scope, relative to the previously-implemented 4.8a/4.9a parsers:

  - the hs1 (T2T-CHM13 v2.0) coordinate fix: hs1_pos(1-based) must be captured
    on both the hg19 and hg38 documents, the same way hg18_pos(1-based) already
    is (no separate hs1 assembly pipeline exists elsewhere in the codebase, so
    hs1 is treated as an auxiliary field rather than a third document type).
    hs1_chr stays unparsed, mirroring hg18_chr.
  - fields added or renamed across dbNSFP 5.0-5.3.1: MANE, MutationTaster2021
    (AAE column retired, trees_benign/trees_deleterious added), MutPred2
    (replacing MutPred v1), MisFit, GERP_92_mammals (renamed from
    GERP_91_mammals), ESM1b_converted_rankscore (renamed from ESM1b_rankscore),
    dbNSFP_POPMAX, and popEVE.
  - VALID_COLUMN_NO (505), matching the real dbNSFP 5.3.1a variant file.
  - the issue #179 multi-transcript merge behavior (see test_dbnsfp_parser.py),
    re-run against 5.3.1a-shaped rows to confirm the version bump didn't
    change the known v1 (aa-only merge) vs. v2 (full protein-list merge)
    divergence.
"""
import os
import sys
import unittest
import importlib.util

# Ensure src/ is on the path so hub modules are importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


def _load_parser(filename, modname):
    """Load a dbnsfp parser module directly, bypassing biothings hub init."""
    path = os.path.join(
        os.path.dirname(__file__),
        "..", "..", "hub", "dataload", "sources", "dbnsfp", filename,
    )
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


V1 = _load_parser("dbnsfp_parser_531a_v1.py", "dbnsfp_parser_531a_v1")
V2 = _load_parser("dbnsfp_parser_531a_v2.py", "dbnsfp_parser_531a_v2")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _base_row(mod):
    """A row with every column NA ('.') plus a fixed, valid hg19/hg38 position."""
    row = {col.name: "." for col in mod.COLUMNS}
    row.update({
        "#chr": "1", "pos(1-based)": "100", "ref": "A", "alt": "G",
        "hg19_chr": "1", "hg19_pos(1-based)": "50",
    })
    return row


# ---------------------------------------------------------------------------
# VALID_COLUMN_NO
# ---------------------------------------------------------------------------

class TestValidColumnNumber(unittest.TestCase):
    """505 is the real column count of the dbNSFP5.3.1a_variant.chr<#> files."""

    def test_v1_column_count(self):
        self.assertEqual(V1.VALID_COLUMN_NO, 505)

    def test_v2_column_count(self):
        self.assertEqual(V2.VALID_COLUMN_NO, 505)


# ---------------------------------------------------------------------------
# hs1 (T2T-CHM13 v2.0) coordinates
# ---------------------------------------------------------------------------

class TestHs1Coordinates(unittest.TestCase):
    """hs1_pos(1-based) must be captured like hg18_pos(1-based) already is:
    present on both the hg19 and hg38 docs; hs1_chr stays unparsed."""

    def _check_present_on_both_assemblies(self, mod):
        row = _base_row(mod)
        row["hs1_pos(1-based)"] = "200"
        hg19_doc = mod.construct_hg19_doc(row)
        hg38_doc = mod.construct_hg38_doc(row)
        expected = {"start": 200, "end": 200}
        self.assertEqual(hg19_doc["dbnsfp"]["hs1"], expected)
        self.assertEqual(hg38_doc["dbnsfp"]["hs1"], expected)

    def test_v1_hs1_present_on_both_assemblies(self):
        self._check_present_on_both_assemblies(V1)

    def test_v2_hs1_present_on_both_assemblies(self):
        self._check_present_on_both_assemblies(V2)

    def test_hs1_chr_is_not_an_active_column(self):
        """hs1_chr is intentionally left unparsed, same as hg18_chr."""
        for mod in (V1, V2):
            names = {c.name for c in mod.COLUMNS}
            self.assertNotIn("hs1_chr", names)
            self.assertNotIn("hg18_chr", names)  # sanity check on the existing precedent

    def test_missing_hs1_is_simply_absent(self):
        """When hs1_pos(1-based) is NA ('.'), the doc must omit 'hs1' rather than error."""
        for mod in (V1, V2):
            row = _base_row(mod)  # hs1_pos(1-based) stays "." (NA) from _base_row
            doc = mod.construct_hg38_doc(row)
            self.assertNotIn("hs1", doc["dbnsfp"])


# ---------------------------------------------------------------------------
# Fields added or renamed between 4.9a and 5.3.1a
# ---------------------------------------------------------------------------

class TestFieldsAddedSince48a(unittest.TestCase):
    """
    Spot-checks for the score sources introduced across dbNSFP 5.0-5.3.1
    that did not exist in the previously-implemented 4.8a/4.9a parsers.
    """

    def test_v1_mane(self):
        row = _base_row(V1)
        row["MANE"] = "Select"
        doc = V1.construct_hg38_doc(row)
        self.assertEqual(doc["dbnsfp"]["mane"], "Select")

    def test_v2_mane_is_per_transcript(self):
        """In v2, MANE is per-transcript, nested under the protein list."""
        row = _base_row(V2)
        row["MANE"] = "Select"
        row["Ensembl_transcriptid"] = "ENST00000001"
        doc = V2.construct_hg38_doc(row)
        self.assertEqual(doc["dbnsfp"]["protein"][0]["mane"], "Select")

    def test_v1_mutpred2_replaces_mutpred_v1(self):
        row = _base_row(V1)
        row.update({
            "MutPred2_score": "0.8", "MutPred2_rankscore": "0.7", "MutPred2_pred": "PS",
            "MutPred2_top5_mechanisms": "Loss of helix (P = 0.0444)",
        })
        doc = V1.construct_hg38_doc(row)
        mp2 = doc["dbnsfp"]["mutpred2"]
        self.assertEqual(mp2["score"], 0.8)
        self.assertEqual(mp2["pred"], "PS")
        self.assertEqual(mp2["mechanisms"], {"mechanism": "Loss of helix", "p_val": 0.0444})
        # The old MutPred (v1) column is gone from both parsers.
        for mod in (V1, V2):
            self.assertNotIn("MutPred_score", {c.name for c in mod.COLUMNS})

    def test_v1_misfit_scores(self):
        row = _base_row(V1)
        row.update({
            "MisFit_D_score": "0.5", "MisFit_D_rankscore": "0.4",
            "MisFit_D_pred_lenient": "D", "MisFit_D_pred_stringent": "T",
            "MisFit_S_score": "0.01", "MisFit_S_rankscore": "0.3",
        })
        doc = V1.construct_hg38_doc(row)
        misfit = doc["dbnsfp"]["misfit"]
        self.assertEqual(misfit["d"], {"score": 0.5, "rankscore": 0.4, "pred_lenient": "D", "pred_stringent": "T"})
        self.assertEqual(misfit["s"], {"score": 0.01, "rankscore": 0.3})

    def test_v1_gerp_92_mammals_renamed_from_91(self):
        row = _base_row(V1)
        row.update({"GERP_92_mammals": "3.5", "GERP_92_mammals_rankscore": "0.6"})
        doc = V1.construct_hg38_doc(row)
        self.assertEqual(doc["dbnsfp"]["gerp"]["92_mammals"], {"score": 3.5, "rankscore": 0.6})
        for mod in (V1, V2):
            self.assertNotIn("GERP_91_mammals", {c.name for c in mod.COLUMNS})

    def test_v1_esm1b_converted_rankscore_renamed_from_rankscore(self):
        row = _base_row(V1)
        row.update({"ESM1b_score": "-5.0", "ESM1b_converted_rankscore": "0.77", "ESM1b_pred": "D"})
        doc = V1.construct_hg38_doc(row)
        self.assertEqual(doc["dbnsfp"]["esm1b"]["converted_rankscore"], 0.77)
        for mod in (V1, V2):
            self.assertNotIn("ESM1b_rankscore", {c.name for c in mod.COLUMNS})

    def test_v1_dbnsfp_popmax(self):
        row = _base_row(V1)
        row.update({"dbNSFP_POPMAX_AF": "0.01", "dbNSFP_POPMAX_AC": "12", "dbNSFP_POPMAX_POP": "AFR"})
        doc = V1.construct_hg38_doc(row)
        self.assertEqual(doc["dbnsfp"]["dbnsfp_popmax"], {"af": 0.01, "ac": 12, "pop": "AFR"})

    def test_v1_popeve(self):
        row = _base_row(V1)
        row.update({"popEVE_score": "-6.2", "popEVE_pred": "S", "popEVE_converted_rankscore": "0.9"})
        doc = V1.construct_hg38_doc(row)
        self.assertEqual(doc["dbnsfp"]["popeve"], {"score": -6.2, "pred": "S", "converted_rankscore": 0.9})

    def test_v1_mutationtaster_2021_model_no_aae_column(self):
        """MutationTaster_AAE is retired; trees_benign/trees_deleterious carry the 2021-model signal."""
        row = _base_row(V1)
        row.update({
            "MutationTaster_score": "1", "MutationTaster_rankscore": "0.9",
            "MutationTaster_pred": "D", "MutationTaster_model": "simple_aae",
            "MutationTaster_trees_benign": "0", "MutationTaster_trees_deleterious": "100",
        })
        doc = V1.construct_hg38_doc(row)
        mt = doc["dbnsfp"]["mutationtaster"]
        self.assertEqual(mt["trees_benign"], 0)
        self.assertEqual(mt["trees_deleterious"], 100)
        for mod in (V1, V2):
            self.assertNotIn("MutationTaster_AAE", {c.name for c in mod.COLUMNS})

    def test_v2_mutationtaster_2021_model_via_analysis(self):
        """v2 folds model/pred/score/trees_benign/trees_deleterious into mutationtaster.analysis."""
        row = _base_row(V2)
        row.update({
            "MutationTaster_score": "1", "MutationTaster_rankscore": "0.9",
            "MutationTaster_pred": "D", "MutationTaster_model": "simple_aae",
            "MutationTaster_trees_benign": "0", "MutationTaster_trees_deleterious": "100",
        })
        doc = V2.construct_hg38_doc(row)
        mt = doc["dbnsfp"]["mutationtaster"]
        self.assertEqual(mt["rankscore"], 0.9)
        self.assertEqual(mt["analysis"]["trees_benign"], 0)
        self.assertEqual(mt["analysis"]["trees_deleterious"], 100)


# ---------------------------------------------------------------------------
# Multi-transcript merge regression (issue #179), re-run for 5.3.1a
# ---------------------------------------------------------------------------

class TestMultiTranscriptRevelMergeRegression(unittest.TestCase):
    """
    Confirms the version bump to 5.3.1a did not change the known divergence
    between v1 and v2 when the same variant has multiple transcript rows
    (same chr/pos/ref/alt, different Ensembl_transcriptid / REVEL_score):

      - v1's load_file() merge only extends the `aa` field; every other
        per-transcript value (e.g. REVEL) from row 2+ is still discarded.
      - v2's load_file() merge extends the `protein` list, so every
        transcript's REVEL score is preserved.
    """

    @staticmethod
    def _two_transcript_rows(mod):
        common = {
            "#chr": "X", "pos(1-based)": "153693944", "ref": "C", "alt": "A",
            "hg19_chr": "X", "hg19_pos(1-based)": "152959399",
            "aaref": "H", "aaalt": "Q",
        }
        rows = []
        for transcriptid, revel_score in (("ENST00000457723", 0.173), ("ENST00000611849", 0.653)):
            row = _base_row(mod)
            row.update(common)
            row.update({"Ensembl_transcriptid": transcriptid, "REVEL_score": str(revel_score)})
            rows.append(row)
        return rows

    def test_v1_still_discards_revel_from_second_transcript(self):
        """Known v1 limitation (root cause of issue #179): unchanged in 5.3.1a."""
        rows = self._two_transcript_rows(V1)
        docs = [V1.construct_hg38_doc(r) for r in rows]
        self.assertEqual(docs[0]["_id"], docs[1]["_id"])  # both rows are the same variant

        # Mirror v1's load_file() merge loop: only `aa` is extended into a list.
        last_doc = docs[0]
        last_aa = [last_doc["dbnsfp"]["aa"]]
        last_aa.append(docs[1]["dbnsfp"]["aa"])
        last_doc["dbnsfp"]["aa"] = last_aa

        self.assertEqual(len(last_doc["dbnsfp"]["aa"]), 2)
        # REVEL still reflects only the first row - the original bug, still present in v1.
        self.assertEqual(last_doc["dbnsfp"]["revel"]["score"], 0.173)

    def test_v2_preserves_revel_from_both_transcripts(self):
        """The v2 fix for issue #179 still holds against 5.3.1a-shaped rows."""
        rows = self._two_transcript_rows(V2)
        docs = [V2.construct_hg38_doc(r) for r in rows]
        self.assertEqual(docs[0]["_id"], docs[1]["_id"])

        # Mirror v2's load_file() merge loop: `protein` lists are concatenated.
        merged_protein = docs[0]["dbnsfp"]["protein"] + docs[1]["dbnsfp"]["protein"]

        revel_scores = [p["revel"]["score"] for p in merged_protein if "revel" in p]
        self.assertIn(0.173, revel_scores)
        self.assertIn(0.653, revel_scores)
        self.assertEqual(len(merged_protein), 2)


if __name__ == "__main__":
    unittest.main()
