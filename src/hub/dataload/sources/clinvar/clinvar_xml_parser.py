"""
Two major parsing functions in this script are:

    1. `clinvar_doc_feeder()`
    2. `merge_rcv_accession()`

`clinvar_doc_feeder()` is responsible for the following jobs:

    1. Receive a ClinVarFullRelease_*.xml.gz file, and split the xml file into `<ClinVarSet>...</ClinVarSet>` blocks
    2. Parse each `<ClinVarSet>...</ClinVarSet>` block into an `PublicSetType` object, which is defined in the
        dynamically imported `clinvarlib`
    3. Convert each `PublicSetType` object into a clinvar document

Note that The `PublicSetType` class is defined to map the block structure of `<ClinVarSet>`, which can be inspected
through its XSD, https://ftp.ncbi.nlm.nih.gov/pub/clinvar/clinvar_public.xsd.

`merge_rcv_accession()` is responsible for only one job:

    1. Group all the document by `doc['_id']`, and then inside each group, merge all the `doc['clinvar']['rcv']`.
        Each group of documents will be merged into a single document.
"""

import glob
import os
import sys
from itertools import groupby

import biothings
import config
biothings.config_for_app(config)

from biothings.utils.dataload import unlist, dict_sweep, value_convert_to_number, rec_handler

GLOB_PATTERN = "ClinVarFullRelease_*.xml.gz"
clinvarlib = None


def import_clinvar_lib(data_folder):
    # a python lib is generated on the fly, in data folder
    sys.path.insert(0, data_folder)
    import genclinvar as clinvar_mod
    global clinvarlib
    clinvarlib = clinvar_mod


def merge_rcv_accession(docs):
    doc_groups = []
    for key, group in groupby(docs, lambda x: x['_id']):
        doc_groups.append(list(group))

    # get the number of groups, and unique keys
    logging.info("number of groups: %s" % len(doc_groups))

    # Each group is a list of documents
    # Loop through each group, if doc number >1, merge rcv accessions
    for doc_list in doc_groups:
        if len(doc_list) == 1:
            yield doc_list[0]
        else:
            rcv_list = [doc['clinvar']['rcv'] for doc in doc_list]
            
            merged_doc = doc_list[0]
            merged_doc['clinvar']['rcv'] = rcv_list
            yield merged_doc


