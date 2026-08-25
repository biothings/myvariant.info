"""
Unit tests for the 'uniprot' myvariant.info source parser.

Architecture (per direct decision from the source owner, overriding an
earlier humsavar-driven design): homo_sapiens_variation.txt.gz is the base --
every unique genomic coordinate found there becomes one output document,
enriched with whatever source_db_id/clinical_significance/phenotype_disease/
phenotype_disease_source values UniProt reports at that position. humsavar.txt
(~85K manually curated records, vs. ~15M coordinates in the base file) is
attached on top, only when available: a document gets a 'humsavar' field only
if one of its source_db_id values matches a dbSNP id humsavar.txt references.
Most documents won't have one.

Other standing decisions this parser implements:
  - humsavar.txt's variant-category vocabulary (now ACMG/AMP-style: LP/P,
    LB/B, US) is stored as-is, not translated to the old Disease/
    Polymorphism/Unclassified scheme.
  - No new fields (e.g. Evidence, Consequence Type) are added to the
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
        """Standing decision: the current LP/P/LB/B/US vocabulary is not translated."""
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
# build_variation_aggregate
# ---------------------------------------------------------------------------

class TestBuildVariationAggregate(unittest.TestCase):
    """
    Grounded in a real record found in UniProt's current release: the NSRP1
    variant p.Lys30Glu (chr17:g.30178149A>G) is reported by three different
    sources at the exact same genomic coordinate: rs143842750 (dbSNP),
    RCV004292335 and RCV004545615 (ClinVar).
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
            # a wholly unrelated coordinate, to prove aggregation doesn't cross-contaminate
            "SENTINEL",
        ]
        self.rows[-1] = {"source_db_id": "rs000000001", "coordinate": "NC_000001.11:g.111A>G",
                          "clinical_significance": "-", "phenotype_disease": "-", "phenotype_disease_source": "-"}

    def test_every_coordinate_becomes_a_key(self):
        """Unlike the old humsavar-driven design, ALL coordinates are aggregated,
        not just a pre-selected subset -- this is the base file now."""
        coordinate_info = up.build_variation_aggregate(self.rows)
        self.assertEqual(set(coordinate_info.keys()), {
            "NC_000017.11:g.30178149A>G", "NC_000001.11:g.111A>G",
        })

    def test_aggregates_all_source_db_ids_sharing_a_coordinate(self):
        coordinate_info = up.build_variation_aggregate(self.rows)
        info = coordinate_info["NC_000017.11:g.30178149A>G"]
        self.assertEqual(info["source_db_id"],
                          {"rs143842750", "RCV004292335", "RCV004545615"})

    def test_aggregates_clinical_and_phenotype_fields(self):
        coordinate_info = up.build_variation_aggregate(self.rows)
        info = coordinate_info["NC_000017.11:g.30178149A>G"]
        self.assertEqual(info["clinical_significance"], {"Likely benign"})
        self.assertEqual(info["phenotype_disease"], {"NSRP1-related disorder"})
        self.assertEqual(info["phenotype_disease_source"], {"RCV004545615"})

    def test_placeholder_dash_values_are_excluded(self):
        coordinate_info = up.build_variation_aggregate(self.rows)
        info = coordinate_info["NC_000017.11:g.30178149A>G"]
        self.assertNotIn("-", info["clinical_significance"])
        self.assertNotIn("-", info["phenotype_disease"])
        self.assertNotIn("-", info["phenotype_disease_source"])

    def test_unrelated_coordinate_has_its_own_isolated_entry(self):
        coordinate_info = up.build_variation_aggregate(self.rows)
        info = coordinate_info["NC_000001.11:g.111A>G"]
        self.assertEqual(info["source_db_id"], {"rs000000001"})
        self.assertEqual(info["clinical_significance"], set())


# ---------------------------------------------------------------------------
# build_humsavar_index
# ---------------------------------------------------------------------------

