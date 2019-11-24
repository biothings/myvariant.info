# a python lib is generated on the fly, in data folder
# adjust path


import sys, os, glob
from itertools import groupby

from config import DATA_ARCHIVE_ROOT, logger as logging
import biothings, config
biothings.config_for_app(config)
from biothings.utils.dataload import unlist, dict_sweep, \
                                     value_convert_to_number, rec_handler

GLOB_PATTERN = "ClinVarFullRelease_*.xml.gz"
clinvarlib = None

def import_clinvar_lib(data_folder):
    sys.path.insert(0,data_folder)
    import genclinvar as clinvar_mod
    global clinvarlib
    clinvarlib = clinvar_mod

def merge_rcv_accession(generator):
    groups = []
    for key, group in groupby(generator, lambda x: x['_id']):
        groups.append(list(group))

    # get the number of groups, and uniquekeys
    logging.info("number of groups: %s" % len(groups))

    # loop through each item, if item number >1, merge rcv accession number
    for item in groups:
        rcv_new = []
        if len(item) > 1:
            json_item = item[0]
            for _item in item:
                    rcv_info = _item['clinvar']['rcv']
                    rcv_new.append(rcv_info)
            json_item['clinvar']['rcv'] = rcv_new
            yield json_item
        else:
            yield item[0]


