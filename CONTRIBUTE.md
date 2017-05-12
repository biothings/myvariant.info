# How to Contribute

If you have/find a variant annotation resource you want to include in our system, you can follow the guideline below to contribute a JSON importer (let's call it a "data plugin") for it.

----
## General guidelines
1. Code in Python (at least for now), and prefer in Python 3.
2. Use hg19 or hg38 genome assembly for genomic coordinates (assuming we are dealing with human variants for now)
3. all data plugins are located under [src/dataload/sources](src/dataload/sources) folder. You should follow this [sample_src example](src/dataload/sources/sample_src).
4. Each data plugin is one sub-folder under "sources", and the name of the sub-folder is typically the same as the root-level data_src key name, e.g. ["dbsnp" subfolder](/src/dataload/sources/dbsnp) handles all annoation data under "dbsnp" key.
5. Other existing data plugin folders typically contain `*_upload.py` and `*_dump.py` files. You generally don't need to worry about the `Uploader` and `Dumper` classes in these files. Just follow the steps below to provide us a simple data parser. Once we verify your data parser, we will convert it to the formal `Uploader` and `Dumper` classes.

## Steps to follow
1. Fork this repo, and clone your *forked repo* locally

    https://github.com/biothings/myvariant.info

2. Add your own data plugin (under a subfolder): The subfolder should start with two files: one parser file and another `__init__.py` file. The parser file, you should include the `load_data` function(see step 3). In `__init__.py` file, you can just leave it empty. Although not required, we typically name the parser file as "\<data_src\>_parser.py", like "dbsnp_parser.py", or "dbsnp_vcf_parser.py" when a data source provides multiple file formats.

3. Write `load_data` function: The first input parameter should be the input file or the input folder for multiple input files. The output of this function should be either a list or generator of JSON documents. A generator is ideal for large lists that won't fit into memory. (Details will be shown in the next section)
   
   If your data file support both hg19 and hg38 genomic assembly for variants, your `load_data` function should support a parameter to return either hg19 or hg38 based variants (e.g. using "assembly=hg19|hg38").

4. [Optional] add Meta dictionary: you can put some metadata like "maintainer", "requirements" etc. at the top of the parser file. Here is an example:
 ```
    __METADATA__ = {
        "requirements": [
            "PyVCF>=0.6.7",
        ],
        "src_name": 'dbSNP',
        "src_url": 'http://www.ncbi.nlm.nih.gov/SNP/',
        "version": '147',
        "field": "dbsnp"
    }
 ```

5. [Optional] `get_mapping` function returns a mapping dictionary to describe the JSON data structure and customize indexing. Typicaly, you can just skip it first and we can help to create one. An example `get_mapping` function can be found in [src/dataload/sources/sample_src/sample_src_parser.py](src/dataload/sources/sample_src/sample_src_parser.py).

6. [Optional] validate HGVS IDs (Details will be shown in the next section)

7. Commit and send the pull request.

   Here is a real-world pull request example from one of our contributors: [#13](https://github.com/biothings/myvariant.info/pull/13).

8. And the last, if you have trouble to code a data plugin, you can just produce a dump of JSON document list using whatever tools you like, and send over your dumped file to us. But that will require us to load it manually.

## `load_data` function
Parsers should be written in python and convert the input data file into structured JSON objects. We will then take the output and merge them with other data sources at our data backend. Some generic helper functions from [`utils.dataload`](src/utils/dataload) module can be utilized to help structure data properly into JSON as well as clean up data.
Check out the example [src/dataload/sources/sample_src](src/dataload/sources/sample_src) folder.

The `load_data` function could be divided into two parts:

### 1. Load data from source file
The first step is to read in source files. The source files could be in different formats, including tsv, csv, vcf, xml. There are a variety of python libraries and packages available to help read and parse these data files, e.g. python cvs library, PyVCF. Here, we have listed examples of data loading modules for some of the major formats.

#### 1) tsv/csv file example
An example of "*tsv*" or "*csv*" data loading module could be found under: [src/dataload/sources/dbnsfp/dbnsfp_parser.py](src/dataload/sources/dbnsfp/dbnsfp_parser.py)

#### 2) vcf file example
An example of "*vcf*" data loading module could be found under: [src/dataload/sources/exac/exac_parser.py](src/dataload/sources/exac/exac_parser.py)

#### 3) xml file example
An example of "*xml*" data loading module could be found under: [src/dataload/sources/clinvar/clinvar_xml_parser.py](src/dataload/sources/clinvar/clinvar_xml_parser.py)

### 2. Convert each item into a JSON object
All JSON objects for MyVariant.info should have two required fields: the **_id** field and the **<data_src\>** field.

#### 1) **_id** field
Each individual JSON object contains an "**_id**" field as the primary key. We utilize recommended nomenclature from Human Genome Variation Society (HGVS) to define the "**_id**" field in MyVariant.info. We use HGVS’s genomic reference sequence notation based on the current reference genome assembly (e.g. hg19 for human). The followings are brief representations of major types of sequence variants. More examples could be found at [our documentation page](http://docs.myvariant.info/en/latest/doc/data.html#id-field) and http://www.hgvs.org/mutnomen/recs-DNA.html.

**NOTE**: In MyVariant.info, we only use "chr??" to represent the reference genomic sequence in "**_id**" field. The valid chromosomes representations are **chr1**, **chr2**, ..., **chr22**, **chrX**, **chrY** and **chrMT**. Do not use *chr23* for *chrX*, *chr24* for *chrY*, or *chrM* for *chrMT*.


##### SNV example
	chr1:g.35366C>T

  The above ID represents a C to T SNP on chromosome 1, genomic position 35366.

##### Insertion example
	chr2:g.177676_177677insT

  The above ID represents that a T is inserted between genomic position 177676 and 177677 on chromosome 2.

##### Deletion example
  	chrM:g.2947878_2947880del

 The above ID represents that a three nucleotides deletion between genomic position 2947878 and 2947880 on chromosome M. Note that we don't include the deleted sequence in the _id field in this case.

##### Deletion/Insertion example
	chrX: g.14112_14117delinsTG

 The above ID represents that six nucleotides between genomic position 14112 and 14117 by TG

#### 2) Top-level **<data_src\>** field
The name of the top-level **<data_src\>** field should be the name of the data source, e.g. ‘clinvar’, ‘dbsnp’, all in lower-cases. Under this top-level field, you can strucutre your annotation in a proper JSON format you like. For example, you can have sub-fields like ‘chromosome’, ‘ref’, ‘alt’, ‘score’ . You can have nested structure if needed. For example, the ‘sift’ field is under 'dbnsfp' top-level **<data_src\>** field, and it contains sub-fields of ‘score’, ‘converted_rankscore’, and ‘pred’.

A typical example of JSON object in MyVariant.info could be found at [src/dataload/sources/dbnsfp/dbnsfp_parser.py](src/dataload/sources/dbnsfp/dbnsfp_parser.py)



## Variant_ID validation

**NOTE** this part of code currently does not work as described, skip this step for now, and we will update the code soon.

In order to make sure all variant IDs loaded into MyVariant.info strictly follows hgvs guidelines, we have developed a variant validation function to validate all variant IDs to be loads. The validation steps are as follows:


### step 1: Call load_data function and get generator of JSON documents


    from dataload.sources.sample_src.sample_src_parser import load_data
    db_generator = load_data(in_file)


### step 2: Call VariantValidator class under src/utils folder


    from utils.validate import VariantValidator
    t = VariantValidator()



### step 3: Run validate_generator function on your generator


    t.validate_generator(db_generator)


or return the correct hgvs id if false example occurred

    t.validate_generator(db_generator, verbose = True)


or return a list of false and none ids

    t.validate_generator(db_generator, return_false = True, return_none = True)


