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
.. _EXAC: http://exac.broadinstitute.org/
.. _GRASP: http://iapps.nhlbi.nih.gov/GRASP

.. raw:: html

    <div class='metadata-table'>

Total variants loaded: **334,292,622**

+-------------------------------+---------------+---------------------------+----------------------------+
| Source                        | version       | # of variants             | key name*                  |
+===============================+===============+===========================+============================+
| `dbNSFP`_                     |v3.0c          | 82,030,830                | dbnsfp                     |
+-------------------------------+---------------+---------------------------+----------------------------+
| `dbSNP`_                      |v144           | 145,132,257               |dbsnp                       |
+-------------------------------+---------------+---------------------------+----------------------------+
| `ClinVar`_                    |201601         | 124,047                   |clinvar                     |
+-------------------------------+---------------+---------------------------+----------------------------+
| `EVS`_                        | v2            | 1,977,300                 | evs                        |
+-------------------------------+---------------+---------------------------+----------------------------+
| `CADD`_                       | v1.3          | 226,932,858               | cadd                       |
+-------------------------------+---------------+---------------------------+----------------------------+
| `MutDB`_                      | \-            | 420,221                   |mutdb                       |
+-------------------------------+---------------+---------------------------+----------------------------+
| `GWAS Catalog`_               |from UCSC      | 15,243                    |gwassnps                    |
+-------------------------------+---------------+---------------------------+----------------------------+
| `COSMIC`_                     |v68 from UCSC  | 1,024,498                 |cosmic                      |
+-------------------------------+---------------+---------------------------+----------------------------+
| `DOCM`_                       | \-            | 1,119                     | docm                       |
+-------------------------------+---------------+---------------------------+----------------------------+
| `SNPedia`_                    | \-            | 5,907                     | snpedia                    |
+-------------------------------+---------------+---------------------------+----------------------------+
| `EMVClass`_                   | \-            | 12,066                    |emv                         |
+-------------------------------+---------------+---------------------------+----------------------------+
| `Scripps Wellderly`_          | \-            | 21,240,519                | wellderly                  |
+-------------------------------+---------------+---------------------------+----------------------------+
| `EXAC`_                       | v0.3          | 10,195,872                | exac                       |
+-------------------------------+---------------+---------------------------+----------------------------+
| `GRASP`_                      | v2.0.0.0      | 2,212,148                 | grasp                      |
+-------------------------------+---------------+---------------------------+----------------------------+

.. raw:: html

    </div>

\* key name: this is the key for the specific annotation data in a variant object.

The most updated information can be accessed `here <http://myvariant.info/v1/metadata>`_.

.. note:: Each data source may have its own usage restrictions (e.g. `CADD`_ data are free for non-commercial use only). Please refer to the data source pages above for their specific restrictions.


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


_id field
---------

Each individual variant object contains an "**_id**" field as the primary key. We utilize the recommended nomenclature from `Human Genome Variation Society <http://www.hgvs.org>`_ to define the "**_id**" field in MyVariant.info. Specifically, we use HGVS’s genomic reference sequence notation based on the current reference genome assembly (e.g. hg19 for human). The followings are brief representations of major types of genetic variants. More examples could be found at HVGS `recommendations for the description of DNA sequence variants <http://www.hgvs.org/mutnomen/recs-DNA.html>`_ page.

.. note:: The default reference genome assembly is always human hg19 in MyVariant.info, so we only use "chr??" to represent the reference genomic sequence in "**_id**" field. The valid chromosomes representations are **chr1**, **chr2**, ..., **chr22**, **chrX**, **chrY** and **chrMT**. Do not use *chr23* for *chrX*, *chr24* for *chrY*, or *chrM* for *chrMT*.

* SNV example::

      chr1:g.35366C>T

  The above _id represents a C to T SNV on chromosome 1, genomic position 35366.

* Insertion example::

      chr2:g.17142_17143insA

  The above _id represents that an A is inserted between genomic position 17142 and 17143 on chromosome 2.

* Deletion example::

    chrMT:g.8271_8279del

  The above _id represents that a nine nucleotides deletion between genomic position 8271 and 8279 on chromosome MT. Note that we don't include the deleted sequence in the _id field in this case.

* Deletion/Insertion example::

    chrX:g.14112_14117delinsTG

  The above _id represents that six nucleotides between genomic position 14112 and 14117 are replaced by TG.


.. _available_fields:

Available fields
----------------

The table below lists all of the possible fields that could be in a variant object, as well as all of their parents (for nested fields).  If the field is indexed, it may also be directly queried, e.g.

::

    q=dbnsfp.polyphen2.hdiv.score:>0.99


All fields can be used with _exists_ or _missing_ filters, e.g.

::

    q=_exists_:dbsnp AND _exists_:cosmic
    q=_missing_:wellderly

or as inputs to the fields parameter, e.g.

::

    q=_exists_:dbsnp&fields=dbsnp.rsid,dbsnp.vartype


.. raw:: html

    <table class='indexed-field-table stripe'>
        <thead>
            <tr>
                <th>Field</th>
                <th>Indexed</th>
                <th>Type</th>
                <th>Notes</th>
            </tr>
        </thead>
        <tbody>
        </tbody>
    </table>

    <div id="spacer" style="height:300px"></div>
