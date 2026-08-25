"""
Unit tests for the 'uniprot' myvariant.info source parser.

Background: humsavar.txt (manually curated missense variants) has no genomic
coordinate of its own -- only a dbSNP id -- so it's enriched by looking up
that dbSNP id in the much larger homo_sapiens_variation.txt.gz variant index,
which does carry a genomic coordinate. Per-source decisions this parser
implements (see conversation / commit history for the "why"):

  1. humsavar.txt drives which variants are produced; it's enriched with
     whatever homo_sapiens_variation.txt.gz reports at the matched genomic
     position -- including rs (dbSNP), RCV (ClinVar) or any other source,
     not just the one dbSNP id used to find that position.
  2. humsavar.txt's variant-category vocabulary (now ACMG/AMP-style: LP/P,
     LB/B, US) is stored as-is, not translated to the old Disease/
     Polymorphism/Unclassified scheme.
  3. No new fields (e.g. Evidence, Consequence Type) are added to the
     existing mapping -- only source_db_id, clinical_significance,
     phenotype_disease, phenotype_disease_source and the humsavar.* fields.
"""
import os
import sys
import unittest

# Ensure src/ is on the path so hub modules are importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import importlib.util

# Load the parser directly to avoid triggering biothings hub initialisation
# (which requires a running config) via the uniprot __init__.py.
_PARSER_PATH = os.path.join(
    os.path.dirname(__file__),
    "..", "..", "hub", "dataload", "sources", "uniprot", "uniprot_parser.py"
)
_spec = importlib.util.spec_from_file_location("uniprot_parser", _PARSER_PATH)
up = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(up)


# ---------------------------------------------------------------------------
# nc_coordinate_to_hgvs_id
# ---------------------------------------------------------------------------

class TestNcCoordinateToHgvsId(unittest.TestCase):

    def test_autosome(self):
        self.assertEqual(
            up.nc_coordinate_to_hgvs_id("NC_000017.11:g.30178149A>G"),
            "chr17:g.30178149A>G")

    def test_chr1(self):
        self.assertEqual(
            up.nc_coordinate_to_hgvs_id("NC_000001.11:g.12345C>T"),
            "chr1:g.12345C>T")

    def test_chrX(self):
        self.assertEqual(
            up.nc_coordinate_to_hgvs_id("NC_000023.11:g.99A>T"),
            "chrX:g.99A>T")

    def test_chrY(self):
        self.assertEqual(
            up.nc_coordinate_to_hgvs_id("NC_000024.10:g.99A>T"),
            "chrY:g.99A>T")

    def test_mitochondrial(self):
        self.assertEqual(
            up.nc_coordinate_to_hgvs_id("NC_012920.1:g.1234A>G"),
            "chrMT:g.1234A>G")

    def test_assembly_patch_version_is_ignored(self):
        """Only the accession prefix (before the dot) determines the chromosome,
        so this is robust to GRCh38 patch version bumps."""
        self.assertEqual(
            up.nc_coordinate_to_hgvs_id("NC_000017.12:g.1A>G"),
            "chr17:g.1A>G")

    def test_unrecognized_accession_returns_none(self):
        self.assertIsNone(up.nc_coordinate_to_hgvs_id("NC_999999.1:g.1A>G"))

    def test_malformed_coordinate_returns_none(self):
        self.assertIsNone(up.nc_coordinate_to_hgvs_id("garbage"))


# ---------------------------------------------------------------------------
# parse_humsavar
# ---------------------------------------------------------------------------

_HUMSAVAR_PREAMBLE = [
    "Description: Index of human variants curated from literature reports\n",
    "\n",
    "Main        Swiss-Prot             AA             Variant\n",
    "gene name   AC         FTId        change         category dbSNP          Disease name\n",
    "_________   __________ ___________ ______________ ________ ______________ _____________________\n",
]