class TestBuildHumsavarIndex(unittest.TestCase):

    def test_indexes_by_dbsnp_id(self):
        rows = [{"swiss_prot_ac": "P04217", "ftid": "VAR_018369", "type_of_variant": "LB/B",
                 "dbsnp_id": "rs893184", "disease_name": None}]
        index = up.build_humsavar_index(rows)
        self.assertIn("rs893184", index)
        self.assertEqual(index["rs893184"][0]["ftid"], "VAR_018369")

    def test_rows_without_dbsnp_id_are_excluded(self):
        rows = [{"swiss_prot_ac": "P00000", "ftid": "VAR_000001", "type_of_variant": "US",
                 "dbsnp_id": None, "disease_name": None}]
        index = up.build_humsavar_index(rows)
        self.assertEqual(index, {})

    def test_duplicate_dbsnp_id_across_records_both_kept(self):
        """Real production case: ABCA1's VAR_009147 and VAR_062487 both cite rs137854496."""
        rows = [
            {"swiss_prot_ac": "O95477", "ftid": "VAR_009147", "type_of_variant": "LP/P",
             "dbsnp_id": "rs137854496", "disease_name": "Tangier disease (TGD) [MIM:205400]"},
            {"swiss_prot_ac": "O95477", "ftid": "VAR_062487", "type_of_variant": "LP/P",
             "dbsnp_id": "rs137854496", "disease_name": "Tangier disease (TGD) [MIM:205400]"},
        ]
        index = up.build_humsavar_index(rows)
        self.assertEqual(len(index["rs137854496"]), 2)
        self.assertEqual({r["ftid"] for r in index["rs137854496"]}, {"VAR_009147", "VAR_062487"})

    def test_disease_name_omitted_when_dash(self):
        rows = [{"swiss_prot_ac": "P00000", "ftid": "VAR_000001", "type_of_variant": "US",
                 "dbsnp_id": "rs1", "disease_name": None}]
        index = up.build_humsavar_index(rows)
        self.assertNotIn("disease_name", index["rs1"][0])


# ---------------------------------------------------------------------------
# build_docs
# ---------------------------------------------------------------------------

