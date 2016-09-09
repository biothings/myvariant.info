import os
import os.path
import sys
import time
from ftplib import FTP
from biothings.utils.common import ask, timesofar, LogPrint, safewfile
from biothings.utils.mongo import get_src_dump
from config import DATA_ARCHIVE_ROOT, logger as logging


timestamp = time.strftime('%Y%m%d')
DATA_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, 'clinvar', timestamp)
FTP_SERVER = 'ftp.ncbi.nlm.nih.gov'
DATAFILE_PATH = 'pub/clinvar/xml'


def wget_file(url,destdir,filename=None):
    orig_path = os.getcwd()
    try:
        os.chdir(destdir)
        filename = filename or url.split("/")[-1]
        logging.info('Downloading "%s"...' % filename)
        cmdline = 'wget %s -O %s' % (url, filename)
        return_code = os.system(cmdline)
        if return_code == 0:
            logging.info("Success.")
        else:
            logging.error("Failed with return code (%s)." % return_code)
    finally:
        os.chdir(orig_path)

def download_ftp_file(no_confirm=False):
    newest_file = get_newest_release()[0]
    url = 'ftp://{}/{}/{}'.format(FTP_SERVER, DATAFILE_PATH, newest_file)
    wget_file(url,DATA_FOLDER)
    url = 'ftp://{}/{}/../{}'.format(FTP_SERVER, DATAFILE_PATH, 'clinvar_public.xsd')
    wget_file(url,DATA_FOLDER)
    logging.info("="*50)

# get the newest version name for ClinVar database
def get_newest_release():
    ftp = FTP('ftp.ncbi.nlm.nih.gov')
    ftp.login()
    ftp.cwd('pub/clinvar/xml')
    releases = ftp.nlst()
    # get rid of readme files
    releases = [x for x in releases if x.startswith('ClinVarFullRelease') and x.endswith('gz')]
    # sort items based on date
    releases = sorted(releases)
    # get the last item in the list, which is the latest version
    newest_file = releases[-1]
    newest_release = releases[-1].split('.')[0].split('_')[1]
    return (newest_file, newest_release)


# check whether there are newer versions
def new_release_available(current_release):
    newest_release = get_newest_release()[1]
    if newest_release == current_release:
        return False
    else:
        return True

def main():
    no_confirm = True   # set it to True for running this script automatically without intervention.
    src_dump = get_src_dump()
    (file_name, release) = get_newest_release()

    doc = src_dump.find_one({'_id': 'clinvar'})
    data_file = doc and os.path.join(doc.get('data_folder',""), file_name)
    if data_file:
        logging.debug("Found data_file '%s'" % data_file)

    need_dump = False
    if not doc:
        logging.info("No previous dump found, initiate")
        need_dump = True
    elif not os.path.exists(data_file):
        logging.info("No files found in '%s'" % doc.get('data_folder',""))
        need_dump = True
    elif new_release_available(doc['release']):
        logging.info("New release available")
        need_dump = True

    if need_dump:
        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)
        else:
            if not (no_confirm or len(os.listdir(DATA_FOLDER)) == 0
                    or ask('DATA_FOLDER (%s) is not empty. Continue?' % DATA_FOLDER) == 'Y'):
                return

        log_f, logfile = safewfile(os.path.join(DATA_FOLDER, 'clinvar_dump.log'), prompt=(not no_confirm), default='O')
        sys.stdout = LogPrint(log_f, timestamp=True)

        # mark the download starts
        doc = {'_id': 'clinvar',
               'timestamp': timestamp,
               'data_folder': DATA_FOLDER,
               'release': release,
               'logfile': logfile,
               'status': 'downloading'}
        src_dump.save(doc)
        t0 = time.time()
        try:
            download_ftp_file(no_confirm)
        finally:
            sys.stdout.close()
        # mark the download finished successfully
        _updates = {
            'status': 'success',
            'time': timesofar(t0),
            'pending_to_upload': True    # a flag to trigger data uploading
        }
        src_dump.update({'_id': 'clinvar'}, {'$set': _updates})

    else:
        logging.info("No dump needed")

if __name__ == "__main__":
    main()