class TestParseHumsavar(unittest.TestCase):

    def test_skips_preamble(self):
        rows = list(up.parse_humsavar(_HUMSAVAR_PREAMBLE))
        self.assertEqual(rows, [])

    def test_parses_basic_row(self):
        lines = _HUMSAVAR_PREAMBLE + [
            "A1BG        P04217     VAR_018369  p.His52Arg     LB/B     rs893184       -\n",
        ]
        rows = list(up.parse_humsavar(lines))
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["swiss_prot_ac"], "P04217")
        self.assertEqual(row["ftid"], "VAR_018369")
        self.assertEqual(row["type_of_variant"], "LB/B")
        self.assertEqual(row["dbsnp_id"], "rs893184")
        self.assertIsNone(row["disease_name"])

    def test_new_acmg_vocabulary_kept_as_is(self):
        """Decision 2: the current LP/P/LB/B/US vocabulary is not translated."""
        lines = _HUMSAVAR_PREAMBLE + [
            "AAAS        Q9NRG9     VAR_012804  p.Gln15Lys     LP/P     rs121918549    "
            "Achalasia-addisonianism-alacrima syndrome (AAAS) [MIM:231550]\n",
        ]
        row = next(iter(up.parse_humsavar(lines)))
        self.assertEqual(row["type_of_variant"], "LP/P")
        self.assertEqual(
            row["disease_name"],
            "Achalasia-addisonianism-alacrima syndrome (AAAS) [MIM:231550]")

    def test_missing_dbsnp_id_is_none(self):
        lines = _HUMSAVAR_PREAMBLE + [
            "AARS1       P49588     VAR_073293  p.Thr608Met    US       -              -\n",
        ]
        row = next(iter(up.parse_humsavar(lines)))
        self.assertIsNone(row["dbsnp_id"])
        self.assertIsNone(row["disease_name"])

    def test_blank_lines_are_skipped(self):
        lines = _HUMSAVAR_PREAMBLE + [
            "\n",
            "A1BG        P04217     VAR_018369  p.His52Arg     LB/B     rs893184       -\n",
            "\n",
        ]
        rows = list(up.parse_humsavar(lines))
        self.assertEqual(len(rows), 1)


# ---------------------------------------------------------------------------
# parse_variation
# ---------------------------------------------------------------------------

_VARIATION_PREAMBLE = [
    "Description:     Index of Protein Altering Variants (SO:0001818)\n",
    "\n",
    "######## VARIANT INDEX ########\n",
    "Gene Name\tAC\tVariant AA Change\tSource DB ID\tConsequence Type\t"
    "Clinical Significance\tPhenotype/Disease\tPhenotype/Disease Source\t"
    "Cytogenetic Band\tChromosome Coordinate\tEnsembl gene ID\t"
    "Ensembl transcript ID\tEnsembl translation ID\tEvidence\n",
    "___________\t___________\t____________________\t________________\t"
    "________________________\t______________________\t"
    "________________________________________\t__________________________\t"
    "__________________\t______________________\t________________________________\t"
    "________________________________\t________________________________\t"
    "________________________________\n",
]


def _variation_row(source_db_id, coordinate, clinsig="-", pheno="-", pheno_src="-",
                    gene="NSRP1", ac="A0A024QZ33", aa="p.Lys30Glu"):
    return "\t".join([
        gene, ac, aa, source_db_id, "missense variant", clinsig, pheno, pheno_src,
        "17q11.2", coordinate, "ENSG00000126653", "ENST00000612959",
        "ENSP00000477862", "TOPMed,gnomAD",
    ]) + "\n"


class TestParseVariation(unittest.TestCase):

    def test_skips_preamble(self):
        rows = list(up.parse_variation(_VARIATION_PREAMBLE))
        self.assertEqual(rows, [])

    def test_parses_basic_row(self):
        lines = _VARIATION_PREAMBLE + [
            _variation_row("rs965203080", "NC_000017.11:g.30172593A>G"),
        ]
        rows = list(up.parse_variation(lines))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["source_db_id"], "rs965203080")
        self.assertEqual(rows[0]["coordinate"], "NC_000017.11:g.30172593A>G")

    def test_short_malformed_row_is_skipped(self):
        lines = _VARIATION_PREAMBLE + ["too\tshort\n"]
        rows = list(up.parse_variation(lines))
        self.assertEqual(rows, [])


# ---------------------------------------------------------------------------
# build_variation_index
# ---------------------------------------------------------------------------

