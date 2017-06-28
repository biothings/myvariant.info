import unicodedata

from csv import DictReader
from pprint import pprint
from biothings.utils.dataload import dict_sweep, open_anyfile


def load_data(input_file):

    with open_anyfile(input_file) as in_f:
        reader = DictReader(in_f, delimiter='\t')

        for row in reader:

            variant = {}

            # Skip
            if 'gDNA' not in row or row['gDNA'] == "":
                continue

            # Skip variants that are not mutations
            if 'Alteration type' not in row or row['Alteration type'] != 'MUT':
                continue

            # Use gDNA as variant identifier
            variant['_id'] = row['gDNA']

            for k in [
                'region', 'cDNA', 'Evidence level', 'transcript', 'Gene', ('individual_mutation', 'protein_change'), 'Primary Tumor type',
                ('Drug full name', 'drug'), 'Source', 'Association']:

                if isinstance(k, tuple):
                    new_k = k[1]
                    old_k = k[0]
                else:
                    new_k = k.lower().replace(' ', '_')
                    old_k = k

                variant[new_k] = unicodedata.normalize("NFKD", row.get(old_k, None))

            yield dict_sweep(variant, vals=['', 'null', 'N/A', None, [], {}])


if __name__ == "__main__":

    for v in load_data('cgi_biomarkers_per_variant.tsv'):
        pprint({k: {"type": "string", "analyzer": "string_lowercase"} for k in v.keys()})
        break
        #pprint(v)
        #input("Press Enter to continue...")
