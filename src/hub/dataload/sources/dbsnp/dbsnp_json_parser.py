from utils.hgvs import get_hgvs_from_vcf, get_pos_start_end
from biothings.utils.dataload import dict_sweep, unlist, value_convert_to_number


def parse_one_rec(assembly, record):
    """Restructure JSON
    """
    doc = {"alleles": [], "gene": [],
           assembly: {},
           "vartype": record.get("primary_snapshot_data").get("variant_type"),
           "rsid": "rs" + str(record.get("refsnp_id")),
           "dbsnp_build": int(record.get("last_update_build_id")),
           "dbsnp_merges": restructure_dbsnp_merge(record.get("dbsnp1_merges")),
           "citations": record.get("citations")}
    data = record.get('primary_snapshot_data')
    hgvs, vcf = get_hgvs_and_vcf(assembly, data.get("placements_with_allele"))
    doc["_id"] = hgvs
    doc["chrom"], pos, doc["ref"], doc["alt"] = vcf
    try:
        doc[assembly]['start'], doc[assembly]['end'] = get_pos_start_end(doc["chrom"], pos, doc["ref"], doc["alt"])
    except ValueError:
        doc[assembly] = {}
    allele_annotations = data.get('allele_annotations')
    allele_annotations = list(allele_annotations)
    doc["alleles"] = restructure_allele_freq_info(allele_annotations)
    doc['gene'] = restructure_gene_info(allele_annotations)
    return dict_sweep(unlist(value_convert_to_number(doc)), vals=[[], {}, None])


def restructure_allele_freq_info(allele_annotations):
    """Restructure information related to allele frequency
    """
    alleles_data = []
    for _annotation in allele_annotations:
        freq_data = _annotation.get('frequency')
        if freq_data:
            freq = {}
            freq_data = list(freq_data)
            for _doc in freq_data:
                if _doc:
                    freq['allele'] = _doc.get('observation').get('inserted_sequence')
                    freq[_doc.get('study_name')] = round(_doc.get('allele_count')/_doc.get('total_count'), 3)
            alleles_data.append(freq)
    return alleles_data


def restructure_gene_info(allele_annotations):
    """Restructure information related to gene
    """
    gene_data = []
    assembly_annotation = allele_annotations[0].get('assembly_annotation')
    if assembly_annotation[0]:
        for _doc in assembly_annotation[0].get('genes'):
            if _doc:
                _doc['geneid'] = _doc.pop('id')
                _doc['symbol'] = _doc.pop('locus')
                gene_data.append(_doc)
    return gene_data

def restructure_dbsnp_merge(merged_data):
    if merged_data:
        for _doc in merged_data:
            _doc["merged_rsid"] = "rs" + _doc["merged_rsid"]
    return merged_data

def accession_2_chr(accession):
    if accession.startswith('NC_0000'):
        return str(int(accession[7:9]))
    else:
        return 'MT'
def get_hgvs_and_vcf(assembly, placements):
    ASSEMBLY_NAME_MAPPING = {"hg19": "GRCh37.p13",
                             "hg38": "GRCh38.p12"}
    hgvs = None
    vcf = {}
    if placements:
        for _placement in placements:
            assembly_name = _placement.get('placement_annot').get('seq_id_traits_by_assembly')[0].get('assembly_name')
            if assembly_name == ASSEMBLY_NAME_MAPPING[assembly]:
                for _allele in _placement.get('alleles'):
                    if _allele.get('allele').get('spdi').get('deleted_sequence') != _allele.get('allele').get('spdi').get('inserted_sequence'):
                        hgvs = 'chr' + accession_2_chr(_allele.get('hgvs')) + ":" + _allele.get('hgvs').split(':')[-1]
                        vcf = (accession_2_chr(_allele.get('allele').get('spdi').get('seq_id')),
                               _allele.get("allele").get('spdi').get('position') + 1,
                               _allele.get("allele").get('spdi').get('deleted_sequence'),
                               _allele.get("allele").get('spdi').get('inserted_sequence'))
                        return (hgvs, vcf)

