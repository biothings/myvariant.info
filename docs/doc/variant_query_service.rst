Variant query service
******************************

.. role:: raw-html(raw)
   :format: html
.. |info| image:: /_static/information.png
             :alt: information!


This page describes the reference for MyVariant.info variant query web service. It's also recommended to try it live on our `interactive API page <http://myvariant.info/v1/api>`_.


Service endpoint
=================

::

    http://myvariant.info/v1/query

GET request
==================

Query parameters
-----------------

q
"""""
    Required, passing user query. The detailed query syntax for parameter "**q**" we explained `below <#query-syntax>`_.

fields
""""""
    Optional, a comma-separated string to limit the fields returned from the matching variant hits. The supported field names can be found from any variant object (e.g. `here <http://myvariant.info/v1/variant/chr16:g.28883241A%3EG>`_). Note that it supports dot notation, and wildcards as well, e.g., you can pass "dbnsfp", "dbnsfp.genename", or "dbnsfp.aa.*". If "fields=all", all available fields will be returned. Default: "all".

size
""""
    Optional, the maximum number of matching variant hits to return (with a cap of 1000 at the moment). Default: 10.

from
""""
    Optional, the number of matching variant hits to skip, starting from 0. Default: 0

.. Hint:: The combination of "**size**" and "**from**" parameters can be used to get paging for large query:

::

    q=cdk*&size=50                     first 50 hits
    q=cdk*&size=50&from=50             the next 50 hits

sort
""""
    Optional, the comma-separated fields to sort on. Prefix with "-" for descending order, otherwise in ascending order. Default: sort by matching scores in descending order.

facets
""""""
    Optional, a single field or comma-separated fields to return facets, for example, "facets=cadd", "facets=cadd,dbsnp.vartype". See `examples of faceted queries here <#faceted-queries>`_.

callback
""""""""
    Optional, you can pass a "**callback**" parameter to make a `JSONP <http://ajaxian.com/archives/jsonp-json-with-padding>`_ call.

email
""""""
    Optional, if you are regular users of our services, we encourage you to provide us an email, so that we can better track the usage or follow up with you.


Query syntax
------------
Examples of query parameter "**q**":


Simple queries
""""""""""""""

search for everything::

    q=rs58991260                        # search for rsid


Fielded queries
"""""""""""""""
::

    q=chr1:69000-70000                        # for a genomic range
    q=dbsnp.vartype:snp                       # for matching value on a specific field
    
    q=dbnsfp.polyphen2.hdiv.pred:(D P)        # multiple values for a field
    q=dbnsfp.polyphen2.hdiv.pred:(D OR P)     # multiple values for a field using OR
    
    q=_exist_:dbsnp                           # having dbsnp field
    q=_missing_:exac                          # missing exac field
    

.. Hint:: For a list of available fields, see :ref:`here <available_fields>`. 


Range queries
"""""""""""""
::

    q=dbnsfp.polyphen2.hdiv.score:>0.99
    q=dbnsfp.polyphen2.hdiv.score:>=0.99
    q=exac.af:<0.00001
    q=exac.af:<=0.00001
    
    q=exac.ac.ac_adj:[76640 TO 80000]        # bounded (including 76640 and 80000)
    q=exac.ac.ac_adj:{76640 TO 80000}        # unbounded
    

Wildcard queries
""""""""""""""""
Wildcard character "*" or "?" is supported in either simple queries or fielded queries::
    
    q=dbnsfp.genename:CDK?
    q=dbnsfp.genename:CDK*

.. note:: Wildcard character can not be the first character. It will be ignored.


Boolean operators and grouping
""""""""""""""""""""""""""""""

You can use **AND**/**OR**/**NOT** boolean operators and grouping to form complicated queries::

    q=dbnsfp.polyphen2.hdiv.score:>0.99 AND chrom:1                        AND operator
    q=_exists_:dbsnp AND NOT dbsnp.vartype:indel                           NOT operator
    q=_exists_:dbsnp AND (NOT dbsnp.vartype:indel)                         grouping with ()
    
    
