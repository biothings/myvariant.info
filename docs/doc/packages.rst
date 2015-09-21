.. PythonPackages

Third-party packages
********************

This page lists the third-party packages/modules built upon the `MyVariant.info <http://myvariant.info>`_ services.

.. _myvariant_python:

MyVariant python module
-----------------------

"`myvariant <https://pypi.python.org/pypi/myvariant>`_" is an easy-to-use Python wrapper to access `MyVariant.info <http://myvariant.info>`_ services.

You can install it easily using either `pip <http://www.pip-installer.org>`_ or `easy_install <https://pypi.python.org/pypi/setuptools>`_::

    pip install myvariant               #this is preferred

or::

    easy_install myvariant

This is a brief example:

.. code-block :: python

        In [1]: import myvariant

        In [2]: mv = myvariant.MyVariantInfo()

        In [3]: mv.getvariant('chr1:g.35367G>A')
        Out[3]:
        {'_id': 'chr1:g.35367G>A',
         '_version': 1,
         'cadd': {'alt': 'A',
          'annotype': 'NonCodingTranscript',
          'bstatistic': 994,
          'chmm': {'bivflnk': 0.0,
           'enh': 0.0,
           'enhbiv': 0.0,
           'het': 0.0,
           'quies': 1.0,
           'reprpc': 0.0,
           'reprpcwk': 0.0,
           'tssa': 0.0,
           'tssaflnk': 0.0,
           'tssbiv': 0.0,
           'tx': 0.0,
           'txflnk': 0.0,
           'txwk': 0.0,
           'znfrpts': 0.0},
          'chrom': 1,
          'consdetail': 'non_coding_exon,nc',
          'consequence': 'NONCODING_CHANGE',
          'consscore': 5,
          'cpg': 0.03,
          'dna': {'helt': -2.04, 'mgw': 0.01, 'prot': 1.54, 'roll': -0.63},
          'encode': {'exp': 31.46, 'h3k27ac': 23.44, 'h3k4me1': 23.8, 'h3k4me3': 8.6},
          'exon': '2/3',
          'fitcons': 0.577621,
          'gc': 0.48,
          'gene': {'cds': {'cdna_pos': 476, 'rel_cdna_pos': 0.4},
           'feature_id': 'ENST00000417324',
           'gene_id': 'ENSG00000237613',
           'genename': 'FAM138A'},
          'gerp': {'n': 1.29, 's': -0.558},
          'isknownvariant': 'FALSE',
          'istv': 'FALSE',
          'length': 0,
          'mapability': {'20bp': 0, '35bp': 0},
          'min_dist_tse': 122,
          'min_dist_tss': 707,
          'mutindex': 70,
          'phast_cons': {'mammalian': 0.003, 'primate': 0.013, 'vertebrate': 0.003},
          'phred': 1.493,
          'phylop': {'mammalian': -0.155, 'primate': 0.151, 'vertebrate': -0.128},
          'pos': 35367,
          'rawscore': -0.160079,
          'ref': 'G',
          'scoresegdup': 0.99,
          'segway': 'D',
          'type': 'SNV'},
         'snpeff': {'ann': [{'effect': 'non_coding_exon_variant',
            'feature_id': 'NR_026818.1',
            'feature_type': 'transcript',
            'gene_id': 'FAM138A',
            'gene_name': 'FAM138A',
            'hgvs_c': 'n.476C>T',
            'putative_impact': 'MODIFIER',
            'rank': '2',
            'total': '3',
            'transcript_biotype': 'Noncoding'},
           {'effect': 'non_coding_exon_variant',
            'feature_id': 'NR_026820.1.2',
            'feature_type': 'transcript',
            'gene_id': 'FAM138F.2',
            'gene_name': 'FAM138F',
            'hgvs_c': 'n.476C>T',
            'putative_impact': 'MODIFIER',
            'rank': '2',
            'total': '3',
            'transcript_biotype': 'Noncoding'}]},
         'vcf': {'alt': 'A', 'position': '35367', 'ref': 'G'}}

See https://pypi.python.org/pypi/myvariant for more details.



.. raw:: html

    <div id="spacer" style="height:300px"></div>
