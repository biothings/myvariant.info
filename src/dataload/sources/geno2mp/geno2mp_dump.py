import os, sys, time, datetime

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT
from biothings.dataload.dumper import HTTPDumper
from biothings.utils.common import gunzipall


class Geno2MPDumper(HTTPDumper):

    SRC_NAME = "geno2mp"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    # URL is always the same, but headers change
    SRC_URL = "http://geno2mp.gs.washington.edu/download/Geno2MP.variants.vcf.gz"

    SCHEDULE = "0 9 * * *"

    # TODO: that *might* be moved in HTTPDumper if process is generic
    # (but I guess header name could change (and most importantly, most
    # of the time there's no such header at all...)
    def remote_is_better(self,remotefile,localfile):
        res = os.stat(localfile)
        local_lastmodified = int(res.st_mtime)
        res = self.client.head(remotefile)
        remote_dt =  datetime.datetime.strptime(res.headers["Last-Modified"], '%a, %d %b %Y %H:%M:%S GMT')
        remote_lastmodified = time.mktime(remote_dt.timetuple())
        if remote_lastmodified > local_lastmodified:
            self.logger.debug("Remote file '%s' is newer (remote: %s, local: %s)" %
                    (remotefile,remote_lastmodified,local_lastmodified))
            # also set release attr
            self.release = remote_dt.strftime("%Y-%m-%d")
            return True
        else:
            return False

    def create_todump_list(self, force=False):
        filename = os.path.basename(self.__class__.SRC_URL)
        try:
            current_localfile = os.path.join(self.current_data_folder,filename)
        except TypeError:
            # current data folder doesn't even exist
            current_localfile = None
        if current_localfile is None or self.remote_is_better(self.__class__.SRC_URL,current_localfile):
            new_localfile = os.path.join(self.new_data_folder,filename)
            self.to_dump.append({"remote":self.__class__.SRC_URL, "local":new_localfile})

    def post_dump(self):
        self.logger.info("Uncompressing files in '%s'" % self.new_data_folder) 
        gunzipall(self.new_data_folder)