class TestBuildDocs(unittest.TestCase):

    def test_coordinate_with_no_humsavar_match_has_no_humsavar_field(self):
        """The common case now: most of the ~15M coordinates have no curated
        humsavar record at all."""
        coordinate_info = {
            "NC_000001.11:g.111A>G": {
                "source_db_id": {"rs000000001"}, "clinical_significance": set(),
                "phenotype_disease": set(), "phenotype_disease_source": set(),
            }
        }
        doc = next(iter(up.build_docs(coordinate_info, humsavar_index={})))
        self.assertEqual(doc["_id"], "chr1:g.111A>G")
        self.assertNotIn("humsavar", doc["uniprot"])
        self.assertEqual(doc["uniprot"]["source_db_id"], "rs000000001")

    def test_humsavar_attached_when_dbsnp_id_matches(self):
        coordinate_info = {
            "NC_000019.10:g.58864491G>A": {
                "source_db_id": {"rs893184"}, "clinical_significance": set(),
                "phenotype_disease": set(), "phenotype_disease_source": set(),
            }
        }
        humsavar_index = {"rs893184": [{"swiss_prot_ac": "P04217", "ftid": "VAR_018369",
                                         "type_of_variant": "LB/B"}]}
        doc = next(iter(up.build_docs(coordinate_info, humsavar_index)))
        self.assertEqual(doc["uniprot"]["humsavar"], {
            "swiss_prot_ac": "P04217", "ftid": "VAR_018369", "type_of_variant": "LB/B",
        })

    def test_unrecognized_coordinate_is_skipped(self):
        coordinate_info = {
            "NC_999999.1:g.1A>G": {
                "source_db_id": {"rsXXX"}, "clinical_significance": set(),
                "phenotype_disease": set(), "phenotype_disease_source": set(),
            }
        }
        docs = list(up.build_docs(coordinate_info, humsavar_index={}))
        self.assertEqual(docs, [])

    def test_multiple_humsavar_matches_become_a_list(self):
        """Real production case: ABCA1's two FTIds both cite rs137854496, which is
        also one of this coordinate's source_db_id values."""
        coordinate_info = {
            "NC_000009.12:g.104831048C>G": {
                "source_db_id": {"rs137854496", "RCV000010098", "RCV001509362"},
                "clinical_significance": {"Pathogenic"},
                "phenotype_disease": set(), "phenotype_disease_source": set(),
            }
        }
        humsavar_index = {
            "rs137854496": [
                {"swiss_prot_ac": "O95477", "ftid": "VAR_009147", "type_of_variant": "LP/P"},
                {"swiss_prot_ac": "O95477", "ftid": "VAR_062487", "type_of_variant": "LP/P"},
            ]
        }
        doc = next(iter(up.build_docs(coordinate_info, humsavar_index)))
        humsavar = doc["uniprot"]["humsavar"]
        self.assertIsInstance(humsavar, list)
        self.assertEqual({h["ftid"] for h in humsavar}, {"VAR_009147", "VAR_062487"})
        self.assertEqual(sorted(doc["uniprot"]["source_db_id"]),
                          ["RCV000010098", "RCV001509362", "rs137854496"])

    def test_no_extra_fields_beyond_existing_mapping(self):
        """Standing decision: no Evidence/Consequence Type/etc. fields are ever added."""
        coordinate_info = {
            "NC_000019.10:g.58864491G>A": {
                "source_db_id": {"rs893184"}, "clinical_significance": {"Pathogenic"},
                "phenotype_disease": {"Some phenotype"}, "phenotype_disease_source": {"MIM:12345"},
            }
        }
        humsavar_index = {"rs893184": [{"swiss_prot_ac": "P04217", "ftid": "VAR_018369",
                                         "type_of_variant": "LB/B", "disease_name": "Some disease"}]}
        doc = next(iter(up.build_docs(coordinate_info, humsavar_index)))
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

    def test_non_colliding_docs_pass_through_unchanged(self):
        doc_a = {"_id": "chr1:g.1A>G", "uniprot": {"source_db_id": "rs1"}}
        doc_b = {"_id": "chr2:g.2A>G", "uniprot": {"source_db_id": "rs2"}}
        docs = list(up.merge_docs([doc_a, doc_b]))
        self.assertEqual(len(docs), 2)
        self.assertIn(doc_a, docs)
        self.assertIn(doc_b, docs)

    def test_colliding_docs_merge_into_one_and_union_source_db_id(self):
        doc_a = {"_id": "chr9:g.104831048C>G", "uniprot": {"source_db_id": "rs137854496"}}
        doc_b = {"_id": "chr9:g.104831048C>G", "uniprot": {"source_db_id": ["RCV000010098", "rs137854496"]}}
        docs = list(up.merge_docs([doc_a, doc_b]))
        self.assertEqual(len(docs), 1, "must not crash storage with two docs sharing an _id")
        self.assertEqual(sorted(docs[0]["uniprot"]["source_db_id"]),
                          ["RCV000010098", "rs137854496"])

    def test_colliding_docs_union_humsavar_records(self):
        doc_a = {"_id": "chr9:g.104831048C>G",
                 "uniprot": {"humsavar": {"ftid": "VAR_009147", "swiss_prot_ac": "O95477",
                                           "type_of_variant": "LP/P"}}}
        doc_b = {"_id": "chr9:g.104831048C>G",
                 "uniprot": {"humsavar": {"ftid": "VAR_062487", "swiss_prot_ac": "O95477",
                                           "type_of_variant": "LP/P"}}}
        merged = next(iter(up.merge_docs([doc_a, doc_b])))
        humsavar = merged["uniprot"]["humsavar"]
        self.assertIsInstance(humsavar, list)
        self.assertEqual({h["ftid"] for h in humsavar}, {"VAR_009147", "VAR_062487"})

    def test_one_doc_with_humsavar_one_without_still_merges(self):
        doc_a = {"_id": "chr1:g.1A>G", "uniprot": {"source_db_id": "rs1"}}
        doc_b = {"_id": "chr1:g.1A>G",
                 "uniprot": {"source_db_id": "rs2",
                             "humsavar": {"ftid": "VAR_1", "swiss_prot_ac": "P1", "type_of_variant": "US"}}}
        merged = next(iter(up.merge_docs([doc_a, doc_b])))
        self.assertEqual(merged["uniprot"]["humsavar"], {
            "ftid": "VAR_1", "swiss_prot_ac": "P1", "type_of_variant": "US",
        })
        self.assertEqual(sorted(merged["uniprot"]["source_db_id"]), ["rs1", "rs2"])

    def test_single_doc_group_keeps_humsavar_as_a_plain_dict(self):
        doc_a = {"_id": "chr1:g.1A>G",
                 "uniprot": {"humsavar": {"ftid": "VAR_1", "swiss_prot_ac": "P1", "type_of_variant": "US"}}}
        docs = list(up.merge_docs([doc_a]))
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
            # matches a variation-file row below -> gets a humsavar field
            f.write("A1BG        P04217     VAR_018369  p.His52Arg     LB/B     rs893184       -\n")
            # dbSNP id not present anywhere in the variation file -> no effect on output
            f.write("A1BG        P04217     VAR_018370  p.His395Arg    LB/B     rs_not_in_variation_file      -\n")
            # regression case: two distinct humsavar records sharing one dbSNP id
            # (real production case: ABCA1 VAR_009147/VAR_062487 both rs137854496)
            f.write("ABCA1       O95477     VAR_009147  p.Trp590Ser    LP/P     rs137854496    "
                    "Tangier disease (TGD) [MIM:205400]\n")
            f.write("ABCA1       O95477     VAR_062487  p.Trp590Leu    LP/P     rs137854496    "
                    "Tangier disease (TGD) [MIM:205400]\n")

        variation_path = os.path.join(self.tmpdir, "homo_sapiens_variation.txt.gz")
        with gzip.open(variation_path, "wt") as f:
            f.writelines(_VARIATION_PREAMBLE)
            # this coordinate matches humsavar's rs893184
            f.write(_variation_row("rs893184", "NC_000019.10:g.58864491G>A",
                                    gene="A1BG", aa="p.His52Arg"))
            f.write(_variation_row("RCV000012345", "NC_000019.10:g.58864491G>A",
                                    clinsig="Benign", gene="A1BG", aa="p.His52Arg"))
            # this coordinate has NO humsavar match at all -- the new common case
            f.write(_variation_row("rs999999999", "NC_000002.12:g.500A>T",
                                    gene="OTHERGENE", ac="Q00000", aa="p.Ala1Val"))
            # matches humsavar's duplicate-dbSNP-id case
            f.write(_variation_row("rs137854496", "NC_000009.12:g.104831048C>G",
                                    clinsig="Pathogenic", gene="ABCA1", ac="O95477", aa="p.Trp590Ser"))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_every_variation_coordinate_produces_a_document(self):
        """The base file drives output now: all 3 coordinates in the fixture
        appear, regardless of whether humsavar has anything for them."""
        docs = up.load_data(self.tmpdir)
        self.assertEqual({d["_id"] for d in docs}, {
            "chr19:g.58864491G>A", "chr2:g.500A>T", "chr9:g.104831048C>G",
        })

    def test_coordinate_with_humsavar_match_is_enriched(self):
        docs = up.load_data(self.tmpdir)
        by_id = {d["_id"]: d for d in docs}
        doc = by_id["chr19:g.58864491G>A"]
        self.assertEqual(sorted(doc["uniprot"]["source_db_id"]),
                          ["RCV000012345", "rs893184"])
        self.assertEqual(doc["uniprot"]["clinical_significance"], "Benign")
        self.assertEqual(doc["uniprot"]["humsavar"]["swiss_prot_ac"], "P04217")

    def test_coordinate_without_humsavar_match_has_no_humsavar_field(self):
        docs = up.load_data(self.tmpdir)
        by_id = {d["_id"]: d for d in docs}
        doc = by_id["chr2:g.500A>T"]
        self.assertNotIn("humsavar", doc["uniprot"])
        self.assertEqual(doc["uniprot"]["source_db_id"], "rs999999999")

    def test_duplicate_dbsnp_id_across_humsavar_records_is_merged_not_crashed(self):
        """
        Regression test for the production crash this was originally built to
        fix: without the merge, two raw humsavar-derived records at the same
        coordinate would either duplicate the _id (old design) or, in the new
        design, both attach to the single coordinate doc and must be combined
        into one 'humsavar' list rather than raising or overwriting silently.
        """
        docs = up.load_data(self.tmpdir)
        by_id = {d["_id"]: d for d in docs}
        doc = by_id["chr9:g.104831048C>G"]
        humsavar = doc["uniprot"]["humsavar"]
        self.assertIsInstance(humsavar, list)
        self.assertEqual({h["ftid"] for h in humsavar}, {"VAR_009147", "VAR_062487"})
        self.assertEqual(doc["uniprot"]["clinical_significance"], "Pathogenic")

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
