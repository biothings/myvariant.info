Variant annotation service
*************************************

This page describes the reference for the MyVariant.info variant annotation web 
service.  It's also recommended to try it live on our `interactive API page <http://myvariant.info/v1/api>`_.


Service endpoint
=================
::

    http://myvariant.info/v1/variant


GET request
==================

Obtaining the variant annotation via our web service is as simple as calling this URL::

    http://myvariant.info/v1/variant/<variantid>

**variantid** above is an HGVS name based variant id using genomic location based on hg19 human genome assembly.

By default, this will return the complete variant annotation object in JSON format. See `here <#returned-object>`_ for an example and :ref:`here <variant_object>` for more details. If the input **variantid** is not valid, 404 (NOT FOUND) will be returned.

Optionally, you can pass a "**fields**" parameter to return only the annotation you want (by filtering returned object fields)::

    http://myvariant.info/v1/variant/chr1:g.35367G>A?fields=cadd

"**fields**" accepts any attributes (a.k.a fields) available from the variant object. Multiple attributes should be seperated by commas. If an attribute is not available for a specific variant object, it will be ignored. Note that the attribute names are case-sensitive.

Just like the `variant query service <variant_query_service.html>`_, you can also pass a "**callback**" parameter to make a `JSONP <http://ajaxian.com/archives/jsonp-json-with-padding>`_ call.


Query parameters
-----------------

fields
""""""""
    Optional, can be a comma-separated fields to limit the fields returned from the variant object. If "fields=all", all available fields will be returned. Note that it supports dot notation as well, e.g., you can pass "cadd.gene". Default: "fields=all".

callback
"""""""""
    Optional, you can pass a "**callback**" parameter to make a `JSONP <http://ajaxian.com/archives/jsonp-json-with-padding>`_ call.

filter
"""""""
    Alias for "fields" parameter.

email
""""""
    Optional, if you are regular users of our services, we encourage you to provide us an email, so that we can better track the usage or follow up with you.

-----------------

Returned object
---------------

A GET request like this::

    http://myvariant.info/v1/variant/chr1:g.35367G>A

should return a variant object below:

.. container :: variant-object-container

    .. include :: variant_object.json


Batch queries via POST
======================

Although making simple GET requests above to our variant query service is sufficient in most use cases,
there are some times you might find it's easier to batch query (e.g., retrieving variant
annotations for multiple variants). Fortunately, you can also make batch queries via POST requests when you
need::


    URL: http://myvariant.info/v1/variant
    HTTP method:  POST


Query parameters
----------------

ids
"""""
    Required. Accept multiple geneids (either Entrez or Ensembl gene ids) seperated by comma, e.g., 'ids=1017,1018' or 'ids=695,ENSG00000123374'. Note that currently we only take the input ids up to **1000** maximum, the rest will be omitted.

fields
"""""""
    Optional, can be a comma-separated fields to limit the fields returned from the matching hits.
    If “fields=all”, all available fields will be returned. Note that it supports dot notation as well, e.g., you can pass "refseq.rna". Default: “symbol,name,taxid,entrezgene”.

email
""""""
    Optional, if you are regular users of our services, we encourage you to provide us an email, so that we can better track the usage or follow up with you.

Example code
------------

Unlike GET requests, you can easily test them from browser, make a POST request is often done via a
piece of code, still trivial of course. Here is a sample python snippet::

    import httplib2
    h = httplib2.Http()
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    params = 'ids=chr16:g.28883241A>G,chr1:g.35367G>A&fields=dbnsfp.genename,cadd.gene'
    res, con = h.request('http://myvariant.info/v1/variant', 'POST', params, headers=headers)

Returned object
---------------

Returned result (the value of "con" variable above) from above example code should look like this:


.. code-block :: json

    [
      {
        "_id": "chr16:g.28883241A>G",
        "cadd": {
          "gene": {
            "ccds_id": "CCDS53996.1",
            "cds": {
              "cdna_pos": 1889,
              "cds_pos": 1450,
              "rel_cdna_pos": 0.61,
              "rel_cds_pos": 0.64
            },
            "feature_id": "ENST00000322610",
            "gene_id": "ENSG00000178188",
            "genename": "SH2B1",
            "prot": {
              "protpos": 484, "rel_prot_pos": 0.64
            }
          }
        },
        "dbnsfp": {
          "genename": "SH2B1"
        },
        "query": "chr16:g.28883241A>G"
      },
      {
        "_id": "chr1:g.35367G>A",
        "cadd": {
          "gene": {
            "cds": {
              "cdna_pos": 476, 
              "rel_cdna_pos": 0.4
            },
            "feature_id": "ENST00000417324",
            "gene_id": "ENSG00000237613",
            "genename": "FAM138A"
          }
        },
        "dbnsfp": {
          "genename": "FAM138A"
        },
        "query": "chr1:g.35367G>A"
      }
    ]

.. raw:: html

    <div id="spacer" style="height:300px"></div>
