"""
Unit tests for the 'uniprot' myvariant.info source parser.

Architecture (per direct decision from the source owner): load ALL data from
both humsavar.txt and homo_sapiens_variation.txt.gz -- every column from
both files, not just a curated subset -- connecting records that relate to
each other:

  - Every unique genomic coordinate in homo_sapiens_variation.txt.gz becomes
    a document, populated with every column UniProt reports there (gene
    name, AC, AA change, source_db_id, consequence_type,
    clinical_significance, phenotype_disease, phenotype_disease_source,
    cytogenetic_band, and the Ensembl gene/transcript/translation ids and
    evidence sources), aggregated across every row sharing the coordinate.
  - Every humsavar.txt record whose dbSNP id matches one of a coordinate's
    source_db_id values gets attached to that coordinate's document (with
    its own gene name, Swiss-Prot AC, FTId, AA change, variant category and
    disease name) -- these are the documents with data from both files.
  - Every humsavar.txt record that never matches anything (no dbSNP id, or
    a dbSNP id absent from the variation file -- about 17% of humsavar.txt)
    still becomes its own standalone document, with a random _id (no
    genomic coordinate to derive a real one from) rather than being dropped.

Other standing decisions this parser implements:
  - humsavar.txt's variant-category vocabulary (now ACMG/AMP-style: LP/P,
    LB/B, US) is stored as-is, not translated to the old Disease/
    Polymorphism/Unclassified scheme.
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
        self.assertEqual(
            up.nc_coordinate_to_hgvs_id("NC_000017.12:g.1A>G"),
            "chr17:g.1A>G")

    def test_unrecognized_accession_returns_none(self):
        self.assertIsNone(up.nc_coordinate_to_hgvs_id("NC_999999.1:g.1A>G"))

    def test_malformed_coordinate_returns_none(self):
        self.assertIsNone(up.nc_coordinate_to_hgvs_id("garbage"))


# ---------------------------------------------------------------------------
# parse_humsavar / parse_variation
# ---------------------------------------------------------------------------

_HUMSAVAR_PREAMBLE = [
    "Description: Index of human variants curated from literature reports\n",
    "\n",
    "Main        Swiss-Prot             AA             Variant\n",
    "gene name   AC         FTId        change         category dbSNP          Disease name\n",
    "_________   __________ ___________ ______________ ________ ______________ _____________________\n",
]

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
                    gene="NSRP1", ac="A0A024QZ33", aa="p.Lys30Glu",
                    consequence="missense variant", cyto="17q11.2",
                    ensg="ENSG00000126653", enst="ENST00000612959",
                    ensp="ENSP00000477862", evidence="TOPMed,gnomAD"):
    return "\t".join([
        gene, ac, aa, source_db_id, consequence, clinsig, pheno, pheno_src,
        cyto, coordinate, ensg, enst, ensp, evidence,
    ]) + "\n"


class TestParseHumsavar(unittest.TestCase):

    def test_skips_preamble(self):
        self.assertEqual(list(up.parse_humsavar(_HUMSAVAR_PREAMBLE)), [])

    def test_parses_all_columns(self):
        lines = _HUMSAVAR_PREAMBLE + [
            "A1BG        P04217     VAR_018369  p.His52Arg     LB/B     rs893184       -\n",
        ]
        row = next(iter(up.parse_humsavar(lines)))
        self.assertEqual(row["gene_name"], "A1BG")
        self.assertEqual(row["swiss_prot_ac"], "P04217")
        self.assertEqual(row["ftid"], "VAR_018369")
        self.assertEqual(row["aa_change"], "p.His52Arg")
        self.assertEqual(row["type_of_variant"], "LB/B")
        self.assertEqual(row["dbsnp_id"], "rs893184")
        self.assertIsNone(row["disease_name"])

    def test_new_acmg_vocabulary_kept_as_is(self):
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


class TestParseVariation(unittest.TestCase):

    def test_skips_preamble(self):
        self.assertEqual(list(up.parse_variation(_VARIATION_PREAMBLE)), [])

    def test_parses_all_14_columns(self):
        lines = _VARIATION_PREAMBLE + [_variation_row("rs965203080", "NC_000017.11:g.30172593A>G")]
        row = next(iter(up.parse_variation(lines)))
        self.assertEqual(row, {
            "gene_name": "NSRP1",
            "swiss_prot_ac": "A0A024QZ33",
            "aa_change": "p.Lys30Glu",
            "source_db_id": "rs965203080",
            "consequence_type": "missense variant",
            "clinical_significance": "-",
            "phenotype_disease": "-",
            "phenotype_disease_source": "-",
            "cytogenetic_band": "17q11.2",
            "coordinate": "NC_000017.11:g.30172593A>G",
            "ensembl_gene_id": "ENSG00000126653",
            "ensembl_transcript_id": "ENST00000612959",
            "ensembl_translation_id": "ENSP00000477862",
            "evidence": "TOPMed,gnomAD",
        })

    def test_short_malformed_row_is_skipped(self):
        lines = _VARIATION_PREAMBLE + ["too\tshort\n"]
        self.assertEqual(list(up.parse_variation(lines)), [])

    def test_row_with_fewer_than_14_columns_is_skipped(self):
        """The old 10-column threshold would have let a truncated row with only
        the first 10 fields through; all 14 are now required."""
        lines = _VARIATION_PREAMBLE + ["\t".join(["g", "ac", "aa", "rs1", "missense variant",
                                                   "-", "-", "-", "17q11.2", "NC_000017.11:g.1A>G"]) + "\n"]
        self.assertEqual(list(up.parse_variation(lines)), [])


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
        base = {
            "gene_name": "NSRP1", "swiss_prot_ac": "A0A024QZ33", "aa_change": "p.Lys30Glu",
            "consequence_type": "missense variant", "cytogenetic_band": "17q11.2",
            "ensembl_gene_id": "ENSG00000126653", "ensembl_transcript_id": "ENST00000612959",
            "ensembl_translation_id": "ENSP00000477862", "evidence": "TOPMed,gnomAD",
            "clinical_significance": "-", "phenotype_disease": "-", "phenotype_disease_source": "-",
        }
        row1 = dict(base, source_db_id="rs143842750", coordinate="NC_000017.11:g.30178149A>G")
        row2 = dict(base, source_db_id="RCV004292335", coordinate="NC_000017.11:g.30178149A>G",
                    ensembl_transcript_id="ENST00000999999")  # a different transcript, same coordinate
        row3 = dict(base, source_db_id="RCV004545615", coordinate="NC_000017.11:g.30178149A>G",
                    clinical_significance="Likely benign", phenotype_disease="NSRP1-related disorder",
                    phenotype_disease_source="RCV004545615")
        row4 = dict(base, source_db_id="rs000000001", coordinate="NC_000001.11:g.111A>G")
        self.rows = [row1, row2, row3, row4]

    def test_every_coordinate_becomes_a_key(self):
        coordinate_info = up.build_variation_aggregate(self.rows)
        self.assertEqual(set(coordinate_info.keys()), {
            "NC_000017.11:g.30178149A>G", "NC_000001.11:g.111A>G",
        })

    def test_aggregates_all_source_db_ids_sharing_a_coordinate(self):
        coordinate_info = up.build_variation_aggregate(self.rows)
        info = coordinate_info["NC_000017.11:g.30178149A>G"]
        self.assertEqual(info["source_db_id"], {"rs143842750", "RCV004292335", "RCV004545615"})

    def test_aggregates_new_fields_across_rows_sharing_a_coordinate(self):
        """Two different Ensembl transcripts at the same coordinate must both
        be collected, not just the first one seen."""
        coordinate_info = up.build_variation_aggregate(self.rows)
        info = coordinate_info["NC_000017.11:g.30178149A>G"]
        self.assertEqual(info["ensembl_transcript_id"], {"ENST00000612959", "ENST00000999999"})
        self.assertEqual(info["gene_name"], {"NSRP1"})
        self.assertEqual(info["cytogenetic_band"], {"17q11.2"})
        self.assertEqual(info["evidence"], {"TOPMed,gnomAD"})

    def test_placeholder_dash_values_are_excluded(self):
        coordinate_info = up.build_variation_aggregate(self.rows)
        info = coordinate_info["NC_000017.11:g.30178149A>G"]
        self.assertNotIn("-", info["clinical_significance"])


# ---------------------------------------------------------------------------
# build_docs
# ---------------------------------------------------------------------------

def _coord_info(**overrides):
    info = {key: set() for key in up._ALL_VARIATION_FIELDS}
    for key, value in overrides.items():
        info[key] = value
    return info


def _humsavar_row(gene_name="P1", swiss_prot_ac="P00000", ftid="VAR_000001", aa_change="p.X1Y",
                   type_of_variant="US", dbsnp_id=None, disease_name=None):
    return {
        "gene_name": gene_name, "swiss_prot_ac": swiss_prot_ac, "ftid": ftid,
        "aa_change": aa_change, "type_of_variant": type_of_variant,
        "dbsnp_id": dbsnp_id, "disease_name": disease_name,
    }


class TestBuildDocs(unittest.TestCase):

    def test_coordinate_with_no_humsavar_match_has_all_variation_fields_and_no_humsavar(self):
        coordinate_info = {"NC_000001.11:g.111A>G": _coord_info(
            source_db_id={"rs000000001"}, gene_name={"OTHERGENE"}, cytogenetic_band={"1p36.33"})}
        docs = list(up.build_docs(coordinate_info, []))
        self.assertEqual(len(docs), 1)
        doc = docs[0]
        self.assertEqual(doc["_id"], "chr1:g.111A>G")
        self.assertNotIn("humsavar", doc["uniprot"])
        self.assertEqual(doc["uniprot"]["gene_name"], "OTHERGENE")
        self.assertEqual(doc["uniprot"]["cytogenetic_band"], "1p36.33")

    def test_humsavar_attached_when_dbsnp_id_matches_includes_gene_name_and_aa_change(self):
        """A document with data from both files, including the newly added
        humsavar.gene_name / humsavar.aa_change fields."""
        coordinate_info = {"NC_000019.10:g.58864491G>A": _coord_info(source_db_id={"rs893184"})}
        humsavar_rows = [_humsavar_row(gene_name="A1BG", swiss_prot_ac="P04217", ftid="VAR_018369",
                                        aa_change="p.His52Arg", type_of_variant="LB/B", dbsnp_id="rs893184")]
        doc = next(iter(up.build_docs(coordinate_info, humsavar_rows)))
        self.assertEqual(doc["uniprot"]["humsavar"], {
            "gene_name": "A1BG", "swiss_prot_ac": "P04217", "ftid": "VAR_018369",
            "aa_change": "p.His52Arg", "type_of_variant": "LB/B",
        })

    def test_unmatched_humsavar_row_becomes_standalone_document_with_all_fields(self):
        humsavar_rows = [_humsavar_row(gene_name="AARS1", swiss_prot_ac="P49588", ftid="VAR_073293",
                                        aa_change="p.Thr608Met", type_of_variant="US")]
        docs = list(up.build_docs({}, humsavar_rows))
        self.assertEqual(len(docs), 1)
        self.assertIn("_id", docs[0])
        self.assertTrue(docs[0]["_id"])
        self.assertEqual(docs[0]["uniprot"], {"humsavar": {
            "gene_name": "AARS1", "swiss_prot_ac": "P49588", "ftid": "VAR_073293",
            "aa_change": "p.Thr608Met", "type_of_variant": "US",
        }})

    def test_humsavar_row_with_dbsnp_id_absent_from_variation_file_becomes_standalone(self):
        coordinate_info = {"NC_000001.11:g.111A>G": _coord_info(source_db_id={"rs_unrelated"})}
        humsavar_rows = [_humsavar_row(ftid="VAR_000001", dbsnp_id="rs_not_in_variation_file")]
        docs = list(up.build_docs(coordinate_info, humsavar_rows))
        self.assertEqual(len(docs), 2)
        standalone = [d for d in docs if d["_id"] != "chr1:g.111A>G"][0]
        self.assertEqual(standalone["uniprot"]["humsavar"]["ftid"], "VAR_000001")

    def test_standalone_documents_get_distinct_random_ids(self):
        humsavar_rows = [_humsavar_row(ftid="VAR_1"), _humsavar_row(ftid="VAR_2")]
        docs = list(up.build_docs({}, humsavar_rows))
        ids = {d["_id"] for d in docs}
        self.assertEqual(len(ids), 2)

    def test_multiple_humsavar_matches_at_one_coordinate_become_a_list(self):
        """Real production case: ABCA1's two FTIds both cite rs137854496, both
        of which end up attached (not standalone) since the id matches."""
        coordinate_info = {"NC_000009.12:g.104831048C>G": _coord_info(
            source_db_id={"rs137854496", "RCV000010098"}, clinical_significance={"Pathogenic"})}
        humsavar_rows = [
            _humsavar_row(gene_name="ABCA1", swiss_prot_ac="O95477", ftid="VAR_009147",
                          aa_change="p.Trp590Ser", type_of_variant="LP/P", dbsnp_id="rs137854496"),
            _humsavar_row(gene_name="ABCA1", swiss_prot_ac="O95477", ftid="VAR_062487",
                          aa_change="p.Trp590Leu", type_of_variant="LP/P", dbsnp_id="rs137854496"),
        ]
        docs = list(up.build_docs(coordinate_info, humsavar_rows))
        self.assertEqual(len(docs), 1)
        humsavar = docs[0]["uniprot"]["humsavar"]
        self.assertIsInstance(humsavar, list)
        self.assertEqual({h["ftid"] for h in humsavar}, {"VAR_009147", "VAR_062487"})
        self.assertEqual({h["aa_change"] for h in humsavar}, {"p.Trp590Ser", "p.Trp590Leu"})

    def test_no_fields_beyond_the_known_set(self):
        coordinate_info = {"NC_000019.10:g.58864491G>A": _coord_info(
            source_db_id={"rs893184"}, clinical_significance={"Pathogenic"},
            phenotype_disease={"Some phenotype"}, phenotype_disease_source={"MIM:12345"})}
        humsavar_rows = [_humsavar_row(ftid="VAR_018369", dbsnp_id="rs893184", disease_name="Some disease")]
        doc = next(iter(up.build_docs(coordinate_info, humsavar_rows)))
        self.assertEqual(set(doc["uniprot"].keys()) - set(up._ALL_VARIATION_FIELDS), {"humsavar"})
        self.assertEqual(set(doc["uniprot"]["humsavar"].keys()), {
            "gene_name", "swiss_prot_ac", "ftid", "aa_change", "type_of_variant", "disease_name",
        })


# ---------------------------------------------------------------------------
# merge_docs
# ---------------------------------------------------------------------------

class TestMergeDocs(unittest.TestCase):
    """
    Regression test for a real production crash: two distinct humsavar.txt
    records for ABCA1 (VAR_009147 p.Trp590Ser and VAR_062487 p.Trp590Leu) both
    reference the same dbSNP id, rs137854496. Both resolve to the same
    genomic coordinate (chr9:g.104831048C>G), so build_docs() can yield two
    documents with the same _id. Storage does a plain insert (not upsert),
    so without merging this crashes the whole batch with a MongoDB E11000
    duplicate key error.
    """

    def setUp(self):
        self.doc_a = {
            "_id": "chr9:g.104831048C>G",
            "uniprot": {
                "humsavar": {"swiss_prot_ac": "O95477", "ftid": "VAR_009147", "type_of_variant": "LP/P"},
                "source_db_id": "rs137854496",
                "gene_name": "ABCA1",
            },
        }
        self.doc_b = {
            "_id": "chr9:g.104831048C>G",
            "uniprot": {
                "humsavar": {"swiss_prot_ac": "O95477", "ftid": "VAR_062487", "type_of_variant": "LP/P"},
                "source_db_id": ["RCV000010098", "rs137854496"],
                "clinical_significance": "Pathogenic",
                "gene_name": "ABCA1",
            },
        }

    def test_colliding_docs_produce_a_single_document(self):
        docs = list(up.merge_docs([self.doc_a, self.doc_b]))
        self.assertEqual(len(docs), 1)

    def test_humsavar_becomes_a_list_of_both_records(self):
        merged = next(iter(up.merge_docs([self.doc_a, self.doc_b])))
        humsavar = merged["uniprot"]["humsavar"]
        self.assertIsInstance(humsavar, list)
        self.assertEqual({h["ftid"] for h in humsavar}, {"VAR_009147", "VAR_062487"})

    def test_source_db_id_unioned(self):
        merged = next(iter(up.merge_docs([self.doc_a, self.doc_b])))
        self.assertEqual(sorted(merged["uniprot"]["source_db_id"]),
                          ["RCV000010098", "rs137854496"])

    def test_matching_new_field_values_collapse_to_a_scalar(self):
        merged = next(iter(up.merge_docs([self.doc_a, self.doc_b])))
        self.assertEqual(merged["uniprot"]["gene_name"], "ABCA1")

    def test_non_colliding_docs_pass_through_unchanged(self):
        other = {"_id": "chr1:g.1A>G", "uniprot": {"humsavar": {"ftid": "VAR_1"}}}
        docs = list(up.merge_docs([self.doc_a, other]))
        self.assertEqual(len(docs), 2)


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
            # matches a variation-file row below -> document with both files' data
            f.write("A1BG        P04217     VAR_018369  p.His52Arg     LB/B     rs893184       -\n")
            # no dbSNP id at all -> standalone document
            f.write("AARS1       P49588     VAR_073293  p.Thr608Met    US       -              -\n")
            # has a dbSNP id, but it's absent from the variation file -> standalone document
            f.write("ZZZ1        Q00000     VAR_999999  p.Ala1Val      US       rs_not_in_variation_file  -\n")
            # regression case: two distinct humsavar records sharing one dbSNP id
            f.write("ABCA1       O95477     VAR_009147  p.Trp590Ser    LP/P     rs137854496    "
                    "Tangier disease (TGD) [MIM:205400]\n")
            f.write("ABCA1       O95477     VAR_062487  p.Trp590Leu    LP/P     rs137854496    "
                    "Tangier disease (TGD) [MIM:205400]\n")

        variation_path = os.path.join(self.tmpdir, "homo_sapiens_variation.txt.gz")
        with gzip.open(variation_path, "wt") as f:
            f.writelines(_VARIATION_PREAMBLE)
            f.write(_variation_row("rs893184", "NC_000019.10:g.58864491G>A", gene="A1BG", aa="p.His52Arg"))
            f.write(_variation_row("RCV000012345", "NC_000019.10:g.58864491G>A",
                                    clinsig="Benign", gene="A1BG", aa="p.His52Arg"))
            # coordinate with no humsavar match at all
            f.write(_variation_row("rs999999999", "NC_000002.12:g.500A>T",
                                    gene="OTHERGENE", ac="Q11111", aa="p.Ala1Val"))
            f.write(_variation_row("rs137854496", "NC_000009.12:g.104831048C>G",
                                    clinsig="Pathogenic", gene="ABCA1", ac="O95477", aa="p.Trp590Ser"))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_every_variation_coordinate_and_every_humsavar_record_is_represented(self):
        docs = up.load_data(self.tmpdir)
        # 3 variation coordinates (chr19, chr2, chr9 -- chr9 gets the merged
        # ABCA1 humsavar pair) + 2 standalone humsavar-only documents
        # (AARS1 with no dbSNP id, ZZZ1 with an unmatched one) = 5 total
        self.assertEqual(len(docs), 5)

    def test_document_with_data_from_both_files_includes_new_fields(self):
        docs = up.load_data(self.tmpdir)
        by_id = {d["_id"]: d for d in docs}
        doc = by_id["chr19:g.58864491G>A"]
        self.assertEqual(sorted(doc["uniprot"]["source_db_id"]), ["RCV000012345", "rs893184"])
        self.assertEqual(doc["uniprot"]["clinical_significance"], "Benign")
        self.assertEqual(doc["uniprot"]["gene_name"], "A1BG")
        self.assertEqual(doc["uniprot"]["ensembl_gene_id"], "ENSG00000126653")
        self.assertEqual(doc["uniprot"]["humsavar"]["swiss_prot_ac"], "P04217")
        self.assertEqual(doc["uniprot"]["humsavar"]["aa_change"], "p.His52Arg")

    def test_variation_only_coordinate_has_no_humsavar(self):
        docs = up.load_data(self.tmpdir)
        by_id = {d["_id"]: d for d in docs}
        doc = by_id["chr2:g.500A>T"]
        self.assertNotIn("humsavar", doc["uniprot"])
        self.assertEqual(doc["uniprot"]["gene_name"], "OTHERGENE")

    def test_unmatched_humsavar_records_are_standalone_not_dropped(self):
        docs = up.load_data(self.tmpdir)
        standalone = [d for d in docs if set(d["uniprot"].keys()) == {"humsavar"}]
        self.assertEqual(len(standalone), 2)
        self.assertEqual({d["uniprot"]["humsavar"]["ftid"] for d in standalone},
                          {"VAR_073293", "VAR_999999"})
        for d in standalone:
            self.assertFalse(d["_id"].startswith("chr"))

    def test_duplicate_dbsnp_id_across_humsavar_records_is_merged_not_crashed(self):
        docs = up.load_data(self.tmpdir)
        by_id = {d["_id"]: d for d in docs}
        doc = by_id["chr9:g.104831048C>G"]
        humsavar = doc["uniprot"]["humsavar"]
        self.assertIsInstance(humsavar, list)
        self.assertEqual({h["ftid"] for h in humsavar}, {"VAR_009147", "VAR_062487"})
        self.assertEqual(doc["uniprot"]["clinical_significance"], "Pathogenic")

    def test_all_ids_unique(self):
        docs = up.load_data(self.tmpdir)
        ids = [d["_id"] for d in docs]
        self.assertEqual(len(ids), len(set(ids)))

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