Escaping reserved characters
""""""""""""""""""""""""""""
If you need to use these reserved characters in your query, make sure to escape them using a back slash ("\\")::
    
    + - = && || > < ! ( ) { } [ ] ^ " ~ * ? : \ /
    


Returned object
---------------

A GET request like this::

    http://myvariant.info/v1/query?q=chr1:69500-70000&fields=cadd.gene

should return hits as:

.. code-block:: json

        {
          "hits": [
            {
              "_id": "chr1:g.69511A>G",
              "_score": 7.2999496,
              "cadd": {
                "gene": {
                  "ccds_id": "CCDS30547.1",
                  "cds": {
                    "cdna_pos": 421,
                    "cds_pos": 421,
                    "rel_cdna_pos": 0.46,
                    "rel_cds_pos": 0.46
                  },
                  "feature_id": "ENST00000335137",
                  "gene_id": "ENSG00000186092",
                  "genename": "OR4F5",
                  "prot": {
                    "domain": "tmhmm",
                    "protpos": 141,
                    "rel_prot_pos": 0.46
                  }
                }
              }
            },
            {
              "_id": "chr1:g.69538G>A",
              "_score": 0.78757036,
              "cadd": {
                "gene": {
                  "ccds_id": "CCDS30547.1",
                  "cds": {
                    "cdna_pos": 448,
                    "cds_pos": 448,
                    "rel_cdna_pos": 0.49,
                    "rel_cds_pos": 0.49
                  },
                  "feature_id": "ENST00000335137",
                  "gene_id": "ENSG00000186092",
                  "genename": "OR4F5",
                  "prot": {
                    "domain": "ndomain",
                    "protpos": 150,
                    "rel_prot_pos": 0.49
                  }
                }
              }
            }
          ],
          "max_score": 7.2999496,
          "took": 2325,
          "total": 2
        }

"**total**" in the output gives the total number of matching hits, while the actual hits are returned under "**hits**" field. "**size**" parameter controls how many hits will be returned in one request (default is 10). Adjust "**size**" parameter and "**from**" parameter to retrieve the additional hits.

Faceted queries
----------------
If you need to perform a faceted query, you can pass an optional "`facets <#facets>`_" parameter. For example, if you want to get the facets on species, you can pass "facets=taxid":

A GET request like this::

    http://myvariant.info/v1/query?q=cadd.gene.gene_id:ENSG00000113368&facets=cadd.polyphen.cat&size=0

should return hits as:

.. code-block:: json
        
        {
          "facets": {
            "cadd.polyphen.cat": {
              "_type": "terms",
              "missing": 797,
              "other": 0,
              "terms": [
                {
                  "count": 1902,
                  "term": "benign"
                },
                {
                  "count": 998,
                  "term": "probably_damaging"
                },
                {
                  "count": 762,
                  "term": "possibly_damaging"
                }
              ],
              "total": 3662
            }
          },
          "hits": [],
          "max_score": 0.0,
          "took": 29,
          "total": 4459
        }



Batch queries via POST
======================

Although making simple GET requests above to our variant query service is sufficient for most use cases,
there are times you might find it more efficient to make batch queries (e.g., retrieving variant
annotation for multiple variants). Fortunately, you can also make batch queries via POST requests when you
need::


    URL: http://myvariant.info/v1/query
    HTTP method:  POST


Query parameters
----------------

q
"""
    Required, multiple query terms seperated by comma (also support "+" or white space), but no wildcard, e.g., 'q=rs58991260,rs2500'

scopes
""""""
    Optional, specify one or more fields (separated by comma) as the search "scopes", e.g., "scopes=dbsnp.rsid", "scopes=dbsnp.rsid,dbnsfp.genename".  The available "fields" can be passed to "**scopes**" parameter are
    :ref:`listed here <available_fields>`. Default: 

fields
""""""
    Optional, a comma-separated string to limit the fields returned from the matching variant hits. The supported field names can be found from any variant object. Note that it supports dot notation, and wildcards as well, e.g., you can pass "dbnsfp", "dbnsfp.genename", or "dbnsfp.aa.*". If "fields=all", all available fields will be returned. Default: "all".

email
""""""
    Optional, if you are regular users of our services, we encourage you to provide us an email, so that we can better track the usage or follow up with you.

Example code
------------

Unlike GET requests, you can easily test them from browser, make a POST request is often done via a
piece of code. Here is a sample python snippet::

    import httplib2
    h = httplib2.Http()
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    params = 'q=rs58991260,rs2500&scopes=dbsnp.rsid'
    res, con = h.request('http://myvariant.info/v1/query', 'POST', params, headers=headers)


Returned object
---------------

Returned result (the value of "con" variable above) from above example code should look like this:

.. code-block:: json

        [
        {'_id': 'chr1:g.218631822G>A',
          'dbsnp': {'allele_origin': 'unspecified',
           'alleles': [{'allele': 'G', 'freq': 0.9784},
            {'allele': 'A', 'freq': 0.02157}],
           'alt': 'A',
           'chrom': '1',
           'class': 'SNV',
           'dbsnp_build': 129,
           'flags': ['ASP', 'G5', 'G5A', 'GNO', 'KGPhase1', 'KGPhase3', 'SLO'],
           'gmaf': 0.02157,
           'hg19': {'end': 218631823, 'start': 218631822},
           'ref': 'G',
           'rsid': 'rs58991260',
           'validated': True,
           'var_subtype': 'ts',
           'vartype': 'snp'},
          'query': 'rs58991260',
          'wellderly': {'alleles': [{'allele': 'A', 'freq': 0.0025},
            {'allele': 'G', 'freq': 0.9975}],
           'alt': 'A',
           'chrom': '1',
           'gene': 'TGFB2',
           'genotypes': [{'count': 1, 'freq': 0.005, 'genotype': 'G/A'},
            {'count': 199, 'freq': 0.995, 'genotype': 'G/G'}],
           'hg19': {'end': 218631822, 'start': 218631822},
           'pos': 218631822,
           'ref': 'G',
           'vartype': 'snp'}},
         {'_id': 'chr11:g.66397320A>G',
          'dbsnp': {'allele_origin': 'unspecified',
           'alleles': [{'allele': 'A'}, {'allele': 'G'}],
           'alt': 'G',
           'chrom': '11',
           'class': 'SNV',
           'dbsnp_build': 36,
           'flags': ['ASP', 'INT', 'RV', 'U3'],
           'hg19': {'end': 66397321, 'start': 66397320},
           'ref': 'A',
           'rsid': 'rs2500',
           'validated': False,
           'var_subtype': 'ts',
           'vartype': 'snp'},
          'query': 'rs2500'}
        ]

.. Tip:: "query" field in returned object indicates the matching query term.

If a query term has no match, it will return with "**notfound**" field as "**true**":

.. code-block:: json

      [
        ...,
        {'query': '...',
         'notfound': true},
        ...
      ]


.. raw:: html

    <div id="spacer" style="height:300px"></div>
