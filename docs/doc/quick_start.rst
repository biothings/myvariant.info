Quick start
-----------

`MyVariant.info <http://myvariant.info>`_ provides two simple web services: one for variant queries and the other for variant annotation retrieval. Both return results in `JSON <http://json.org>`_ format.

Variant query service
^^^^^^^^^^^^^^^^^^^^^


URL
"""""
::

    http://myvariant.info/v1/query

Examples
""""""""
::

    http://myvariant.info/v1/query?q=rs58991260
    http://myvariant.info/v1/query?q=chr1:69000-70000
    http://myvariant.info/v1/query?q=dbsnp.vartype:snp
    http://myvariant.info/v1/query?q=_exists_:dbsnp  AND NOT dbsnp.vartype:indel
    http://myvariant.info/v1/query?q=dbnsfp.polyphen2.hdiv.score:>0.99 AND chrom:1
    http://myvariant.info/v1/query?q=cadd.gene.gene_id:ENSG00000113368&facets=cadd.polyphen.cat&size=0
    http://myvariant.info/v1/query?q=_exists_:dbsnp AND _exists_:cosmic    
    

.. Hint:: View nicely formatted JSON result in your browser with this handy add-on: `JSON formater <https://chrome.google.com/webstore/detail/bcjindcccaagfpapjjmafapmmgkkhgoa>`_ for Chrome or `JSONView <https://addons.mozilla.org/en-US/firefox/addon/jsonview/>`_ for Firefox.



To learn more
"""""""""""""

* You can read `the full description of our query syntax here <doc/variant_query_service.html>`_.
* Try it live on `interactive API page <http://myvariant.info/v1/api>`_.
* Batch queries? Yes, you can. do it with `a POST request <doc/variant_query_service.html#batch-queries-via-post>`_.



Variant annotation service
^^^^^^^^^^^^^^^^^^^^^^^^^^

URL
"""""
::

    http://myvariant.info/v1/variant/<variant_id>

Examples
""""""""
::

    http://myvariant.info/v1/variant/chr1:g.35367G>A
    http://myvariant.info/v1/variant/chr7:g.55241707G>T
    http://myvariant.info/v1/variant/chr9:g.107620835G>A
    http://myvariant.info/v1/variant/chr1:g.160145907G>T
    http://myvariant.info/v1/variant/chr16:g.28883241A>G
    http://myvariant.info/v1/variant/chr3:g.49721532G>A    

"*\<variant_id\>*" is an HGVS name based variant id using genomic location based on hg19 human genome assembly..


To learn more
"""""""""""""

* You can read `the full description of our query syntax here <doc/variant_annotation_service.html>`_.
* Try it live on `interactive API page <http://myvariant.info/v1/api>`_.
* Yes, batch queries via `POST request <doc/variant_annotation_service.html#batch-queries-via-post>`_ as well.