def _map_measure_to_json(measure_obj, hg19=True):
    """
    Convert a `clinvarlib.MeasureType` object into json.

    Each `clinvarlib.MeasureType` object is mapped to a `<Measure>` block in the XML, which is part of the hierarchy
    below:

        <ClinVarSet ...>
          <ReferenceClinVarAssertion ...>
            <MeasureSet ...>
              <Measure ...> ... </Measure>
              <Measure ...> ... </Measure>
              ...
            </MeasureSet>
          </ReferenceClinVarAssertion>
        </ClinVarSet>
    """
    
    # exclude any item of which types belong to 'Variation', 'protein only' or 'Microsatellite'
    variation_type = measure_obj.Type
    if variation_type == 'Variation' or variation_type == 'protein only' or variation_type == 'Microsatellite':
        return None

    allele_id = measure_obj.ID

    chrom = None
    chromStart_19, chromEnd_19, chromStart_38, chromEnd_38 = None, None, None, None
    ref, alt = None, None
    if measure_obj.SequenceLocation:
        for SequenceLocation in measure_obj.SequenceLocation:
            if 'GRCh37' in SequenceLocation.Assembly:
                chrom = SequenceLocation.Chr
                chromStart_19 = SequenceLocation.start
                chromEnd_19 = SequenceLocation.stop
                if not ref:
                    ref = SequenceLocation.referenceAllele or SequenceLocation.referenceAlleleVCF
                if not alt:
                    alt = SequenceLocation.alternateAllele or SequenceLocation.alternateAlleleVCF

            if 'GRCh38' in SequenceLocation.Assembly:
                chromStart_38 = SequenceLocation.start
                chromEnd_38 = SequenceLocation.stop
                if not ref:
                    ref = SequenceLocation.referenceAllele or SequenceLocation.referenceAlleleVCF
                if not alt:
                    alt = SequenceLocation.alternateAllele or SequenceLocation.alternateAlleleVCF

    symbol = None
    gene_id = None
    if measure_obj.MeasureRelationship:
        try:
            symbol = measure_obj.MeasureRelationship[0].Symbol[0].get_ElementValue().valueOf_
        except:
            symbol = None
        gene_id = measure_obj.MeasureRelationship[0].XRef[0].ID

    name = None
    if measure_obj.Name:
        name = measure_obj.Name[0].ElementValue.valueOf_

    if len(measure_obj.CytogeneticLocation) == 1:
        cytogenic = measure_obj.CytogeneticLocation[0]
    else:
        cytogenic = measure_obj.CytogeneticLocation

    hgvs_coding = None
    hgvs_genome = None
    HGVS = {'genomic': [], 'coding': [], 'non-coding': [], 'protein': []}
    coding_hgvs_only = None
    hgvs_id = None
    if hg19:
        chromStart = chromStart_19
        chromEnd = chromEnd_19
    else:
        chromStart = chromStart_38
        chromEnd = chromEnd_38

    # hgvs_not_validated = None
    if measure_obj.AttributeSet:
        # 'copy number loss' or 'gain' have format different\
        # from other types, should be dealt with seperately
        if (variation_type == 'copy number loss') or (variation_type == 'copy number gain'):
            for AttributeSet in measure_obj.AttributeSet:
                if 'HGVS, genomic, top level' in AttributeSet.Attribute.Type:
                    if AttributeSet.Attribute.integerValue == 37:
                        hgvs_genome = AttributeSet.Attribute.get_valueOf_()

                if 'genomic' in AttributeSet.Attribute.Type:
                    HGVS['genomic'].append(AttributeSet.Attribute.get_valueOf_())
                elif 'non-coding' in AttributeSet.Attribute.Type:
                    HGVS['non-coding'].append(AttributeSet.Attribute.get_valueOf_())
                elif 'coding' in AttributeSet.Attribute.Type:
                    HGVS['coding'].append(AttributeSet.Attribute.get_valueOf_())
                elif 'protein' in AttributeSet.Attribute.Type:
                    HGVS['protein'].append(AttributeSet.Attribute.get_valueOf_())
        else:
            for AttributeSet in measure_obj.AttributeSet:
                if 'genomic' in AttributeSet.Attribute.Type:
                    HGVS['genomic'].append(AttributeSet.Attribute.get_valueOf_())
                elif 'non-coding' in AttributeSet.Attribute.Type:
                    HGVS['non-coding'].append(AttributeSet.Attribute.get_valueOf_())
                elif 'coding' in AttributeSet.Attribute.Type:
                    HGVS['coding'].append(AttributeSet.Attribute.get_valueOf_())
                elif 'protein' in AttributeSet.Attribute.Type:
                    HGVS['protein'].append(AttributeSet.Attribute.get_valueOf_())

                if not hgvs_coding and AttributeSet.Attribute.Type == 'HGVS, coding, RefSeq':
                    hgvs_coding = AttributeSet.Attribute.get_valueOf_()
                if not hgvs_genome and AttributeSet.Attribute.Type == 'HGVS, genomic, top level, previous':
                    hgvs_genome = AttributeSet.Attribute.get_valueOf_()

        if chrom and chromStart and chromEnd:
            # if its SNP, make sure chrom, chromStart, chromEnd, ref, alt are all provided
            if variation_type == 'single nucleotide variant':
                if ref and alt:
                    hgvs_id = "chr%s:g.%s%s>%s" % (chrom, chromStart, ref, alt)
                else:
                    print('hgvs not found chr {}, chromStart {}, chromEnd {}, ref {}, alt {}, allele id {}'.
                          format(chrom, chromStart, chromEnd, ref, alt, allele_id))
            # items whose type belong to 'Indel, Insertion, \
            # Duplication' might not hava explicit alt information, \
            # so we will parse from hgvs_genome
            elif variation_type == 'Indel':
                # RCV000156073, NC_000010.10:g.112581638_112581639delinsG
                if hgvs_genome:
                    indel_position = hgvs_genome.find('del')
                    indel_alt = hgvs_genome[indel_position+3:]
                    hgvs_id = "chr%s:g.%s_%sdel%s" % (chrom, chromStart, chromEnd, indel_alt)
            elif variation_type == 'Deletion':
                if chromStart == chromEnd:
                    # RCV000048406, chr17:g.41243547del
                    hgvs_id = "chr%s:g.%sdel" % (chrom, chromStart)
                else:
                    hgvs_id = "chr%s:g.%s_%sdel" % (chrom, chromStart, chromEnd)
            elif variation_type == 'Insertion':
                if hgvs_genome:
                    ins_position = hgvs_genome.find('ins')
                    if 'ins' in hgvs_genome:
                        ins_ref = hgvs_genome[ins_position+3:]
                        if chromStart == chromEnd:
                            hgvs_id = "chr%s:g.%sins%s" % (chrom, chromStart, ins_ref)
                        else:
                            hgvs_id = "chr%s:g.%s_%sins%s" % (chrom, chromStart, chromEnd, ins_ref)
            elif variation_type == 'Duplication':
                if hgvs_genome:
                    dup_position = hgvs_genome.find('dup')
                    if 'dup' in hgvs_genome:
                        dup_ref = hgvs_genome[dup_position+3:]
                        if chromStart == chromEnd:
                            hgvs_id = "chr%s:g.%sdup%s" % (chrom, chromStart, dup_ref)
                        else:
                            hgvs_id = "chr%s:g.%s_%sdup%s" % (chrom, chromStart, chromEnd, dup_ref)
        elif variation_type == 'copy number loss' or variation_type == 'copy number gain':
            if hgvs_genome and chrom:
                hgvs_id = "chr" + chrom + ":" + hgvs_genome.split('.')[2]
        elif hgvs_coding:
            hgvs_id = hgvs_coding
            coding_hgvs_only = True
        else:
            return
    else:
        return

    for key in HGVS:
        HGVS[key].sort()

    rsid = None
    cosmic = None
    dbvar = None
    uniprot = None
    omim = None
    # loop through XRef to find rsid as well as other ids
    if measure_obj.XRef:
        for XRef in measure_obj.XRef:
            if XRef.Type == 'rs':
                rsid = 'rs' + str(XRef.ID)
            elif XRef.DB == 'COSMIC':
                cosmic = XRef.ID
            elif XRef.DB == 'OMIM':
                omim = XRef.ID
            elif XRef.DB == 'UniProtKB/Swiss-Prot':
                uniprot = XRef.ID
            elif XRef.DB == 'dbVar':
                dbvar = XRef.ID

    # make sure the hgvs_id is not none
    if hgvs_id:
        one_snp_json = {
            "_id": hgvs_id,
            "clinvar": {
                "allele_id": allele_id,
                "chrom": chrom,
                "omim": omim,
                "cosmic": cosmic,
                "uniprot": uniprot,
                "dbvar": dbvar,
                "hg19": {
                    "start": chromStart_19,
                    "end": chromEnd_19
                },
                "hg38": {
                    "start": chromStart_38,
                    "end": chromEnd_38
                },
                "type": variation_type,
                "gene": {
                    "id": gene_id,
                    "symbol": symbol
                },
                "rcv": {
                    "preferred_name": name,
                },
                "rsid": rsid,
                "cytogenic": cytogenic,
                "hgvs": HGVS,
                "coding_hgvs_only": coding_hgvs_only,
                "ref": ref,
                "alt": alt
            }
        }

        return one_snp_json


