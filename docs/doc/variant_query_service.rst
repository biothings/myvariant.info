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

fetch_all
"""""""""
    Optional, a boolean, which when TRUE, allows fast retrieval of all unsorted query hits.  The return object contains a **_scroll_id** field, which when passed as a parameter to the query endpoint, returns the next 1000 query results.  Setting **fetch_all** = TRUE causes the results to be inherently unsorted, therefore the **sort** parameter is ignored.  For more information see `examples using fetch_all here <#scrolling-queries>`_.  Default: FALSE.

scroll_id
"""""""""
    Optional, a string containing the **_scroll_id** returned from a query request with **fetch_all** = TRUE.  Supplying a valid **scroll_id** will return the next 1000 unordered results.  If the next results are not obtained within 1 minute of the previous set of results, the **scroll_id** becomes stale, and a new one must be obtained with another query request with **fetch_all** = TRUE.  All other parameters are ignored when the **scroll_id** parameter is supplied.  For more information see `examples using scroll_id here <#scrolling-queries>`_.

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
    
    q=_exists_:dbsnp                          # having dbsnp field
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


Scrolling queries
"""""""""""""""""
If you want to return ALL results of a very large query, sometimes the paging method described `above <#from>`_ can take too long.  In these cases, you can use a scrolling query.  
This is a two-step process that turns off database sorting to allow very fast retrieval of all query results.  To begin a scrolling query, you first call the query
endpoint as you normally would, but with an extra parameter **fetch_all** = TRUE.  For example, a GET request to::

    http://myvariant.info/v1/query?q=cadd.phred:>50&fetch_all=TRUE

Returns the following object:

.. code-block:: json

    {
      "_scroll_id": "c2NhbjsxMDs5MjQ2OTc2Ok5nM0d0czYzUlcyU0dUU1dFemo5Mmc7MTE1NTgyNjA6RV9La1c5WklSQy16cVFuRXFzcEV3dzs5MjQ2ODc0Ok5uQkVpaEg5Uk9pYjA4ZVQ3RVh5TWc7OTI0Njg3MTpObkJFaWhIOVJPaWIwOGVUN0VYeU1nOzkyNDY4NzI6Tm5CRWloSDlST2liMDhlVDdFWHlNZzs5MjQ3Mjc3OjRNV2NtY1A5VFdPLUotSmM4a0w1Z0E7OTI0Njk3NzpOZzNHdHM2M1JXMlNHVFNXRXpqOTJnOzkyNDY4NzM6Tm5CRWloSDlST2liMDhlVDdFWHlNZzs5MjQ3MDgxOjE3MEZxVWRXU3BTdC1DMmdYeHdHNXc7MTE1NTgyNTk6RV9La1c5WklSQy16cVFuRXFzcEV3dzsxO3RvdGFsX2hpdHM6NTg3NTk7",
      "hits": [],
      "max_score": 0.0,
      "took": 84,
      "total": 58759
    }

At this point a scroll has been set up for your query.  To get the next batch of 1000 unordered results, simply execute a GET request to the following address, supplying the _scroll_id from the first step into the **scroll_id** parameter in the second step::

    http://myvariant.info/v1/query?scroll_id=c2NhbjsxMDsxMTU1NjY5MTpxSnFkTFdVQlJ6T1dRVzNQaWRzQkhROzExNTU4MjYxOkVfS2tXOVpJUkMtenFRbkVxc3BFd3c7MTE1NTY2OTI6cUpxZExXVUJSek9XUVczUGlkc0JIUTsxMTU1NjY5MDpxSnFkTFdVQlJ6T1dRVzNQaWRzQkhROzkyNDcyNzg6NE1XY21jUDlUV08tSi1KYzhrTDVnQTs5MjQ2OTc4Ok5nM0d0czYzUlcyU0dUU1dFemo5Mmc7OTI0NzI3OTo0TVdjbWNQOVRXTy1KLUpjOGtMNWdBOzkyNDY4NzU6Tm5CRWloSDlST2liMDhlVDdFWHlNZzs5MjQ3MTEyOlpQb3M5cDh6VDMyNnczenFhMW1hcVE7OTI0NzA4MjoxNzBGcVVkV1NwU3QtQzJnWHh3RzV3OzE7dG90YWxfaGl0czo1ODc1OTs=

.. Hint:: Your scroll will remain active for 1 minute from the last time you requested results from it.  If your scroll expires before you get the last batch of results, you must re-request the scroll_id by setting **fetch_all** = TRUE as in step 1.

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