class TestBuildVariationIndex(unittest.TestCase):
    """
    Grounded in a real record found in UniProt's current release: the NSRP1
    variant p.Lys30Glu (chr17:g.30178149A>G) is reported by three different
    sources at the exact same genomic coordinate: rs143842750 (dbSNP),
    RCV004292335 and RCV004545615 (ClinVar) -- exactly the "rs and RCV and any
    other one" case Decision 1 calls for.
    """

    def setUp(self):
        self.rows = [
            {"source_db_id": "rs143842750", "coordinate": "NC_000017.11:g.30178149A>G",
             "clinical_significance": "-", "phenotype_disease": "-", "phenotype_disease_source": "-"},
            {"source_db_id": "RCV004292335", "coordinate": "NC_000017.11:g.30178149A>G",
             "clinical_significance": "-", "phenotype_disease": "-", "phenotype_disease_source": "-"},
            {"source_db_id": "RCV004545615", "coordinate": "NC_000017.11:g.30178149A>G",
             "clinical_significance": "Likely benign", "phenotype_disease": "NSRP1-related disorder",
             "phenotype_disease_source": "RCV004545615"},
            # unrelated variant elsewhere in the file -- must never leak into the index
            {"source_db_id": "rs000000001", "coordinate": "NC_000001.11:g.111A>G",
             "clinical_significance": "-", "phenotype_disease": "-", "phenotype_disease_source": "-"},
        ]

    def _factory(self):
        return lambda: iter(self.rows)

    def test_resolves_needed_dbsnp_id_to_coordinate(self):
        dbsnp_to_coord, _ = up.build_variation_index(self._factory(), {"rs143842750"})
        self.assertEqual(dbsnp_to_coord["rs143842750"], "NC_000017.11:g.30178149A>G")

    def test_unneeded_dbsnp_id_not_resolved(self):
        dbsnp_to_coord, _ = up.build_variation_index(self._factory(), {"rs143842750"})
        self.assertNotIn("rs000000001", dbsnp_to_coord)

    def test_unknown_dbsnp_id_absent_from_result(self):
        dbsnp_to_coord, _ = up.build_variation_index(self._factory(), {"rs_not_in_file"})
        self.assertNotIn("rs_not_in_file", dbsnp_to_coord)

    def test_aggregates_all_source_db_ids_sharing_the_coordinate(self):
        """Decision 1: include rs, RCV, and any other source_db_id at that position."""
        _, coord_info = up.build_variation_index(self._factory(), {"rs143842750"})
        info = coord_info["NC_000017.11:g.30178149A>G"]
        self.assertEqual(info["source_db_id"],
                          {"rs143842750", "RCV004292335", "RCV004545615"})

    def test_aggregates_clinical_and_phenotype_fields(self):
        _, coord_info = up.build_variation_index(self._factory(), {"rs143842750"})
        info = coord_info["NC_000017.11:g.30178149A>G"]
        self.assertEqual(info["clinical_significance"], {"Likely benign"})
        self.assertEqual(info["phenotype_disease"], {"NSRP1-related disorder"})
        self.assertEqual(info["phenotype_disease_source"], {"RCV004545615"})

    def test_placeholder_dash_values_are_excluded(self):
        """Most rows are '-' for these fields; they must not pollute the aggregate."""
        _, coord_info = up.build_variation_index(self._factory(), {"rs143842750"})
        info = coord_info["NC_000017.11:g.30178149A>G"]
        self.assertNotIn("-", info["clinical_significance"])
        self.assertNotIn("-", info["phenotype_disease"])
        self.assertNotIn("-", info["phenotype_disease_source"])

    def test_unrelated_coordinate_not_collected(self):
        _, coord_info = up.build_variation_index(self._factory(), {"rs143842750"})
        self.assertNotIn("NC_000001.11:g.111A>G", coord_info)


# ---------------------------------------------------------------------------
# build_docs
# ---------------------------------------------------------------------------

