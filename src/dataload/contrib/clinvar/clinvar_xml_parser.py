# a python lib is generated on the fly, in data folder
# adjust path


import sys, os, glob
from config import DATA_ARCHIVE_ROOT, logger as logging
from biothings.utils.mongo import get_data_folder
DATA_FOLDER = get_data_folder("clinvar")
GLOB_PATTERN = "ClinVarFullRelease_*.xml.gz"

sys.path.insert(0,DATA_FOLDER)

try:
    import clinvar
except ImportError:
    # ok, generate xml parser
    orig_path = os.getcwd()
    try:
        os.chdir(DATA_FOLDER)
        logging.info("Generate XM parser")
        ret = os.system('''generateDS.py -f -o "clinvar_tmp.py" -s "clinvarsubs.py" clinvar_public.xsd''')
        if ret != 0:
            logging.error("Unable to generate parser, return code: %s" % ret)
            raise
        try:
            py = open("clinvar_tmp.py").read()
            # convert py2 to py3 (though they claim it support both versions)
            py = py.replace("from StringIO import StringIO","from io import StringIO")
            fout = open("clinvar.py","w")
            fout.write(py)
            fout.close()
            os.unlink("clinvar_tmp.py")
        except Exception as e:
            logging.error("Cannot convert to py3...")
    finally:
        os.chdir(orig_path)
    # now try again
    import clinvar

logging.info("Found generated clinvar module: %s" % clinvar)

from itertools import groupby

from utils.dataload import unlist, dict_sweep, \
    value_convert, rec_handler


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


