"""
Unit tests for the dbNSFP 5.4a parser (v1 and v2).

Scope, relative to the previously-implemented 5.3.1a parser (see
test_dbnsfp_parser_531a.py, which remains as-is and still passes against the
531a parser - none of its assertions changed underneath it):

  - VALID_COLUMN_NO (508), matching the real dbNSFP 5.4a variant file
    (505 in 5.3.1a + 3 new GPN-MSA columns).
  - GPN-MSA: 3 new columns (GPN_MSA_score, GPN_MSA_converted_rankscore,
    GPN_MSA_pred), new in dbNSFP 5.4. Not per-transcript (same category as
    ESM1b/AlphaMissense/popEVE), so v2 keeps it top-level, not under "protein".
  - Ensembl_canonical: renamed from VEP_canonical in dbNSFP 5.4 (same meaning -
    canonical transcript designation, provided by Gencode/Ensembl). v1 keeps
    it top-level (dest "ensembl_canonical"); v2 keeps it per-transcript, under
    "protein" (dest "protein.ensembl_canonical"), same placement VEP_canonical
    had.
  - Everything else carried over unchanged from 5.3.1a: hs1 handling, the
    fields added/renamed across 5.0-5.3.1 (MANE, MutationTaster2021, MutPred2,
    MisFit, GERP_92_mammals, ESM1b_converted_rankscore, dbNSFP_POPMAX,
    popEVE), and the issue #179 multi-transcript merge divergence between v1
    and v2.
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


V1 = _load_parser("dbnsfp_parser_54a_v1.py", "dbnsfp_parser_54a_v1")
V2 = _load_parser("dbnsfp_parser_54a_v2.py", "dbnsfp_parser_54a_v2")


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
    """508 is the real column count of the dbNSFP5.4a_variant.chr<#> files (505 + 3 GPN-MSA)."""

    def test_v1_column_count(self):
        self.assertEqual(V1.VALID_COLUMN_NO, 508)

    def test_v2_column_count(self):
        self.assertEqual(V2.VALID_COLUMN_NO, 508)


# ---------------------------------------------------------------------------
# GPN-MSA (new in dbNSFP 5.4)
# ---------------------------------------------------------------------------

class TestGpnMsa(unittest.TestCase):

    def test_v1_gpn_msa(self):
        row = _base_row(V1)
        row.update({"GPN_MSA_score": "-8.5", "GPN_MSA_converted_rankscore": "0.9", "GPN_MSA_pred": "D"})
        doc = V1.construct_hg38_doc(row)
        self.assertEqual(doc["dbnsfp"]["gpn_msa"], {"score": -8.5, "converted_rankscore": 0.9, "pred": "D"})

    def test_v2_gpn_msa_is_not_per_transcript(self):
        """Unlike SIFT/REVEL/etc., GPN-MSA isn't tied to a specific transcript, so it
        stays top-level in v2 rather than nested under the per-transcript 'protein' list."""
        row = _base_row(V2)
        row.update({
            "GPN_MSA_score": "-8.5", "GPN_MSA_converted_rankscore": "0.9", "GPN_MSA_pred": "D",
            "Ensembl_transcriptid": "ENST00000001",
        })
        doc = V2.construct_hg38_doc(row)
        self.assertEqual(doc["dbnsfp"]["gpn_msa"], {"score": -8.5, "converted_rankscore": 0.9, "pred": "D"})
        protein = doc["dbnsfp"]["protein"]
        protein = protein if isinstance(protein, list) else [protein]
        for entry in protein:
            self.assertNotIn("gpn_msa", entry)

    def test_missing_gpn_msa_is_simply_absent(self):
        for mod in (V1, V2):
            row = _base_row(mod)
            doc = mod.construct_hg38_doc(row)
            self.assertNotIn("gpn_msa", doc["dbnsfp"])


# ---------------------------------------------------------------------------
# Ensembl_canonical (renamed from VEP_canonical in dbNSFP 5.4)
# ---------------------------------------------------------------------------

