import os
import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT
from biothings.hub.dataload.dumper import ManualDumper


class WellderlyDumper(ManualDumper):

    SRC_NAME = "wellderly"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)

    def __init__(self, *args, **kwargs):
        super(WellderlyDumper, self).__init__(*args, **kwargs)
        self.logger.info("Assuming Wellderly.chr*.g.vcf.gz.tsv files were manual downloaded")