def _map_public_set_to_json(public_set_obj, hg19: bool):
    """
    Convert a `clinvarlib.PublicSetType` object into a json document.

    Each `clinvarlib.PublicSetType` object is mapped to a `<ClinVarSet>` block in the XML.

    E.g., `public_set_obj.ReferenceClinVarAssertion.MeasureSet` is the parsed value from a block structure below:

        <ClinVarSet ...>
          <ReferenceClinVarAssertion ...>
            <MeasureSet ...>
              ...
            </MeasureSet>
          </ReferenceClinVarAssertion>
        </ClinVarSet>
    """
    try:
        clinical_significance = public_set_obj.ReferenceClinVarAssertion.ClinicalSignificance.Description
    except:
        clinical_significance = None

    rcv_accession = public_set_obj.ReferenceClinVarAssertion.ClinVarAccession.Acc

    try:
        review_status = public_set_obj.ReferenceClinVarAssertion.ClinicalSignificance.ReviewStatus
    except:
        review_status = None

    try:
        last_evaluated = public_set_obj.ReferenceClinVarAssertion.ClinicalSignificance.DateLastEvaluated
    except:
        last_evaluated = None
    
    number_submitters = len(public_set_obj.ClinVarAssertion)

    # some items in clinvar_xml doesn't have origin information
    try:
        origin = public_set_obj.ReferenceClinVarAssertion.ObservedIn[0].Sample.Origin
    except:
        origin = None

    conditions = []
    for _trait in public_set_obj.ReferenceClinVarAssertion.TraitSet.Trait:
        synonyms = []
        conditions_name = ''
        for name in _trait.Name:
            if name.ElementValue.Type == 'Alternate':
                synonyms.append(name.ElementValue.get_valueOf_())
            if name.ElementValue.Type == 'Preferred':
                conditions_name += name.ElementValue.get_valueOf_()

        identifiers = {}
        for item in _trait.XRef:
            if item.DB == 'Human Phenotype Ontology':
                key = 'Human_Phenotype_Ontology'
            else:
                key = item.DB
            identifiers[key.lower()] = item.ID
        for symbol in _trait.Symbol:
            if symbol.ElementValue.Type == 'Preferred':
                conditions_name += ' (' + symbol.ElementValue.get_valueOf_() + ')'

        age_of_onset = ''
        for _set in _trait.AttributeSet:
            if _set.Attribute.Type == 'age of onset':
                age_of_onset = _set.Attribute.get_valueOf_()

        conditions.append({"name": conditions_name, "synonyms": synonyms, "identifiers": identifiers,
                           "age_of_onset": age_of_onset})

    try:
        genotypeset = public_set_obj.ReferenceClinVarAssertion.GenotypeSet
    except:
        genotypeset = None

    if genotypeset:
        obj_list = []
        id_list = []
        for _set in public_set_obj.ReferenceClinVarAssertion.GenotypeSet.MeasureSet:
            variant_id = _set.ID
            for _measure in _set.Measure:
                json_obj = _map_measure_to_json(_measure, hg19=hg19)
                if json_obj:
                    json_obj['clinvar']['rcv'].update({
                        'accession': rcv_accession,
                        'clinical_significance': clinical_significance,
                        'number_submitters': number_submitters,
                        'review_status': review_status,
                        'last_evaluated': str(last_evaluated),
                        'origin': origin,
                        'conditions': conditions
                    })
                    json_obj['clinvar'].update({'variant_id': variant_id})
                    json_obj = (dict_sweep(unlist(value_convert_to_number(json_obj,
                                ['chrom', 'omim', 'id', 'orphanet', 'gene', 'rettbase_(cdkl5)', 'cosmic', 'dbrbc'])),
                                [None, '', 'None']))
                    obj_list.append(json_obj)
                    id_list.append(json_obj['_id'])
        for _obj in obj_list:
            _obj['clinvar'].update({'genotypeset': {
                'type': 'CompoundHeterozygote',
                'genotype': id_list
            }})
            yield _obj
    else:
        variant_id = public_set_obj.ReferenceClinVarAssertion.MeasureSet.ID
        for _measure in public_set_obj.ReferenceClinVarAssertion.MeasureSet.Measure:
            json_obj = _map_measure_to_json(_measure, hg19=hg19)
            if json_obj:
                json_obj['clinvar']['rcv'].update({
                    'accession': rcv_accession,
                    'clinical_significance': clinical_significance,
                    'number_submitters': number_submitters,
                    'review_status': review_status,
                    'last_evaluated': str(last_evaluated),
                    'origin': origin,
                    'conditions': conditions
                })
                json_obj['clinvar'].update({'variant_id': variant_id})
                json_obj = (dict_sweep(unlist(value_convert_to_number(json_obj,
                                               ['chrom', 'omim', 'id', 'orphanet', 'gene',
                                                'rettbase_(cdkl5)', 'cosmic', 'dbrbc'])), [None, '', 'None']))
                yield json_obj