def parse_measure(Measure, hg19=True):
    variation_type = Measure.Type
    # exclude any item of which types belong to
    # 'Variation', 'protein only' or 'Microsatellite'
    if variation_type == 'Variation' or variation_type == 'protein only' or variation_type == 'Microsatellite':
        return None
    allele_id = Measure.ID
    chrom = None
    chromStart_19 = None
    chromEnd_19 = None
    chromStart_38 = None
    chromEnd_38 = None
    ref = None
    alt = None
    if Measure.SequenceLocation:
        for SequenceLocation in Measure.SequenceLocation:
            # In this version, only accept information concerning GRCh37
            if 'GRCh37' in SequenceLocation.Assembly:
                chrom = SequenceLocation.Chr
                chromStart_19 = SequenceLocation.start
                chromEnd_19 = SequenceLocation.stop
                if not ref:
                    ref = SequenceLocation.referenceAllele
                if not ref:
                    ref = SequenceLocation.referenceAlleleVCF
                if not alt:
                    alt = SequenceLocation.alternateAllele
                if not alt:
                    alt = SequenceLocation.alternateAlleleVCF
            if 'GRCh38' in SequenceLocation.Assembly:
                chromStart_38 = SequenceLocation.start
                chromEnd_38 = SequenceLocation.stop
                if not ref:
                    ref = SequenceLocation.referenceAllele
                if not ref:
                    ref = SequenceLocation.referenceAlleleVCF
                if not alt:
                    alt = SequenceLocation.alternateAllele
                if not alt:
                    alt = SequenceLocation.alternateAlleleVCF
    if Measure.MeasureRelationship:
        try:
            symbol = Measure.MeasureRelationship[0].\
                Symbol[0].get_ElementValue().valueOf_
        except:
            symbol = None
        gene_id = Measure.MeasureRelationship[0].XRef[0].ID
    else:
        symbol = None
        gene_id = None
    if Measure.Name:
        name = Measure.Name[0].ElementValue.valueOf_
    else:
        name = None
    if len(Measure.CytogeneticLocation) == 1:
        cytogenic = Measure.CytogeneticLocation[0]
    else:
        cytogenic = Measure.CytogeneticLocation
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
    if Measure.AttributeSet:
        # 'copy number loss' or 'gain' have format different\
        # from other types, should be dealt with seperately
        if (variation_type == 'copy number loss') or \
                (variation_type == 'copy number gain'):
            for AttributeSet in Measure.AttributeSet:
                if 'HGVS, genomic, top level' in AttributeSet.\
                        Attribute.Type:
                    if AttributeSet.Attribute.integerValue == 37:
                        hgvs_genome = AttributeSet.Attribute.get_valueOf_()
                if 'genomic' in AttributeSet.Attribute.Type:
                    HGVS['genomic'].append(AttributeSet.Attribute.
                                           get_valueOf_())
                elif 'non-coding' in AttributeSet.Attribute.Type:
                    HGVS['non-coding'].append(AttributeSet.Attribute.
                                              get_valueOf_())
                elif 'coding' in AttributeSet.Attribute.Type:
                    HGVS['coding'].append(AttributeSet.Attribute.
                                          get_valueOf_())
                elif 'protein' in AttributeSet.Attribute.Type:
                    HGVS['protein'].append(AttributeSet.
                                           Attribute.get_valueOf_())
        else:
            for AttributeSet in Measure.AttributeSet:
                if 'genomic' in AttributeSet.Attribute.Type:
                    HGVS['genomic'].append(AttributeSet.
                                           Attribute.get_valueOf_())
                elif 'non-coding' in AttributeSet.Attribute.Type:
                    HGVS['non-coding'].append(AttributeSet.
                                              Attribute.get_valueOf_())
                elif 'coding' in AttributeSet.Attribute.Type:
                    HGVS['coding'].append(AttributeSet.Attribute.
                                          get_valueOf_())
                elif 'protein' in AttributeSet.Attribute.Type:
                    HGVS['protein'].append(AttributeSet.
                                           Attribute.get_valueOf_())
                if AttributeSet.Attribute.Type == 'HGVS, coding, RefSeq':
                    hgvs_coding = AttributeSet.Attribute.get_valueOf_()
                elif AttributeSet.Attribute.Type == \
                        'HGVS, genomic, top level, previous':
                    hgvs_genome = AttributeSet.Attribute.get_valueOf_()
                    break
        if chrom and chromStart and chromEnd:
            # if its SNP, make sure chrom, chromStart, chromEnd, ref, alt are all provided
            if variation_type == 'single nucleotide variant':
                if ref and alt:
                    hgvs_id = "chr%s:g.%s%s>%s" % (chrom, chromStart, ref, alt)
                else:
                    print('hgvs not found chr {}, chromStart {}, chromEnd {}, ref {}, alt {}, allele id {}'.format(chrom, chromStart, chromEnd, ref, alt, allele_id))
            # items whose type belong to 'Indel, Insertion, \
            # Duplication' might not hava explicit alt information, \
            # so we will parse from hgvs_genome
            elif variation_type == 'Indel':
            # RCV000156073, NC_000010.10:g.112581638_112581639delinsG
                if hgvs_genome:
                    indel_position = hgvs_genome.find('del')
                    indel_alt = hgvs_genome[indel_position+3:]
                    hgvs_id = "chr%s:g.%s_%sdel%s" % \
                              (chrom, chromStart, chromEnd, indel_alt)
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
                            hgvs_id = "chr%s:g.%sins%s" % \
                                      (chrom, chromStart, ins_ref)
                        else:
                            hgvs_id = "chr%s:g.%s_%sins%s" % \
                                      (chrom, chromStart, chromEnd, ins_ref)
            elif variation_type == 'Duplication':
                if hgvs_genome:
                    dup_position = hgvs_genome.find('dup')
                    if 'dup' in hgvs_genome:
                        dup_ref = hgvs_genome[dup_position+3:]
                        if chromStart == chromEnd:
                            hgvs_id = "chr%s:g.%sdup%s" % \
                                  (chrom, chromStart, dup_ref)
                        else:
                            hgvs_id = "chr%s:g.%s_%sdup%s" % \
                                  (chrom, chromStart, chromEnd, dup_ref)
        elif variation_type == 'copy number loss' or\
                variation_type == 'copy number gain':
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
    if Measure.XRef:
        for XRef in Measure.XRef:
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
            "clinvar":
                {
                    "allele_id": allele_id,
                    "chrom": chrom,
                    "omim": omim,
                    "cosmic": cosmic,
                    "uniprot": uniprot,
                    "dbvar": dbvar,
                    "hg19":
                        {
                            "start": chromStart_19,
                            "end": chromEnd_19
                        },
                    "hg38":
                        {
                            "start": chromStart_38,
                            "end": chromEnd_38
                        },
                    "type": variation_type,
                    "gene":
                        {
                            "id": gene_id,
                            "symbol": symbol
                        },
                    "rcv":
                        {
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

def _map_line_to_json(cp, hg19):
    try:
        clinical_significance = cp.ReferenceClinVarAssertion.\
            ClinicalSignificance.Description
    except:
        clinical_significance = None
    rcv_accession = cp.ReferenceClinVarAssertion.ClinVarAccession.Acc
    try:
        review_status = cp.ReferenceClinVarAssertion.ClinicalSignificance.\
            ReviewStatus
    except:
        review_status = None
    try:
        last_evaluated = cp.ReferenceClinVarAssertion.ClinicalSignificance.\
            DateLastEvaluated
    except:
        last_evaluated = None
    
    number_submitters = len(cp.ClinVarAssertion)
    # some items in clinvar_xml doesn't have origin information
    try:
        origin = cp.ReferenceClinVarAssertion.ObservedIn[0].Sample.Origin
    except:
        origin = None
    conditions = []
    for _trait in cp.ReferenceClinVarAssertion.TraitSet.Trait:
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
        conditions.append({"name": conditions_name, "synonyms": synonyms, "identifiers": identifiers, "age_of_onset": age_of_onset})

    try:
        genotypeset = cp.ReferenceClinVarAssertion.GenotypeSet
    except:
        genotypeset = None
    if genotypeset:
        obj_list = []
        id_list = []
        for _set in cp.ReferenceClinVarAssertion.GenotypeSet.MeasureSet:
            variant_id = _set.ID
            for _measure in _set.Measure:
                json_obj = parse_measure(_measure, hg19=hg19)
                if json_obj:
                    json_obj['clinvar']['rcv'].update({'accession': rcv_accession,
                        'clinical_significance': clinical_significance,
                        'number_submitters': number_submitters,
                        'review_status': review_status,
                        'last_evaluated': str(last_evaluated),
                        'origin': origin,
                        'conditions': conditions})
                    json_obj['clinvar'].update({'variant_id': variant_id})
                    json_obj = (dict_sweep(unlist(value_convert_to_number(json_obj,
                                               ['chrom', 'omim', 'id', 'orphanet', 'gene',
                                                'rettbase_(cdkl5)', 'cosmic', 'dbrbc'])), [None, '', 'None']))
                    obj_list.append(json_obj)
                    id_list.append(json_obj['_id'])
        for _obj in obj_list:
            _obj['clinvar'].update({'genotypeset': {
                    'type': 'CompoundHeterozygote',
                    'genotype': id_list
                    }})
            yield _obj
    else:
        variant_id = cp.ReferenceClinVarAssertion.MeasureSet.ID
        for _measure in cp.ReferenceClinVarAssertion.MeasureSet.Measure:
            json_obj = parse_measure(_measure, hg19=hg19)
            if json_obj:
                json_obj['clinvar']['rcv'].update({'accession': rcv_accession,
                        'clinical_significance': clinical_significance,
                        'number_submitters': number_submitters,
                        'review_status': review_status,
                        'last_evaluated': str(last_evaluated),
                        'origin': origin,
                        'conditions': conditions})
                json_obj['clinvar'].update({'variant_id': variant_id})
                json_obj = (dict_sweep(unlist(value_convert_to_number(json_obj,
                                               ['chrom', 'omim', 'id', 'orphanet', 'gene',
                                                'rettbase_(cdkl5)', 'cosmic', 'dbrbc'])), [None, '', 'None']))
                yield json_obj


def rcv_feeder(input_file, hg19):
    # the first two line of clinvar_xml is not useful information
    cv_data = rec_handler(input_file, block_end='</ClinVarSet>\n',
                          skip=2, include_block_end=True)
    for record in cv_data:
        # some exceptions
        if record.startswith('\n</ReleaseSet>'):
            continue
        try:
            record_parsed = clinvarlib.parseString(record, silence=1)
        except:
            logging.debug(record)
            raise
        for record_mapped in _map_line_to_json(record_parsed, hg19):
            yield record_mapped

def load_data(data_folder, version):
    # try to get logger from uploader
    import logging as loggingmod
    global logging
    logging = loggingmod.getLogger("clinvar_upload")

    import_clinvar_lib(data_folder)
    files = glob.glob(os.path.join(data_folder,GLOB_PATTERN))
    assert len(files) == 1, "Expecting only one file matching '%s', got: %s" % (GLOB_PATTERN,files)
    input_file = files[0]
    data_generator = rcv_feeder(input_file, version == "hg19")
    data_list = list(data_generator)
    # TODO: why do we sort this list ? this prevent from using yield/iterator
    data_list_sorted = sorted(data_list, key=lambda k: k['_id'])
    data_merge_rcv = merge_rcv_accession(data_list_sorted)
    return data_merge_rcv

if __name__ == "__main__":
    from biothings.utils.mongo import get_data_folder
    data_folder = get_data_folder("clinvar")
    load_data(data_folder=data_folder)
