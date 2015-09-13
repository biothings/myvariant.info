# Generated Mon Mar 30 11:14:08 2015 by generateDS.py version 2.15a.
# Command line:
#   /home/cwu/opt/devpy/bin/generateDS.py -o\
# "clinvar.py" -s "clinvarsubs.py" /home/cwu/Desktop/clinvar_public.xsd
import clinvar

from utils.dataload import unlist, dict_sweep, \
    value_convert, rec_handler


def _map_line_to_json(cp):
    clinical_siginificance = cp.ReferenceClinVarAssertion.\
        ClinicalSignificance.Description
    rcv_accession = cp.ReferenceClinVarAssertion.ClinVarAccession.Acc
    review_status = cp.ReferenceClinVarAssertion.ClinicalSignificance.\
        ReviewStatus
    last_evaluated = cp.ReferenceClinVarAssertion.ClinicalSignificance.\
        DateLastEvaluated
    CLINVAR_ID = cp.ReferenceClinVarAssertion.MeasureSet.ID
    number_submitters = len(cp.ClinVarAssertion)
    # some items in clinvar_xml doesn't have origin information
    try:
        origin = cp.ReferenceClinVarAssertion.ObservedIn[0].Sample.Origin
    except:
        origin = None
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
                print "couldn't find any id", rcv_accession
                return
        else:
            print 'no measure.attribute', rcv_accession
            return
        other_ids = ''
        rsid = None
        # loop through XRef to find rsid as well as other ids
        if Measure.XRef:
            for XRef in Measure.XRef:
                if XRef.Type == 'rs':
                    rsid = 'rs' + str(XRef.ID)
                other_ids = other_ids + XRef.DB + ':' + XRef.ID + ';'
        # make sure the hgvs_id is not none
        if hgvs_id:
            one_snp_json = {

                "_id": hgvs_id,
                "clinvar":
                    {
                        "allele_id": allele_id,
                        "chrom": chrom,
                        "hg19":
                            {
                                "start": chromStart,
                                "end": chromEnd
                            },
                        "type": variation_type,
                        "name": name,
                        "gene":
                            {
                                "id": gene_id,
                                "symbol": symbol
                            },
                        "clinical_significance": clinical_siginificance,
                        "rsid": rsid,
                        "rcv_accession": rcv_accession,
                        "origin": origin,
                        "cytogenic": cytogenic,
                        "review_status": review_status,
                        "hgvs": HGVS,
                        "number_submitters": number_submitters,
                        "last_evaluated": str(last_evaluated),
                        "other_ids": other_ids,
                        "clinvar_id": CLINVAR_ID,
                        "coding_hgvs_only": coding_hgvs_only,
                        "ref": ref,
                        "alt": alt
                    }
                }
            obj = (dict_sweep(unlist(value_convert(one_snp_json)), [None]))
            yield obj


def load_data(input_file):
    # the first two line of clinvar_xml is not useful information
    cv_data = rec_handler(input_file, block_end='</ClinVarSet>\n',
                          skip=2, include_block_end=True)
    print input_file
    for record in cv_data:
        # some exceptions
        if record.startswith('\n</ReleaseSet>'):
            continue
        try:
            record_parsed = clinvar.parseString(record, silence=1)
        except:
            print(record)
            raise
        for record_mapped in _map_line_to_json(record_parsed):
            yield record_mapped
