import json
import glob

from utils.hgvs import get_pos_start_end, prune_redundant_seq
from biothings.utils.dataload import dict_sweep, unlist, value_convert_to_number
from biothings.utils.common import open_compressed_file

# QUESTION:
# rs5823327 => no ref, alt; do we still want to keep it
# rs10577038 => two different hgvs representations
#               NC_000018.9:g.476589_476590delGC
#               NC_000018.9:g.476588_476590delCGCinsA
# rs16442   => novel patch
#               NC_000021.8:g.34821649_34821650delAA
#               NW_003315970.1:g.43915_43916delAA
# geneid is going to be integer (previously string)
# fields gone: allele_origin, gmaf, alleles/allele/freq, class, flags, validated, var_subtype
# current code unable to get assembly start/end position based on vcf for indel/del/is
# TODO
# Index geneid field as string

# Note on dbsnp hg38 data:
#   release 154 are based on "GRCh38.p12",
#   release 155 on "GRCh38.p13"
#   release 156 on "GRCh38.p14"
ASSEMBLY_NAME_MAPPING = {"hg19": "GRCh37.p13", "hg38": "GRCh38.p14"}


def parse_one_rec(assembly, record):
    """
    Parse a record from a 'refsnp-chr*.json.bz2' file into one or multiple documents.

    From https://ftp.ncbi.nlm.nih.gov/snp/latest_release/JSON/JSON_README.txt we know that each
    'refsnp-chr*.json.bz2' file conform to the "refsnp_snapshot_success" OpenAPI schema, as defined in
    https://api.ncbi.nlm.nih.gov/variation/v0/var_service.yaml

    From the above schema, we can find that each record (i.e. each line of one of 'refsnp-chr*.json.bz2' files) conform
    to the "refsnp_snapshot" OpenAPI schema, which **requires** the following components:

    - "refsnp_id" (type: string, format: uint64),
    - "create_date" (type: string, format: ISO 8601),
    - "last_update_date" (type: string, format: ISO 8601),
    - "last_update_build_id" (type: string, format: ascii),
    - "dbsnp1_merges" (type: array),
    - "lost_obs_movements" (type: array),
    - "present_obs_movements" (type: array),
    - "citations" (type: array)

    A another component of our interest is "primary_snapshot_data" (type: object), which is optional to
    "refsnp_snapshot". If exists, itself **requires** the following sub-components:

    - "placements_with_allele" (type: array),
    - "allele_annotations" (type: array),
    - "support" (type: array),
    - "anchor" (type: string, format: ascii),
    - "variant_type" (type: string, format: ascii)

    Plus, it's known that **none** of the fields defined in the above schema is "nullable".
    (See https://stackoverflow.com/questions/45575493/what-does-required-in-openapi-really-mean for more.)

    The requiredness, data types, and nullability of each components are a guideline to apply existence check and type
    conversion to those fields in the output json objects.
    """

    """
    We can extract common fields from the input record, and for each "allele" in each "placement" from the record's 
    "primary_snapshot_data" component, we can extract some allele-specific fields. The generation of the output 
    documents can be described with the pseudocode below:
    
        common_fields = {...}
        
        for placement in placements:
            for allele in placement["alleles"]
                allele_specific_fields = {...}
                doc = {
                    **common_fields,
                    **allele_specific_fields,
                }
            
                yield doc
    """
    snapshot = record.get("primary_snapshot_data")
    annotations = snapshot.get("allele_annotations")
    placements = snapshot.get("placements_with_allele")

    common_fields = {
        # fields parsed directly from `record`
        "rsid": "rs" + str(record.get("refsnp_id")),
        "dbsnp_build": int(record.get("last_update_build_id")),
        "dbsnp_merges": restructure_dbsnp_merge(record.get("dbsnp1_merges")),
        "citations": record.get("citations"),

        # fields parsed from `record["primary_snapshot_data"]`
        "vartype": snapshot.get("variant_type"),

        # fields parsed from `record["primary_snapshot_data"]["allele_annotations"]`
        "alleles": restructure_allele_freq_info(annotations),
        "gene": restructure_gene_info(annotations)
    }

    variant_type = common_fields["vartype"]

    # fields parsed from `record["primary_snapshot_data"]["placements_with_allele"]
    for hgvs, vcf in get_hgvs_and_vcf(assembly, placements):
        chrom, pos, ref, alt = vcf

        start, end = get_start_end(variant_type, chrom, pos, ref, alt)
        if start is None and end is None:
            coordinates = {}
        else:  # we can infer from `get_pos_start_end` that in this case, neither of `start` or `end` could be None
            coordinates = {
                "start": start,
                "end": end
            }

        allele_specific_fields = {
            "_id": hgvs,
            "chrom": chrom,
            "ref": ref,
            "alt": alt,
            assembly: coordinates
        }

        doc = {
            **common_fields,
            **allele_specific_fields
        }
        yield dict_sweep(unlist(value_convert_to_number(doc, skipped_keys=['chrom', 'ref', 'alt', 'allele', 'deleted_sequence', 'inserted_sequence'])), vals=[[], {}, None])


def get_start_end(variant_type, chrom, pos, ref, alt):
    # TODO this is actually a hack.
    #   When the variant is not a 'snv', ref or alt might be empty.
    #   However `get_pos_start_end` cannot work with empty ref or alt.
    #   Therefore we add a preceding "T" (or any single character) to bypass this limitation.
    #   The detail of this hack should be handled by `get_pos_start_end` itself, not here.
    if variant_type != "snv":
        ref = "T" + ref
        alt = "T" + alt

    try:
        if variant_type in ["ins", "del", "delins"]:
            start, end = get_pos_start_end(chrom, pos - 1, ref, alt)
        else:
            start, end = get_pos_start_end(chrom, pos, ref, alt)

        return start, end
    except (ValueError, AssertionError):
        return None, None


