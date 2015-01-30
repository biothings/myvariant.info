# How to Contribute

This vignette will demonstrate how to upload a variant annotation data source to MyVariant.info web service. 

----
### Introduction
Parsers should be written in python and structured into JSON format to be uploaded into MongoDb, where the data will be indexed to ElasticSearch. Generic functions are can be utilized from the utils.dataload module to help structure data properly into JSON as well as clean up data. Further elaboration will be provided.  

----
### HGVS IDs As Primary Key 
Each document, or genetic variant and its respective annotations, are referenced by [HGVS](http://www.hgvs.org/mutnomen/recs-DNA.html) (Human Genome Variation Society)nomenclature. These are brief representations of the sequence variant. 

Ex) 

**chr1:g.35366C>T**

The above ID represents a C to T SNP on chromosome 1, genomic position 35366. Deletions, insertions, duplications, indels, etc. representations are further described [here](http://www.hgvs.org/mutnomen/recs-DNA.html).

### Mapping to JSON 
The variant documents must be stored in JSON. One function called **_map****_****line****_****to**_**json** calls a flat file's fields as dictionary keys and assigns the data from the cells to the values. The document's first key is `_id:`. The HGVS ID can usually be created by concatenating data values and using python's *re* module to extract them. The second key is the database name and the value is a dictionary of the database's annotations. A **load_data** function should then be used to pass the flatfile to the **_map****_****line****_****to**_**json** and output a generator, which is ideal for large lists that will not fit into memory.

### Helper Functions
Helper [functions](https://github.com/Network-of-BioThings/myvariant.info/blob/master/src/utils/dataload.py) should be utilized to help format and clean up the data. Commonly used functions:

**dict_sweep**: Recursively removes keys from the dictionary whose values are specified by the input parameter, typically empty strings or "NA" values.

**value_convert**: Converts number values to integers or floats.

**merge_duplicate**_**rows**: Combines variant documents with duplicate HGVS IDs into a single document. Only works on sorted databases (typically by chromosome and location). MongoDb will not accept duplicate variant documents.

### Validation

### More
The ClinVar [parser](https://github.com/Network-of-BioThings/myvariant.info/blob/master/src/dataload/contrib/clinvar/clinvar_parser.py) can be used as a guideline for uploading your own annotations to MyVariant.info. Once complete, fork this repo, add a module to src.dataload.contrib, and send a pull request. 