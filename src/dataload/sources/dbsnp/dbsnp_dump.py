import os
import os.path
import sys, re
import time
from ftplib import FTP
from datetime import datetime

import biothings, config
biothings.config_for_app(config)

from biothings.utils.common import ask, timesofar, LogPrint, safewfile
from biothings.utils.mongo import get_src_dump
from config import DATA_ARCHIVE_ROOT, logger as logging


class DBSNPDumper(object):

    SRC_NAME = "dbsnp"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    FTP_HOST = 'ftp.ncbi.nlm.nih.gov'
    CWD_DIR = '/snp/organisms'
    DATAFILE_RE_PATTERN = '''human_9606_(.\d+)_GRCh\d\dp\d+'''
    FILE_PATH = 'VCF/00-All.vcf.gz'

    def __init__(self, no_confirm=True, archive=True):
        self.client = None
        self.src_dump = None
        self.src_doc = None
        self.no_confirm = no_confirm
        self.archive = archive
        self.to_dump = []
        self.release = None
        self.t0 = time.time()
        self.logfile = None
        self.prev_data_folder = None
        self.timestamp = time.strftime('%Y%m%d')
        # init
        self.setup_log()
        self.prepare()

    def get_new_data_folder(self):
        if self.archive:
            return os.path.join(DATA_ARCHIVE_ROOT, self.SRC_NAME, self.timestamp) 
        else:
            return os.path.join(DATA_ARCHIVE_ROOT, self.SRC_NAME, 'latest') 

    def setup_log(self):
        import logging as logging_mod
        if not os.path.exists(self.SRC_ROOT_FOLDER):
            os.makedirs(self.SRC_ROOT_FOLDER)
        self.logfile = os.path.join(self.SRC_ROOT_FOLDER, '%s_%s_dump.log' % (self.SRC_NAME,self.timestamp))
        fh = logging_mod.FileHandler(self.logfile)
        fh.setFormatter(logging_mod.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        fh.name = "logfile"
        sh = logging_mod.StreamHandler()
        sh.name = "logstream"
        logger = logging_mod.getLogger("%s_dump" % self.SRC_NAME)
        logger.setLevel(logging_mod.DEBUG)
        if not fh.name in [h.name for h in logger.handlers]:
            logger.addHandler(fh)
        if not sh.name in [h.name for h in logger.handlers]:
            logger.addHandler(sh)
        # propagate to global "logging" var for convenience
        global logging
        logging = logger

    def prepare_client(self):
        # FTP side
        self.client = FTP(self.FTP_HOST)
        self.client.login()
        if self.CWD_DIR:
            self.client.cwd(self.CWD_DIR)

    def prepare_src_dump(self):
        # Mongo side
        self.src_dump = get_src_dump()
        self.src_doc = self.src_dump.find_one({'_id': self.SRC_NAME}) or {}

    def prepare(self):
        self.prepare_client()
        self.prepare_src_dump()
        self.new_data_folder = self.get_new_data_folder()
        self.current_data_folder = self.src_doc.get("data_folder")
        self.to_dump = []

    def dump(self):
        '''dump (ie. download) resource as needed'''
        try:
            if self.client and not self.client.file:
                self.prepare()
            self.create_todump_list()
            if self.to_dump:
                # mark the download starts
                self.register_status("downloading",transient=True)
                self.do_dump()
                self.register_status("success",pending_to_upload=True)
        except (KeyboardInterrupt,Exception) as e:
            logging.error("Error while dumping source: %s" % e)
            self.register_status("failed")
        finally:
            if self.client:
                self.client.close()
            #sys.stdout.close()

    def find_latest_human_dirs(self):
        # list all orgs
        orgs = self.client.nlst()
        humans = {}
        for org in orgs:
            m = re.match(self.DATAFILE_RE_PATTERN,org)
            if m:
                humans.setdefault(m.groups()[0],[]).append(org)
        # get latest
        self.release = sorted(humans)[-1]
        latest_human_dirs = humans[self.release]
        return latest_human_dirs

    def create_todump_list(self):
        latest_remote_dirs = self.find_latest_human_dirs()
        for one_dir in latest_remote_dirs:
            rel_path = os.path.join(one_dir,self.FILE_PATH)
            new_localfile = os.path.join(self.new_data_folder,rel_path)
            try:
                current_localfile = os.path.join(self.current_data_folder,rel_path)
            except TypeError:
                # current data folder doesn't even exist
                current_localfile = new_localfile
            if not os.path.exists(current_localfile) or self.remote_is_better(rel_path, current_localfile):
                self.to_dump.append({"remote":rel_path, "local":new_localfile})

    def remote_is_better(self,remotefile,localfile):
        '''Compared to local file, remote file is worth downloading.
        It's either bigger or newer'''
        res = os.stat(localfile)
        local_lastmodified = int(res.st_mtime)
        response = self.client.sendcmd('MDTM ' + remotefile)
        code, remote_lastmodified = response.split()
        remote_lastmodified = int(time.mktime(datetime.strptime(remote_lastmodified, '%Y%m%d%H%M%S').timetuple()))

        if remote_lastmodified > local_lastmodified:
            logging.debug("Remote file '%s' is newer (remote: %s, local: %s)" %
                    (remotefile,remote_lastmodified,local_lastmodified))
            return True
        local_size = res.st_size
        self.client.sendcmd("TYPE I")
        response = self.client.sendcmd('SIZE ' + remotefile)
        code, remote_size= map(int,response.split())
        if remote_size > local_size:
            logging.debug("Remote file '%s' is bigger (remote: %s, local: %s)" % (remotefile,remote_size,local_size))
            return True
        logging.debug("No need to download '%s'" % remotefile)
        return False

    def register_status(self,status,transient=False,**extra):
        self.src_doc = {'_id': self.SRC_NAME,
               'timestamp': self.timestamp,
               'data_folder': self.new_data_folder,
               'release': self.release,
               'logfile': self.logfile,
               'status': status}
        # only register time when it's a final state
        if not transient:
            self.src_doc["time"] = timesofar(self.t0)
        self.src_doc.update(extra)
        self.src_dump.save(self.src_doc)

    def do_dump(self):
        for todo in self.to_dump:
            remote = todo["remote"]
            local = todo["local"]
            self.download(remote,local)

    def download(self,remotefile,localfile):
        logging.debug("Downloading '%s'" % remotefile)
        localdir = os.path.dirname(localfile)
        if not os.path.exists(localdir):
            os.makedirs(localdir)
        with open(localfile,"wb") as out_f:
            self.client.retrbinary('RETR %s' % remotefile, out_f.write)
        # set the mtime to match remote ftp server
        response = self.client.sendcmd('MDTM ' + remotefile)
        code, lastmodified = response.split()
        # an example: 'last-modified': '20121128150000'
        lastmodified = time.mktime(datetime.strptime(lastmodified, '%Y%m%d%H%M%S').timetuple())
        os.utime(localfile, (lastmodified, lastmodified))

def main():
    dumper = DBSNPDumper()
    dumper.dump()

if __name__ == "__main__":
    main()