def restructure_allele_freq_info(allele_annotations):
    """Restructure information related to allele frequency
    """
    alleles_data = []
    for _annotation in allele_annotations:
        freq_data = _annotation.get('frequency')
        if freq_data:
            freq = {'freq': {}}
            for _doc in filter(None, freq_data):
                freq['allele'] = _doc.get('observation').get('inserted_sequence')
                freq_source = _doc.get('study_name').lower()
                if freq_source == '1000genomes':
                    freq_source = '1000g'
                freq['freq'][freq_source] = round(_doc.get('allele_count')/_doc.get('total_count'), 3)
            alleles_data.append(freq)
    return alleles_data


def restructure_gene_info(allele_annotations):
    """Restructure information related to gene
    """
    gene_data = []
    assembly_annotation = allele_annotations[0].get('assembly_annotation')
    if assembly_annotation and assembly_annotation[0]:
        for _doc in filter(None, assembly_annotation[0].get('genes')):
            if "orientation" in _doc:
                _doc['strand'] = _doc.pop("orientation")
            if _doc["strand"] == "plus":
                _doc["strand"] = "+"
            elif _doc["strand"] == "minus":
                _doc["strand"] = "-"
            _doc['geneid'] = _doc.pop('id')
            _doc['symbol'] = _doc.pop('locus')
            _doc['so'] = _doc.pop('sequence_ontology')
            for _item in filter(None, _doc['rnas']):
                _item['refseq'] = _item.pop('id')
                _item['so'] = _item.pop('sequence_ontology')
                if 'product_id' in _item:
                    _item['protein_product'] = {'refseq': _item.pop('product_id')}
            gene_data.append(_doc)
    return gene_data


def restructure_dbsnp_merge(merged_data):
    if merged_data:
        for _doc in merged_data:
            _doc["rsid"] = "rs" + _doc.pop("merged_rsid")
            _doc["date"] = _doc.pop('merge_date')
            _doc["rv"] = _doc.pop("revision")
    return merged_data


def accession_to_chr(accession):
    if accession.startswith('NC_0000'):
        # If accession[7:9] is not a valid chrom representation, `int()` conversion would fail and raise an error
        # `int()` could also eliminate the leading 0
        chrom = int(accession[7:9])
        if chrom == 23:
            return "X"
        elif chrom == 24:
            return "Y"
        else:
            return str(chrom)
    else:
        return 'MT'


def get_hgvs_and_vcf(assembly, placements):
    if not placements:
        return

    expected_assembly_name = ASSEMBLY_NAME_MAPPING[assembly]
    for _placement in placements:
        seq = _placement.get('placement_annot').get('seq_id_traits_by_assembly')
        if not seq:
            continue

        """
        An assembly name has two parts, a build number and a release number.
        Take "GRCh38.p13" as an example. "GRCh38" is the build number; "p13" is the release number.
        
        A "placements" array may contain two placements on different assemblies.
        E.g. one on "GRCh38.p13" and the other on "GRCh37.p13"
        Say `assembly` is "hg19", the expected build is "GRCh37"; placements not on the expected build should be 
        discarded for parsing.
        
        However, if the placement's build is expected but its release does not match, an error should be raised.
        """
        placement_assembly_name = seq[0].get('assembly_name')
        if placement_assembly_name != expected_assembly_name:
            placement_build = placement_assembly_name.split(r".", 1)[0]
            expected_build = expected_assembly_name.split(r".", 1)[0]
            if placement_build == expected_build:
                raise ValueError("GRCh release numbers do not match. Expect {}. Got {}.".format(
                    expected_assembly_name, placement_assembly_name))
            else:
                continue

        """
        The naming in the OpenAPI schema (https://api.ncbi.nlm.nih.gov/variation/v0/var_service.yaml) is kind of 
        confusing.
        
        Each placement has an array of "placement_annotated_allele" objects, accessible via `_placement["alleles"]`.
        Each "placement_annotated_allele" object **requires** two fields, "allele" and "hgvs".
        """
        for _allele in _placement.get('alleles'):
            # (type: object, required: [seq_id, position, deleted_sequence, inserted_sequence])
            spdi = _allele.get('allele').get('spdi')
            if not spdi:  # note that "spdi" is not a **required** component to "allele"
                continue

            hgvs = _allele.get('hgvs')  # (type: string, format: ascii)
            if not hgvs:  # hgvs is not nullable but it could be an empty string
                continue

            ref = spdi.get('deleted_sequence')
            alt = spdi.get('inserted_sequence')
            if ref != alt and hgvs.startswith('NC'):
                new_hgvs = 'chr' + accession_to_chr(hgvs) + ":" + hgvs.split(':')[-1]

                chrom = accession_to_chr(spdi.get('seq_id'))
                pos = spdi.get('position') + 1
                vcf = (chrom, pos, ref, alt)

                yield new_hgvs, vcf


def load_data_file(input_file, version):
    f = open_compressed_file(input_file)
    for line in f:
        record = parse_one_rec(version, json.loads(line.decode()))
        for _doc in record:
            new_doc = dict()
            new_doc['_id'] = prune_redundant_seq(_doc.pop('_id'))
            new_doc['dbsnp'] = _doc
            yield new_doc


# load path and find files, pass to data_generator
def load_data(path_glob, version='hg19'):
    for input_file in sorted(glob.glob(path_glob)):
        for d in load_data_file(input_file, version):
            yield d