class TestBuildDocs(unittest.TestCase):

    def test_row_without_dbsnp_id_is_skipped(self):
        humsavar_rows = [{
            "swiss_prot_ac": "P00000", "ftid": "VAR_000001", "type_of_variant": "US",
            "dbsnp_id": None, "disease_name": None,
        }]
        docs = list(up.build_docs(humsavar_rows, {}, {}))
        self.assertEqual(docs, [])

    def test_unresolved_dbsnp_id_is_skipped(self):
        humsavar_rows = [{
            "swiss_prot_ac": "P00000", "ftid": "VAR_000001", "type_of_variant": "US",
            "dbsnp_id": "rs_unresolved", "disease_name": None,
        }]
        docs = list(up.build_docs(humsavar_rows, {}, {}))
        self.assertEqual(docs, [])

    def test_resolved_row_produces_expected_doc(self):
        humsavar_rows = [{
            "swiss_prot_ac": "P04217", "ftid": "VAR_018369", "type_of_variant": "LB/B",
            "dbsnp_id": "rs893184", "disease_name": None,
        }]
        dbsnp_to_coord = {"rs893184": "NC_000019.10:g.58864491G>A"}
        coord_info = {"NC_000019.10:g.58864491G>A": {
            "source_db_id": {"rs893184"},
            "clinical_significance": set(),
            "phenotype_disease": set(),
            "phenotype_disease_source": set(),
        }}
        docs = list(up.build_docs(humsavar_rows, dbsnp_to_coord, coord_info))
        self.assertEqual(len(docs), 1)
        doc = docs[0]
        self.assertEqual(doc["_id"], "chr19:g.58864491G>A")
        self.assertEqual(doc["uniprot"]["humsavar"], {
            "swiss_prot_ac": "P04217", "ftid": "VAR_018369", "type_of_variant": "LB/B",
        })
        # single value -> unlist() collapses it to a scalar, matching prod's shape
        self.assertEqual(doc["uniprot"]["source_db_id"], "rs893184")

    def test_multi_valued_source_db_id_stays_a_sorted_list(self):
        """Mirrors the real NSRP1 p.Lys30Glu case: rs + 2 RCV ids at one position."""
        humsavar_rows = [{
            "swiss_prot_ac": "A0A024QZ33", "ftid": "VAR_999999", "type_of_variant": "LB/B",
            "dbsnp_id": "rs143842750", "disease_name": None,
        }]
        dbsnp_to_coord = {"rs143842750": "NC_000017.11:g.30178149A>G"}
        coord_info = {"NC_000017.11:g.30178149A>G": {
            "source_db_id": {"rs143842750", "RCV004292335", "RCV004545615"},
            "clinical_significance": {"Likely benign"},
            "phenotype_disease": {"NSRP1-related disorder"},
            "phenotype_disease_source": {"RCV004545615"},
        }}
        doc = next(iter(up.build_docs(humsavar_rows, dbsnp_to_coord, coord_info)))
        self.assertEqual(doc["_id"], "chr17:g.30178149A>G")
        self.assertEqual(sorted(doc["uniprot"]["source_db_id"]),
                          ["RCV004292335", "RCV004545615", "rs143842750"])
        self.assertEqual(doc["uniprot"]["clinical_significance"], "Likely benign")

    def test_no_extra_fields_beyond_existing_mapping(self):
        """Decision 3: no Evidence/Consequence Type/etc. fields are ever added."""
        humsavar_rows = [{
            "swiss_prot_ac": "P04217", "ftid": "VAR_018369", "type_of_variant": "LB/B",
            "dbsnp_id": "rs893184", "disease_name": "Some disease",
        }]
        dbsnp_to_coord = {"rs893184": "NC_000019.10:g.58864491G>A"}
        coord_info = {"NC_000019.10:g.58864491G>A": {
            "source_db_id": {"rs893184"},
            "clinical_significance": {"Pathogenic"},
            "phenotype_disease": {"Some phenotype"},
            "phenotype_disease_source": {"MIM:12345"},
        }}
        doc = next(iter(up.build_docs(humsavar_rows, dbsnp_to_coord, coord_info)))
        self.assertEqual(set(doc["uniprot"].keys()), {
            "humsavar", "source_db_id", "clinical_significance",
            "phenotype_disease", "phenotype_disease_source",
        })
        self.assertEqual(set(doc["uniprot"]["humsavar"].keys()), {
            "swiss_prot_ac", "ftid", "type_of_variant", "disease_name",
        })