def clinvar_doc_feeder(input_file, hg19: bool):
    """
    This function will split the xml file into `<ClinVarSet>...</ClinVarSet>` blocks, then parse each block into an
    `PublicSetType` object (which is defined in the dynamically imported `clinvarlib`), and finally convert each
    `PublicSetType` object into a clinvar document.
    """

    """
    A ClinVarFullRelease_*.xml.gz file has the following structure:
    
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <ReleaseSet Dated="2021-06-26" ...>

            <ClinVarSet ID="38756179">
              ...
            </ClinVarSet>
            
            <ClinVarSet ID="38756180">
              ...
            </ClinVarSet>
            
            ...

        </ReleaseSet>
    
    Therefore when splitting the xml into `<ClinVarSet>` blocks, the first 2 lines and the last 1 line should be 
    skipped. 
    
    However the `rec_handler` function cannot skip the last 1 line, and will return "\n</ReleaseSet>...</ClinVarSet>" as 
    the last block in this scenario. Therefore in the for-loop below, we will skip any block starting with 
    "\n</ReleaseSet>".
    """
    clinvar_set_blocks = rec_handler(input_file, block_end='</ClinVarSet>\n', skip=2, include_block_end=True)
    for clinvar_set_block in clinvar_set_blocks:
        # Skip any block starting with "\n</ReleaseSet>"
        # Actually only the last block will be skipped. See comments above
        if clinvar_set_block.startswith('\n</ReleaseSet>'):
            continue

        try:
            # Parse each `<ClinVarSet>` block into a `clinvarlib.PublicSetType` object
            public_set_obj = clinvarlib.parseString(clinvar_set_block, silence=1)
        except:
            logging.debug(clinvar_set_block)
            raise

        # Convert each `clinvarlib.PublicSetType` object into a json document
        for doc in _map_public_set_to_json(public_set_obj, hg19):
            yield doc


def load_data(data_folder, version):
    # try to get logger from uploader
    import logging as loggingmod
    global logging
    logging = loggingmod.getLogger("clinvar_upload")

    import_clinvar_lib(data_folder)

    files = glob.glob(os.path.join(data_folder, GLOB_PATTERN))
    assert len(files) == 1, "Expecting only one file matching '%s', got: %s" % (GLOB_PATTERN, files)
    input_file = files[0]

    doc_generator = clinvar_doc_feeder(input_file, hg19=(version == "hg19"))

    # Sorting is necessary because `merge_rcv_accession` will call `itertools.groupby()`
    #   which cannot put non-adjacent items with the same key into a group
    doc_list = list(doc_generator)
    doc_list = sorted(doc_list, key=lambda k: k['_id'])

    merged_doc_generator = merge_rcv_accession(doc_list)
    return merged_doc_generator


if __name__ == "__main__":
    from biothings.utils.mongo import get_data_folder
    data_folder = get_data_folder("clinvar")
    load_data(data_folder=data_folder, version="hg19")
