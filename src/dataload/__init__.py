
__sources_dict__ = {
        'clinvar' : [
            'clinvar.clinvar_hg19',
            'clinvar.clinvar_hg38',
        ],
        'dbsnp' : [
            {
                "name": 'dbsnp',
                'uploader' : 'biothings.dataload.uploader.NoBatchIgnoreDuplicatedSourceUploader'
            },
        ],
    }


import sys, time