# ---------------------------------------------------------------------------
# merge_docs
# ---------------------------------------------------------------------------

class TestMergeDocs(unittest.TestCase):
    """
    Regression test for a real production crash: two distinct humsavar.txt
    records for ABCA1 (VAR_009147 p.Trp590Ser and VAR_062487 p.Trp590Leu) both
    reference the same dbSNP id, rs137854496 -- a UniProt curation duplicate
    that was never cleaned up. Both resolve to the same genomic coordinate
    (chr9:g.104831048C>G), so build_docs() yields two documents with the same
    _id. Storage does a plain insert (not upsert), so without merging this
    crashes the whole batch with a MongoDB E11000 duplicate key error.
    """

    def setUp(self):
        self.doc_a = {
            "_id": "chr9:g.104831048C>G",
            "uniprot": {
                "humsavar": {"swiss_prot_ac": "O95477", "ftid": "VAR_009147",
                             "type_of_variant": "LP/P",
                             "disease_name": "Tangier disease (TGD) [MIM:205400]"},
                "source_db_id": "rs137854496",
            },
        }
        self.doc_b = {
            "_id": "chr9:g.104831048C>G",
            "uniprot": {
                "humsavar": {"swiss_prot_ac": "O95477", "ftid": "VAR_062487",
                             "type_of_variant": "LP/P",
                             "disease_name": "Tangier disease (TGD) [MIM:205400]"},
                "source_db_id": ["RCV000010098", "RCV001509362", "rs137854496"],
                "clinical_significance": "Variant of uncertain significance, Likely pathogenic, Pathogenic",
                "phenotype_disease": ["Tangier disease (TGD)", "Tangier disease (tgd)"],
                "phenotype_disease_source": "MIM:205400, 31751110, RCV000010098",
            },
        }

    def test_non_colliding_docs_pass_through_unchanged(self):
        other = {"_id": "chr1:g.1A>G", "uniprot": {"humsavar": {"ftid": "VAR_1"}}}
        docs = list(up.merge_docs([self.doc_a, other]))
        self.assertEqual(len(docs), 2)
        self.assertIn(other, docs)

    def test_colliding_docs_produce_a_single_document(self):
        docs = list(up.merge_docs([self.doc_a, self.doc_b]))
        self.assertEqual(len(docs), 1, "must not crash storage with two docs sharing an _id")
        self.assertEqual(docs[0]["_id"], "chr9:g.104831048C>G")

    def test_humsavar_becomes_a_list_of_both_records(self):
        merged = next(iter(up.merge_docs([self.doc_a, self.doc_b])))
        humsavar = merged["uniprot"]["humsavar"]
        self.assertIsInstance(humsavar, list)
        self.assertEqual({h["ftid"] for h in humsavar}, {"VAR_009147", "VAR_062487"})

    def test_source_db_id_unioned_across_scalar_and_list_values(self):
        """doc_a has a scalar source_db_id, doc_b has a list -- both must merge cleanly."""
        merged = next(iter(up.merge_docs([self.doc_a, self.doc_b])))
        self.assertEqual(sorted(merged["uniprot"]["source_db_id"]),
                          ["RCV000010098", "RCV001509362", "rs137854496"])

    def test_enrichment_fields_from_either_doc_are_preserved(self):
        merged = next(iter(up.merge_docs([self.doc_a, self.doc_b])))
        self.assertEqual(merged["uniprot"]["clinical_significance"],
                          "Variant of uncertain significance, Likely pathogenic, Pathogenic")
        self.assertEqual(sorted(merged["uniprot"]["phenotype_disease"]),
                          ["Tangier disease (TGD)", "Tangier disease (tgd)"])

    def test_single_doc_group_is_not_wrapped_in_extra_list(self):
        """The overwhelmingly common case (no collision) must keep humsavar as a plain dict."""
        docs = list(up.merge_docs([self.doc_a]))
        self.assertEqual(len(docs), 1)
        self.assertIsInstance(docs[0]["uniprot"]["humsavar"], dict)


# ---------------------------------------------------------------------------
# load_data (integration)
# ---------------------------------------------------------------------------

