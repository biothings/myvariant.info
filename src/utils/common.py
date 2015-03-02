from __future__ import print_function
import sys
import time
from itertools import islice
import os.path
from shlex import shlex
import gzip
import pickle

if sys.version_info.major == 3:
    str_types = str
    import pickle       # noqa
else:
    str_types = (str, unicode)    # noqa
    import cPickle as pickle


# ===============================================================================
# Misc. Utility functions
# ===============================================================================
def ask(prompt, options='YN'):
    '''Prompt Yes or No,return the upper case 'Y' or 'N'.'''
    options = options.upper()
    while 1:
        s = input(prompt+'[%s]' % '|'.join(list(options))).strip().upper()
        if s in options:
            break
    return s


def timesofar(t0, clock=0, t1=None):
    '''return the string(eg.'3m3.42s') for the passed real time/CPU time so far
       from given t0 (return from t0=time.time() for real time/
       t0=time.clock() for CPU time).'''
    t1 = t1 or time.clock() if clock else time.time()
    t = t1 - t0
    h = int(t / 3600)
    m = int((t % 3600) / 60)
    s = round((t % 3600) % 60, 2)
    t_str = ''
    if h != 0:
        t_str += '%sh' % h
    if m != 0:
        t_str += '%sm' % m
    t_str += '%ss' % s
    return t_str


def is_str(s):
    """return True or False if input is a string or not.
        python3 compatible.
    """
    return isinstance(s, str_types)


def is_seq(li):
    """return True if input is either a list or a tuple.
    """
    return isinstance(li, (list, tuple))


def iter_n(iterable, n):
    '''
    ref http://stackoverflow.com/questions/8991506/iterate-an-iterator-by-chunks-of-n-in-python
    '''
    it = iter(iterable)
    while True:
        chunk = tuple(islice(it, n))
        if not chunk:
            return
        yield chunk


def anyfile(infile, mode='r'):
    '''
    return a file handler with the support for gzip/zip comppressed files
    if infile is a two value tuple, then first one is the compressed file;
      the second one is the actual filename in the compressed file.
      e.g., ('a.zip', 'aa.txt')

    '''
    if isinstance(infile, tuple):
        infile, rawfile = infile[:2]
    else:
        rawfile = os.path.splitext(infile)[0]
    filetype = os.path.splitext(infile)[1].lower()
    if filetype == '.gz':
        import gzip
        #in_f = gzip.GzipFile(infile, 'r')
        in_f = gzip.open(infile, 'rt')
    elif filetype == '.zip':
        import zipfile
        in_f = zipfile.ZipFile(infile, 'r').open(rawfile, 'r')
    else:
        in_f = open(infile, mode)
    return in_f


def is_filehandle(fh):
    '''return True/False if fh is a file-like object'''
    return hasattr(fh, 'read') and hasattr(fh, 'close')


class open_anyfile():
    '''a context manager can be used in "with" stmt.
       accepts a filehandle or anything accepted by anyfile function.

        with open_anyfile('test.txt') as in_f:
            do_something()
    '''
    def __init__(self, infile, mode='r'):
        self.infile = infile
        self.mode = mode

    def __enter__(self):
        if is_filehandle(self.infile):
            self.in_f = self.infile
        else:
            self.in_f = anyfile(self.infile, mode=self.mode)
        return self.in_f

    def __exit__(self, type, value, traceback):
        self.in_f.close()


class dotdict(dict):
    def __getattr__(self, attr):
        value = self.get(attr, None)
        if isinstance(value, dict):
            return dotdict(value)
        else:
            return value
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def split_ids(q):
    '''split input query string into list of ids.
       any of " \t\n\x0b\x0c\r|,+" as the separator,
        but perserving a phrase if quoted
        (either single or double quoted)
        more detailed rules see:
        http://docs.python.org/2/library/shlex.html#parsing-rules

        e.g. split_ids('CDK2 CDK3') --> ['CDK2', 'CDK3']
             split_ids('"CDK2 CDK3"\n CDk4')  --> ['CDK2 CDK3', 'CDK4']

    '''
    lex = shlex(q.encode('utf8'), posix=True)
    lex.whitespace = ' \t\n\x0b\x0c\r|,+'
    lex.whitespace_split = True
    lex.commenters = ''
    ids = [x.decode('utf8').strip() for x in list(lex)]
    ids = [x for x in ids if x]
    return ids


def dump(obj, filename, bin=2):
    '''Saves a compressed object to disk
       binary protocol 2 is compatible with py2, 3 and 4 are for py3
    '''
    print('Dumping into "%s"...' % filename, end='')
    out_f = gzip.GzipFile(filename, 'wb')
    # out_f = bz2.BZ2File(filename, 'w')
    # out_f = lzma.LZMAFile(filename, 'w')
    pickle.dump(obj, out_f, protocol=bin)
    out_f.close()
    print('Done. [%s]' % os.stat(filename).st_size)


def dump2gridfs(object, filename, db, bin=2):
    '''Save a compressed object to MongoDB gridfs.'''
    import gridfs
    print('Dumping into "MongoDB:%s/%s"...' % (db.name, filename), end='')
    fs = gridfs.GridFS(db)
    if fs.exists(_id=filename):
        fs.delete(filename)
    fobj = fs.new_file(filename=filename, _id=filename)
    try:
        gzfobj = gzip.GzipFile(filename=filename, mode='wb', fileobj=fobj)
        pickle.dump(object, gzfobj, protocol=bin)
    finally:
        gzfobj.close()
        fobj.close()
    print('Done. [%s]' % fs.get(filename).length)


def loadobj(filename, mode='file'):
    '''Loads a compressed object from disk file (or file-like handler) or
        MongoDB gridfs file (mode='gridfs')
           obj = loadobj('data.pyobj')

           obj = loadobj(('data.pyobj', mongo_db), mode='gridfs')
    '''
    if mode == 'gridfs':
        import gridfs
        filename, db = filename   # input is a tuple of (filename, mongo_db)
        fs = gridfs.GridFS(db)
        fobj = fs.get(filename)
    else:
        if is_str(filename):
            fobj = gzip.GzipFile(filename, 'rb')
            # fobj = bz2.BZ2File(filename, 'r')
            # fobj = lzma.LZMAFile(filename, 'r')
        else:
            fobj = filename   # input is a file-like handler
    try:
        object = pickle.load(fobj)
    finally:
        fobj.close()
    return object
