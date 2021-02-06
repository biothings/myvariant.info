import os
import os.path
import sys
import shutil
import subprocess

import biothings
import config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT, logger as logging
from biothings.hub.dataload.dumper import FTPDumper


class ClinvarDumper(FTPDumper):

    SRC_NAME = "clinvar"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    FTP_HOST = 'ftp.ncbi.nlm.nih.gov'
    CWD_DIR = '/pub/clinvar/xml'

    SCHEDULE = "0 9 * * *"

    def get_newest_info(self):
        releases = self.client.nlst()
        # get rid of readme files
        releases = [x for x in releases if x.startswith('ClinVarFullRelease') and x.endswith('gz')]
        # sort items based on date
        releases = sorted(releases)
        # get the last item in the list, which is the latest version
        self.newest_file = releases[-1]
        self.release = releases[-1].split('.')[0].split('_')[1]

    def new_release_available(self):
        current_release = self.src_doc.get("download", {}).get("release")
        if not current_release or self.release > current_release:
            self.logger.info("New release '%s' found" % self.release)
            return True
        else:
            self.logger.debug("No new release found")
            return False

    def create_todump_list(self, force=False):
        self.get_newest_info()
        new_localfile = os.path.join(self.new_data_folder, os.path.basename(self.newest_file))
        try:
            current_localfile = os.path.join(self.current_data_folder, os.path.basename(self.newest_file))
        except TypeError:
            # current data folder doesn't even exist
            current_localfile = new_localfile
        if force or not os.path.exists(current_localfile) or self.remote_is_better(self.newest_file, current_localfile) or self.new_release_available():
            # register new release (will be stored in backend)
            self.to_dump.append({"remote": self.newest_file, "local": new_localfile})
            # schema
            xsd = "clinvar_public.xsd"
            localxsdfile = os.path.join(self.new_data_folder, xsd)
            self.to_dump.append({"remote": "../%s" % xsd, "local": localxsdfile})

    def post_dump(self, *args, **kwargs):
        generate_clinvar_lib(self.new_data_folder)


def generate_clinvar_lib(data_folder):
    sys.path.insert(0, data_folder)
    orig_path = os.getcwd()
    try:
        os.chdir(data_folder)
        logging.info("Generate XM parser")
        # ret = os.system('''generateDS.py -f -o "clinvar_tmp.py" -s "clinvarsubs.py" clinvar_public.xsd''')
        cmd = shutil.which('generateDS.py')
        if not cmd:
            raise OSError('"generateDS.py" is not found in the PATH!')
        # logging.info("CMD: %s; PATH: %s", cmd, os.environ.get("PATH"))
        cmd += " -f -o clinvar_tmp.py -s clinvarsubs.py clinvar_public.xsd"
        # logging.info("CMD: %s", cmd)
        ret = subprocess.call(cmd, shell=True)
        if ret != 0:
            raise Exception("Unable to generate parser, return code: %s" % ret)
        try:
            py = open("clinvar_tmp.py").read()
            # convert py2 to py3 (though they claim it support both versions)
            py = py.replace("from StringIO import StringIO", "from io import StringIO")
            fout = open("genclinvar.py", "w")
            fout.write(py)
            fout.close()
            os.unlink("clinvar_tmp.py")
            # can we import it ?
            import genclinvar
            logging.info("Found generated clinvar module: %s" % genclinvar)
        except Exception as e:
            logging.error("Cannot convert to py3: %s" % e)
            raise
    finally:
        os.chdir(orig_path)


def main():
    dumper = ClinvarDumper()
    dumper.dump()


if __name__ == "__main__":
    main()