class TestLoadDataIntegration(unittest.TestCase):

    def setUp(self):
        import tempfile
        import gzip

        self.tmpdir = tempfile.mkdtemp()

        with open(os.path.join(self.tmpdir, up.HUMSAVAR_FILE), "w") as f:
            f.writelines(_HUMSAVAR_PREAMBLE)
            # resolvable row (matches a variation-file row below)
            f.write("A1BG        P04217     VAR_018369  p.His52Arg     LB/B     rs893184       -\n")
            # unresolvable row: no matching entry in the variation file
            f.write("A1BG        P04217     VAR_018370  p.His395Arg    LB/B     rs2241788      -\n")
            # unresolvable row: no dbSNP id at all
            f.write("AARS1       P49588     VAR_073293  p.Thr608Met    US       -              -\n")
            # regression case: two distinct humsavar records sharing one dbSNP id
            # (real production case: ABCA1 VAR_009147/VAR_062487 both rs137854496)
            f.write("ABCA1       O95477     VAR_009147  p.Trp590Ser    LP/P     rs137854496    "
                    "Tangier disease (TGD) [MIM:205400]\n")
            f.write("ABCA1       O95477     VAR_062487  p.Trp590Leu    LP/P     rs137854496    "
                    "Tangier disease (TGD) [MIM:205400]\n")

        variation_path = os.path.join(self.tmpdir, "homo_sapiens_variation.txt.gz")
        with gzip.open(variation_path, "wt") as f:
            f.writelines(_VARIATION_PREAMBLE)
            f.write(_variation_row("rs893184", "NC_000019.10:g.58864491G>A",
                                    gene="A1BG", aa="p.His52Arg"))
            # a second source at that same position, to exercise aggregation end-to-end
            f.write(_variation_row("RCV000012345", "NC_000019.10:g.58864491G>A",
                                    clinsig="Benign", gene="A1BG", aa="p.His52Arg"))
            f.write(_variation_row("rs137854496", "NC_000009.12:g.104831048C>G",
                                    clinsig="Pathogenic", gene="ABCA1", ac="O95477", aa="p.Trp590Ser"))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_end_to_end(self):
        docs = up.load_data(self.tmpdir)
        # 2 resolvable groups: the A1BG row, and the merged ABCA1 pair (the 2
        # unresolvable/no-dbSNP-id rows are skipped, not 4 separate documents)
        self.assertEqual(len(docs), 2)
        by_id = {d["_id"]: d for d in docs}

        doc = by_id["chr19:g.58864491G>A"]
        self.assertEqual(sorted(doc["uniprot"]["source_db_id"]),
                          ["RCV000012345", "rs893184"])
        self.assertEqual(doc["uniprot"]["clinical_significance"], "Benign")
        self.assertEqual(doc["uniprot"]["humsavar"]["swiss_prot_ac"], "P04217")

    def test_end_to_end_merges_duplicate_dbsnp_id_across_humsavar_records(self):
        """
        Regression test for the production crash: without merge_docs(), this
        scenario yields two raw documents with _id 'chr9:g.104831048C>G' and
        crashes storage.process()'s plain insert_many() with E11000. Here it
        must produce exactly one merged document instead.
        """
        docs = up.load_data(self.tmpdir)
        by_id = {d["_id"]: d for d in docs}
        self.assertIn("chr9:g.104831048C>G", by_id)
        merged = by_id["chr9:g.104831048C>G"]
        humsavar = merged["uniprot"]["humsavar"]
        self.assertIsInstance(humsavar, list)
        self.assertEqual({h["ftid"] for h in humsavar}, {"VAR_009147", "VAR_062487"})
        self.assertEqual(merged["uniprot"]["source_db_id"], "rs137854496")
        self.assertEqual(merged["uniprot"]["clinical_significance"], "Pathogenic")

    def test_missing_variation_file_raises(self):
        import tempfile
        empty_dir = tempfile.mkdtemp()
        try:
            with open(os.path.join(empty_dir, up.HUMSAVAR_FILE), "w") as f:
                f.writelines(_HUMSAVAR_PREAMBLE)
            with self.assertRaises(AssertionError):
                up.load_data(empty_dir)
        finally:
            import shutil
            shutil.rmtree(empty_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
