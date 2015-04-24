.. Data

Variant annotation data
************************

.. _data_sources:

Data sources
------------

We currently obtain variant annotation data from several data resources and 
keep them up-to-date, so that you don't have to do it:

+---------------------+--------------------------+------------------------+ 
| Source              | Update Frequency         | Notes                  | 
+=====================+==========================+========================+ 
| EVS                 | on new release           | evs                    | 
+---------------------+--------------------------+------------------------+ 
| CADD                | on new release           | cadd                   |
+---------------------+--------------------------+------------------------+ 
| Scripps Wellderly   | on new release           | wellderly              |
| Genome Resource     |                          |                        |
+---------------------+--------------------------+------------------------+
| dbNSFP              | on new release           | dbnsfp                 |
+---------------------+--------------------------+------------------------+
| SNPedia             | on new release           | snpedia                |
+---------------------+--------------------------+------------------------+
| ClinVar             | on new release           | clinvar                |
+---------------------+--------------------------+------------------------+
| DoCM                | on new release           | docm                   |
+---------------------+--------------------------+------------------------+
| MutDB               | on new release           | mutdb                  |
+---------------------+--------------------------+------------------------+
| COSMIC              | on new release           | cosmic                 |
+---------------------+--------------------------+------------------------+
| dbSNP               | on new release           | dbsnp                  |
+---------------------+--------------------------+------------------------+
| EmVClass            | on new release           | emv                    |
+---------------------+--------------------------+------------------------+
| GWAS SNP            | on new release           | gwassnp                |
+---------------------+--------------------------+------------------------+

The most updated information can be accessed 'here <http://myvariant.info/v1/metadata>'_.

.. _variant_object:

Variant object
---------------

Variant annotation data are both stored and returned as a variant object, which 
is essentially a collection of fields (attributes) and their values:

.. code-block :: json

{
  "_id": "chr1:g.35367G>A",
  "_version": 2,
  "cadd": {
    "alt": "A",
    "annotype": "NonCodingTranscript",
    "chrom": 1,
    "gene": {
      "cds": {
        "cdna_pos": 476,
        "rel_cdna_pos": 0.4
      },
      "feature_id": "ENST00000417324",
      "gene_id": "ENSG00000237613",
    },
    "ref": "G",
    "type": "SNV"  
  },
  "dbnsfp": {
    "aa": {
      "aapos_sift": "ENSP00000409362:P44L",
      "alt": "L",
      "codonpos": 2,
      "pos": 44,
      "ref": "P",
      "refcodon": "CCG"
    },
    "alt": "A",
    "ancestral_allele": "G",
    "chrom": "1",
    "ensembl": {
      "geneid": "ENSG00000237613",
      "transcriptid": "ENST00000417324"
    },
    "genename": "FAM138A",
    "hg19": {
      "end": 35367,
      "start": 35367
    }
  }
}

The example above omits many of the available fields.  For a full example, 
check out 'this example variant <http://myvariant.info/v1/variant/chr1:g.35367G%3EA>'_, or try the 'interactive API page <http://myvariant.info/v1/api>'_.

.. raw:: html

    <div id="spacer" style="height:300px"></div> 
