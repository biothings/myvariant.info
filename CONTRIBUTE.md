# How to Contribute

If you have/find a variant annotation resource you want to include in our system, you can follow the guideline below to contribute a JSON importer (let's call it "data plugin") for it.

----
## General guidelines
1. Code in Python (at least for now)
2. Use hg19 genome assembly for genomic coordinates (assuming we are dealing with human variants for now)
3. all data plugins are located under [src/dataload/contrib](https://github.com/Network-of-BioThings/myvariant.info/tree/master/src/dataload/contrib) folder

## Steps to follow
1. Fork this repo

        git clone https://github.com/Network-of-BioThings/myvariant.info [**repo_name**]

2. Add your own data plugin (under a subfolder): The subfolder should have two files, one parser file and another '\_\_init\_\_.py' file. In '\_\_init\_\_.py' file, you should include Meta dictionary information as well as the get_mapping function(see step 4 and 5). For parser file, you should include the load_data function(see step 3).
3. Write load_data function: The output of this function should be either a list or generator of JSON documents. A generator is ideal for large lists that won't fit into memory. (Details will be shown in the next section)
4. Include Meta dictionary: you can put some metadata like "maintainer", "requirements", etc. An example could be found at [src/dataload/contrib/dbsnp/\_\_init\_\_.py](https://github.com/Network-of-BioThings/myvariant.info/blob/master/src/dataload/contrib/dbnsfp/__init__.py)
5. Get mapping function: optional, this can be used to customize the indexing. You can just leave it empty. An example could be found at [src/dataload/contrib/dbsnp/\_\_init\_\_.py](https://github.com/Network-of-BioThings/myvariant.info/blob/master/src/dataload/contrib/dbnsfp/\_\_init\_\_.py)
6. Validate HGVS IDs (Details will be shown in the next section)
7. Commit and send the pull request
8. And the last, if you have trouble to code a data plugin, you can just produce a dump of JSON document list using whatever tools you like, and send over your dumped file to us. But that will require us to load it manually.

## load_data function
Parsers should be written in python and structured into JSON format to be uploaded into MongoDb, where the data will be indexed to ElasticSearch. Generic functions are can be utilized from the utils.dataload module to help structure data properly into JSON as well as clean up data. Further elaboration will be provided. 
Check out the example [src/dataload/contrib/dbsnp](https://github.com/Network-of-BioThings/myvariant.info/tree/master/src/dataload/contrib/dbsnp) folder.
The following should be defined
 

The load_data function could be divided into two parts:

----
### 1. Load data from source file
The first step is to read in source files. The source files could be in different formats, including tsv, csv, vcf, xml. There are a variety of python libraries and packages available to help read and parse these data files, e.g. python cvs library, PyVCF. Here, we have listed examples of data loading modules for some of the major formats.

#### 1) tsv/csv file example
An example of ‘tsv’ or ‘csv’ data loading module could be found under: [src/dataload/contrib/dbnsfp/dbnsfp_parser.py](https://github.com/Network-of-BioThings/myvariant.info/blob/master/src/dataload/contrib/dbnsfp/dbnsfp_parser.py)

#### 2) vcf file example
An example of ‘vcf’ data loading module could be found under: [src/dataload/contrib/exac/exac_parser.py](https://github.com/Network-of-BioThings/myvariant.info/blob/master/src/dataload/contrib/exac/exac_parser.py)

#### 3) xml file example
An example of ‘xml’ data loading module could be found under: [src/dataload/contrib/clinvar/clinvar_xml_parser.py](https://github.com/Network-of-BioThings/myvariant.info/blob/master/src/dataload/contrib/exac/exac_parser.py)

### 2. Convert each item into a JSON object
All JSON objects for MyVariant.info should have two major field, the ‘_id’ field and the ‘property’ field.

#### 1) ’_id’ field
Each individual JSON object contains an "**_id**" field as the primary key. We utilize recommended nomenclature from Human Genome Variation Society to define the "**_id**" field in MyVariant.info. We use HGVS’s genomic reference sequence notation based on the current reference genome assembly (e.g. hg19 for human). The followings are brief representations of major types of sequence variants. More examples could be found at http://www.hgvs.org/mutnomen/recs-DNA.html.

**NOTE**: The default reference genome assembly is always human hg19 in MyVariant.info, so we only use "chr??" to represent the reference genomic sequence in "**_id**" field. The valid chromosomes representations are **chr1**, **chr2**, ..., **chr22**, **chrX**, **chrY** and **chrMT**. Do not use *chr23* for *chrX*, *chr24* for *chrY*, or *chrM* for *chrMT*.


##### SNV example
	    e.g. chr1:g.35366C>T
   	    The above ID represents a C to T SNP on chromosome 1, genomic position 35366.

##### Insertion example
	    e.g. chr2:g.177676_177677insT 
	    The above ID represents that a T is inserted between genomic position 177676 and 177677 on chromosome 2.

##### Deletion example
  	    e.g. chrM:g.2947878_2947880del
	    The above ID represents that a three nucleotides deletion between genomic position 2947878 and 2947880 on chromosome M. Note that we don't include the deleted sequence in the _id field in this case.

##### Deletion/Insertion example
	    e.g. chrX: g.14112_14117delinsTG
	    The above ID represents that six nucleotides between genomic position 14112 and 14117 by TG

#### 2) Property field
The name of the ‘property’ field should be the same as the data source, e.g. ‘clinvar’, ‘dbsnp’. Multiple properties could be included in this field. And each property should represent one attribute, e.g. ‘chromosome’, ‘ref’, ‘alt’, ‘score’. Under each property, it could also have sub-properties. For example, in ‘dbnsfp’, the ‘sift’ property has sub-properties, including ‘score’, ‘converted_rankscore’, and ‘pred’. 
A typical example of JSON object in MyVariant.info could be found at [src/dataload/contrib/dbnsfp/dbnsfp_parser.py](https://github.com/Network-of-BioThings/myvariant.info/blob/master/src/dataload/contrib/dbnsfp/dbnsfp_parser.py)



## Variant_ID validation
In order to make sure all variant IDs loaded into MyVariant.info strictly follows hgvs guidelines, we have developed a variant validation function to validate all variant IDs to be loads. The validation steps are as follows:


### step 1: Call load_data function and get generator of JSON documents


    from dataload.contrib.[db].[db]_parser import load_data
    db_generator = load_data()


### step 2: Call VariantValidator class under src/utils folder


    from utils.validate import VariantValidator
    t = VariantValidator()



### step 3: Run validate_generator function on your generator


    t.validate_generator(db_generator)


or return the correct hgvs id if false example occurred

    t.validate_generator(db_generator, verbose = True)


or return a list of false and none ids

    t.validate_generator(db_generator, return_false = True, return_none = True)


