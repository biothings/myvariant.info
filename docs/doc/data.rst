.. Data

Variant annotation data
************************

.. _data_sources:

Data sources
------------

We currently obtain variant annotation data from several data resources and 
keep them up-to-date, so that you don't have to do it:

.. _dbNSFP: https://sites.google.com/site/jpopgen/dbNSFP
.. _dbSNP: http://www.ncbi.nlm.nih.gov/snp/
.. _ClinVar: http://www.ncbi.nlm.nih.gov/clinvar
.. _EVS : http://evs.gs.washington.edu/EVS/
.. _CADD: http://cadd.gs.washington.edu/
.. _MutDB: http://www.mutdb.org/
.. _GWAS Catalog: http://www.ebi.ac.uk/gwas/
.. _COSMIC: http://cancer.sanger.ac.uk/cancergenome/projects/cosmic/
.. _DOCM: http://docm.genome.wustl.edu/
.. _SNPedia: http://www.snpedia.com
.. _EMVClass: http://geneticslab.emory.edu/emvclass/emvclass.php 
.. _Scripps Wellderly: http://www.stsiweb.org/wellderly/

Total variants loaded: **286,219,908**

+-------------------------------+---------------+---------------------------+----------------------------+
| Source                        | version       | # of variants             | key name*                  |
+===============================+===============+===========================+============================+
| `dbNSFP`_                     |v2.9           | 78,045,379                | dbnsfp                     |
+-------------------------------+---------------+---------------------------+----------------------------+
| `dbSNP`_                      |v142           | 110,234,210               |dbsnp                       |
+-------------------------------+---------------+---------------------------+----------------------------+
| `ClinVar`_                    |20150323       |85,789                     |clinvar                     |
+-------------------------------+---------------+---------------------------+----------------------------+
| `EVS`_                        | v2            | 1,977,300                 | evs                        |
+-------------------------------+---------------+---------------------------+----------------------------+
| `CADD`_                       | v1.2          | 163,690,986               | cadd                       |
+-------------------------------+---------------+---------------------------+----------------------------+
| `MutDB`_                      | \-            | 420,221                   |mutdb                       |
+-------------------------------+---------------+---------------------------+----------------------------+
| `GWAS Catalog`_               |from UCSC      |15,243                     |gwassnps                    |
+-------------------------------+---------------+---------------------------+----------------------------+
| `COSMIC`_                     |v68 from UCSC  |1,024,498                  |cosmic                      |
+-------------------------------+---------------+---------------------------+----------------------------+
| `DOCM`_                       | \-            | 1,119                     | docm                       |
+-------------------------------+---------------+---------------------------+----------------------------+
| `SNPedia`_                    | \-            | 5,907                     | snpedia                    |
+-------------------------------+---------------+---------------------------+----------------------------+
| `EMVClass`_                   | \-            | 12,066                    |emv                         |
+-------------------------------+---------------+---------------------------+----------------------------+
| `Scripps Wellderly`_          | \-            |21,240,519                 | wellderly                  |
+-------------------------------+---------------+---------------------------+----------------------------+

\* key name: this is the key for the specific annotation data in a variant object. 

The most updated information can be accessed `here <http://myvariant.info/v1/metadata>`_.

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
check out `this example variant <http://myvariant.info/v1/variant/chr1:g.35367G%3EA>`_, or try the `interactive API page <http://myvariant.info/v1/api>`_.

.. raw:: html

    <div id="spacer" style="height:300px"></div> 
