import os
import os.path
import sys
import time
from ftplib import FTP
from utils.common import ask, timesofar, LogPrint, safewfile
from utils.mongo import get_src_dump
from config import DATA_ARCHIVE_ROOT


timestamp = time.strftime('%Y%m%d')
DATA_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, 'clinvar', timestamp)
FTP_SERVER = 'ftp.ncbi.nlm.nih.gov'
DATAFILE_PATH = 'pub/clinvar/xml'


def download_ftp_file(no_confirm=False):
    orig_path = os.getcwd()
    newest_file = get_newest_release()[0]
    try:
        os.chdir(DATA_FOLDER)
        print('Downloading "%s"...' % newest_file)
        url = 'ftp://{}/{}/{}'.format(FTP_SERVER, DATAFILE_PATH, newest_file)
        cmdline = 'wget %s -O %s' % (url, newest_file)
        # cmdline = 'axel -a -n 5 %s' % url   #faster than wget using 5 connections
        return_code = os.system(cmdline)
        if return_code == 0:
            print("Success.")
        else:
            print("Failed with return code (%s)." % return_code)
        print("="*50)
    finally:
        os.chdir(orig_path)


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
    if new_release_available(doc['release']):
        data_file = os.path.join(doc['data_folder'], file_name)
        if os.path.exists(data_file):
            print("No newer file found. Abort now.")
            return

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
