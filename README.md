Introduction
-------------

This is a project coming out of [1st NoB Hackathon](https://github.com/Network-of-BioThings/nob-hq/wiki/1st-Network-of-BioThings-Hackathon).

The scope of this project is to aggregate existing annotations for genetic variants. Variant annotations have drawn huge amount of efforts from researchers, which made many variant annotation resources available, but also very scattered. Doing integration of all of them is hard, so we want to create a simple way to pool them together first, with high-performance programmatic access. That way, the further integration (e.g. deduplication, deriving higher-level annotations, etc) can be much easier.

From the discussion of the hackathon, we decided a strategy summarized as below:

##### A very simple rule to aggregate variant annotations
  * each variant is represented as a JSON document
  * the only requirement of the JSON document is that the key of this JSON document ("_id" field in this document) follows [HGVS nomenclature](http://www.hgvs.org/mutnomen/recs-DNA.html). For example:

   ```javascript
        {
          '_id': 'chr1:g.35366C>T',
          'allele1': 'C',
          'allele2': 'T',
          'chrom': 'chr1',
          'chromEnd': 35367,
          'chromStart': 35366,
          'func': 'unknown',
          'rsid': 'rs71409357',
          'snpclass': 'single',
          'strand': '-'
        }
  ```
  * that way, we can then merge multiple annotations for the same variant into a merged JSON document. Each resource of annotations is under its own field. Here is [a merged example](https://gist.github.com/newgene/9251a2036918caea694c).
  
  
##### A powerful query-engine to access/query aggregated annotations

  The query engine we developed for [MyGene.info](http://mygene.info) can be easily adapted to provide the high-performance and flexible query interface for programmatic access. [MyGene.info](http://mygene.info) follows the same spirit, but for gene annotations. It currently serves ~3M request per month.
  
##### User contributions of variant annotations

  User contribution is vital, given the scale of avaialble (also increasing) resources. The simple rule we defined above makes the merging new annotation resource very easy, essentially writing a JSON importer. And the sophisticated query-engine we built can save users effort to build their own infrastructure, which provides the incentive for them to contribute.
  
  Also note that it's not neccesary the data-provider can write the importer, anyone who finds a useful resource can do that as well (of course, check to make sure the data release license allows that)

  See the guideline below for contributing JSON importer.
  
How to contribute
------------------

If you have/find a variant annotation resource you want to included in our system, you can following the guideline below to contribute a JSON importer (let's call it "**data plugin**") for it.

* Code in Python (at least for now)
* Using hg19 genome assembly for genomic cordinates (assuming we are dealing with human variants for now)
* all data plugins is under *[src/dataload/contrib](https://github.com/Network-of-BioThings/myvariant.info/tree/master/src/dataload/contrib)* folder.
* check out the example *[src/dataload/contrib/cosmic](https://github.com/Network-of-BioThings/myvariant.info/tree/master/src/dataload/contrib/cosmic)* for loading cosmic data from UCSC server. The following should be defined:
  * **load_data** function: the output of this function should be either a **list** or **[generator](https://wiki.python.org/moin/Generators)** of JSON documents. A **generator** is ideal for large lists won't fit into memeory. For example, [*cosmic*](https://github.com/Network-of-BioThings/myvariant.info/tree/master/src/dataload/contrib/cosmic) example above uses generator. See [requirements/example](#a-very-simple-rule-to-aggregate-variant-annotations) above for each JSON document.
  * **Meta** dictionary: you can put some metadata like "maintainer", "requirements", etc. Note that "requirements" is a list of strings follows [pip requirements.txt format](https://pip.pypa.io/en/1.1/requirements.html).
  * **get_mapping** function: optional, this can be used to customize the indexing. You can just leave it empty.
* fork this repo, and add your own data plugin (under a subfolder, like *cosmic* example), commit and send the pull request.
* And the last, if you have trouble to code a data plugin, you can just produce a dump of JSON document list using whatever tools you like, and send over your dumped file to us. But that will require us to load it manually.
