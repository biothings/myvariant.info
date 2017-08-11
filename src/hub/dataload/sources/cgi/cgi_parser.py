import unicodedata
from collections import defaultdict

from csv import DictReader
from biothings.utils.dataload import dict_sweep, open_anyfile


def load_data(input_file):

    with open_anyfile(input_file) as in_f:

        # Remove duplicated lines if any
        header = next(in_f).strip().split('\t')
        lines = set(list(in_f))
        reader = DictReader(lines, fieldnames=header, delimiter='\t')

        results = defaultdict(list)
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
            variant['cgi'] = {}

            for k in [
                'region', 'cDNA', 'Evidence level', 'transcript', 'Gene', ('individual_mutation', 'protein_change'), 'Primary Tumor type',
                ('Drug full name', 'drug'), 'Source', 'Association']:

                if isinstance(k, tuple):
                    new_k = k[1]
                    old_k = k[0]
                else:
                    new_k = k.lower().replace(' ', '_')
                    old_k = k

                variant['cgi'][new_k] = unicodedata.normalize("NFKD", row.get(old_k, None))

            variant = dict_sweep(variant, vals=['', 'null', 'N/A', None, [], {}])
            results[variant['_id']].append(variant)

        # Merge duplications
        for v in results.values():
            if len(v) == 1:
                yield v[0]
            else:
                yield {
                    '_id': v[0]['_id'],
                    'cgi': [i['cgi'] for i in v]
                }