def _map_line_to_json(cp):
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
    variant_id = cp.ReferenceClinVarAssertion.MeasureSet.ID
    number_submitters = len(cp.ClinVarAssertion)
    # some items in clinvar_xml doesn't have origin information
    try:
        origin = cp.ReferenceClinVarAssertion.ObservedIn[0].Sample.Origin
    except:
        origin = None
    trait = cp.ReferenceClinVarAssertion.TraitSet.Trait[0]
    synonyms = []
    conditions_name = ''
    for name in trait.Name:
        if name.ElementValue.Type == 'Alternate':
            synonyms.append(name.ElementValue.get_valueOf_())
        if name.ElementValue.Type == 'Preferred':
            conditions_name += name.ElementValue.get_valueOf_()
    identifiers = {}
    for item in trait.XRef:
        if item.DB == 'Human Phenotype Ontology':
            key = 'Human_Phenotype_Ontology'
        else:
            key = item.DB
        identifiers[key.lower()] = item.ID
    for symbol in trait.Symbol:
        if symbol.ElementValue.Type == 'Preferred':
            conditions_name += ' (' + symbol.ElementValue.get_valueOf_() + ')'
    age_of_onset = ''
    for _set in trait.AttributeSet:
        if _set.Attribute.Type == 'age of onset':
            age_of_onset = _set.Attribute.get_valueOf_()

    # MeasureSet.Measure return a list, there might be multiple
    # Measure under one MeasureSet
    for Measure in cp.ReferenceClinVarAssertion.MeasureSet.Measure:
        variation_type = Measure.Type
        # exclude any item of which types belong to
        # 'Variation', 'protein only' or 'Microsatellite'
        if variation_type == 'Variation' or variation_type\
           == 'protein only' or variation_type == 'Microsatellite':
            continue
        allele_id = Measure.ID
        chrom = None
        chromStart = None
        chromEnd = None
        chromStart_38 = None
        chromEnd_38 = None
        ref = None
        alt = None
        if Measure.SequenceLocation:
            for SequenceLocation in Measure.SequenceLocation:
                # In this version, only accept information concerning GRCh37
                if 'GRCh37' in SequenceLocation.Assembly:
                    chrom = SequenceLocation.Chr
                    chromStart = SequenceLocation.start
                    chromEnd = SequenceLocation.stop
                    ref = SequenceLocation.referenceAllele
                    alt = SequenceLocation.alternateAllele
                if 'GRCh38' in SequenceLocation.Assembly:
                    chromStart_38 = SequenceLocation.start
                    chromEnd_38 = SequenceLocation.stop
                    if not ref:
                        ref = SequenceLocation.referenceAllele
                    if not alt:
                        alt = SequenceLocation.alternateAllele
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
                if variation_type == 'single nucleotide variant':
                    hgvs_id = "chr%s:g.%s%s>%s" % (chrom, chromStart, ref, alt)
                # items whose type belong to 'Indel, Insertion, \
                # Duplication' might not hava explicit alt information, \
                # so we will parse from hgvs_genome
                elif variation_type == 'Indel':
                    if hgvs_genome:
                        indel_position = hgvs_genome.find('del')
                        indel_alt = hgvs_genome[indel_position+3:]
                        hgvs_id = "chr%s:g.%s_%sdel%s" % \
                                  (chrom, chromStart, chromEnd, indel_alt)
                elif variation_type == 'Deletion':
                    hgvs_id = "chr%s:g.%s_%sdel" % \
                              (chrom, chromStart, chromEnd)
                elif variation_type == 'Insertion':
                    if hgvs_genome:
                        ins_position = hgvs_genome.find('ins')
                        if 'ins' in hgvs_genome:
                            ins_ref = hgvs_genome[ins_position+3:]
                            hgvs_id = "chr%s:g.%s_%sins%s" % \
                                      (chrom, chromStart, chromEnd, ins_ref)
                elif variation_type == 'Duplication':
                    if hgvs_genome:
                        dup_position = hgvs_genome.find('dup')
                        if 'dup' in hgvs_genome:
                            dup_ref = hgvs_genome[dup_position+3:]
                            hgvs_id = "chr%s:g.%s_%sdup%s" % \
                                      (chrom, chromStart, chromEnd, dup_ref)
            elif variation_type == 'copy number loss' or\
                    variation_type == 'copy number gain':
                if hgvs_genome:
                    hgvs_id = "chr" + hgvs_genome.split('.')[1] +\
                              hgvs_genome.split('.')[2]
            elif hgvs_coding:
                hgvs_id = hgvs_coding
                coding_hgvs_only = True
            else:
                logging.warn("couldn't find any id %s" % rcv_accession)
                return
        else:
            logging.debug('no measure.attribute %s' % rcv_accession)
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
                        "variant_id": variant_id,
                        "chrom": chrom,
                        "omim": omim,
                        "cosmic": cosmic,
                        "uniprot": uniprot,
                        "dbvar": dbvar,
                        "hg19":
                            {
                                "start": chromStart,
                                "end": chromEnd
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
                                "accession": rcv_accession,
                                "clinical_significance": clinical_significance,
                                "number_submitters": number_submitters,
                                "review_status": review_status,
                                "last_evaluated": str(last_evaluated),
                                "preferred_name": name,
                                "origin": origin,
                                "conditions":
                                    {
                                        "name": conditions_name,
                                        "synonyms": synonyms,
                                        "identifiers": identifiers,
                                        "age_of_onset": age_of_onset
                                }
                            },
                        "rsid": rsid,
                        "cytogenic": cytogenic,
                        "hgvs": HGVS,
                        "coding_hgvs_only": coding_hgvs_only,
                        "ref": ref,
                        "alt": alt
                    }
            }
            obj = (dict_sweep(unlist(value_convert(one_snp_json,
                                                   ['chrom', 'omim', 'id', 'orphanet', 'gene',
                                                    'rettbase_(cdkl5)', 'cosmic', 'dbrbc'])), [None, '', 'None']))
            yield obj


def rcv_feeder(input_file):
    # the first two line of clinvar_xml is not useful information
    cv_data = rec_handler(input_file, block_end='</ClinVarSet>\n',
                          skip=2, include_block_end=True)
    for record in cv_data:
        # some exceptions
        if record.startswith('\n</ReleaseSet>'):
            continue
        try:
            record_parsed = clinvar.parseString(record, silence=1)
        except:
            logging.debug(record)
            raise
        for record_mapped in _map_line_to_json(record_parsed):
            yield record_mapped

def load_data():
    files = glob.glob(os.path.join(DATA_FOLDER,GLOB_PATTERN))
    assert len(files) == 1, "Expecting only one file matching '%s', got: %s" % (GLOB_PATTERN,files)
    input_file = files[0]
    data_generator = rcv_feeder(input_file)
    data_list = list(data_generator)
    # TODO: why do we sort this list ? this prevent from using yield/iterator
    data_list_sorted = sorted(data_list, key=lambda k: k['_id'])
    data_merge_rcv = merge_rcv_accession(data_list_sorted)
    return data_merge_rcv