class TestEnsemblCanonical(unittest.TestCase):

    def test_vep_canonical_is_gone(self):
        for mod in (V1, V2):
            self.assertNotIn("VEP_canonical", {c.name for c in mod.COLUMNS})
            self.assertIn("Ensembl_canonical", {c.name for c in mod.COLUMNS})

    def test_v1_ensembl_canonical(self):
        row = _base_row(V1)
        row["Ensembl_canonical"] = "1"
        doc = V1.construct_hg38_doc(row)
        self.assertEqual(doc["dbnsfp"]["ensembl_canonical"], "1")

    def test_v2_ensembl_canonical_is_per_transcript(self):
        """Same placement VEP_canonical had: per-transcript, nested under the protein list."""
        row = _base_row(V2)
        row["Ensembl_canonical"] = "1"
        row["Ensembl_transcriptid"] = "ENST00000001"
        doc = V2.construct_hg38_doc(row)
        self.assertEqual(doc["dbnsfp"]["protein"][0]["ensembl_canonical"], "1")


# ---------------------------------------------------------------------------
# Fields carried over from 5.3.1a - unaffected by the 5.4a bump, spot-checked
# here so this file alone documents 54a's actual (not just delta) behavior.
# ---------------------------------------------------------------------------

class TestFieldsCarriedOverFrom531a(unittest.TestCase):

    def test_v1_hs1_present_on_both_assemblies(self):
        row = _base_row(V1)
        row["hs1_pos(1-based)"] = "200"
        hg19_doc = V1.construct_hg19_doc(row)
        hg38_doc = V1.construct_hg38_doc(row)
        expected = {"start": 200, "end": 200}
        self.assertEqual(hg19_doc["dbnsfp"]["hs1"], expected)
        self.assertEqual(hg38_doc["dbnsfp"]["hs1"], expected)

    def test_v1_mane(self):
        row = _base_row(V1)
        row["MANE"] = "Select"
        doc = V1.construct_hg38_doc(row)
        self.assertEqual(doc["dbnsfp"]["mane"], "Select")

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

    def test_v1_gerp_92_mammals(self):
        row = _base_row(V1)
        row.update({"GERP_92_mammals": "3.5", "GERP_92_mammals_rankscore": "0.6"})
        doc = V1.construct_hg38_doc(row)
        self.assertEqual(doc["dbnsfp"]["gerp"]["92_mammals"], {"score": 3.5, "rankscore": 0.6})

    def test_v1_esm1b_converted_rankscore(self):
        row = _base_row(V1)
        row.update({"ESM1b_score": "-5.0", "ESM1b_converted_rankscore": "0.77", "ESM1b_pred": "D"})
        doc = V1.construct_hg38_doc(row)
        self.assertEqual(doc["dbnsfp"]["esm1b"]["converted_rankscore"], 0.77)

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

    def test_v2_mutationtaster_2021_model_via_analysis(self):
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
# Multi-transcript merge regression (issue #179), re-run for 5.4a
# ---------------------------------------------------------------------------

class TestMultiTranscriptRevelMergeRegression(unittest.TestCase):
    """
    Confirms the version bump to 5.4a did not change the known divergence
    between v1 and v2 when the same variant has multiple transcript rows:

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
        rows = self._two_transcript_rows(V1)
        docs = [V1.construct_hg38_doc(r) for r in rows]
        self.assertEqual(docs[0]["_id"], docs[1]["_id"])

        last_doc = docs[0]
        last_aa = [last_doc["dbnsfp"]["aa"]]
        last_aa.append(docs[1]["dbnsfp"]["aa"])
        last_doc["dbnsfp"]["aa"] = last_aa

        self.assertEqual(len(last_doc["dbnsfp"]["aa"]), 2)
        self.assertEqual(last_doc["dbnsfp"]["revel"]["score"], 0.173)

    def test_v2_preserves_revel_from_both_transcripts(self):
        rows = self._two_transcript_rows(V2)
        docs = [V2.construct_hg38_doc(r) for r in rows]
        self.assertEqual(docs[0]["_id"], docs[1]["_id"])

        merged_protein = docs[0]["dbnsfp"]["protein"] + docs[1]["dbnsfp"]["protein"]

        revel_scores = [p["revel"]["score"] for p in merged_protein if "revel" in p]
        self.assertIn(0.173, revel_scores)
        self.assertIn(0.653, revel_scores)
        self.assertEqual(len(merged_protein), 2)


if __name__ == "__main__":
    unittest.main()
