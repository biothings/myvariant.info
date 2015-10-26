from __future__ import print_function
import base64
import os
import random
import string
import sys
import time
from itertools import islice
from contextlib import contextmanager
import os.path
from shlex import shlex
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


def is_float(f):
    """return True if input is a float.
    """
    return isinstance(f, float)


def iter_n(iterable, n, with_cnt=False):
    '''
    Iterate an iterator by chunks (of n)
    if with_cnt is True, return (chunk, cnt) each time
    ref http://stackoverflow.com/questions/8991506/iterate-an-iterator-by-chunks-of-n-in-python
    '''
    it = iter(iterable)
    if with_cnt:
        cnt = 0
    while True:
        chunk = tuple(islice(it, n))
        if not chunk:
            return
        if with_cnt:
            cnt += len(chunk)
            yield (chunk, cnt)
        else:
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


@contextmanager
def open_anyfile2(infile, mode='r'):
    '''a context manager can be used in "with" stmt.
       accepts a filehandle or anything accepted by anyfile function.

        with open_anyfile('test.txt') as in_f:
            do_something()

       This is equivelant of above open_anyfile, but simplier code flow.
    '''
    if is_filehandle(infile):
        in_f = infile
    else:
        in_f = anyfile(infile, mode=mode)
    try:
        yield in_f
    finally:
        in_f.close()


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
    # Python3 strings are already unicode, .encode
    # now returns a bytearray, which cannot be searched with
    # shlex.  For now, do this terrible thing until we discuss
    if sys.version_info.major == 3:
        lex = shlex(q, posix=True)
    else:
        lex = shlex(q.encode('utf8'), posix=True)
    lex.whitespace = ' \t\n\x0b\x0c\r|,+'
    lex.whitespace_split = True
    lex.commenters = ''
    if sys.version_info.major == 3:
        ids = [x.strip() for x in list(lex)]
    else:
        ids = [x.decode('utf8').strip() for x in list(lex)]
    ids = [x for x in ids if x]
    return ids


def get_compressed_outfile(filename, compress='gzip'):
    '''Get a output file handler with given compress method.
       currently support gzip/bz2/lzma, lzma only available in py3
    '''
    if compress == "gzip":
        import gzip
        out_f = gzip.GzipFile(filename, 'wb')
    elif compress == 'bz2':
        import bz2
        out_f = bz2.BZ2File(filename, 'w')
    elif compress == 'lzma':
        import lzma
        out_f = lzma.LZMAFile(filename, 'w')
    else:
        raise ValueError("Invalid compress parameter.")
    return out_f


def open_compressed_file(filename):
    '''Get a read-only file-handler for compressed file,
       currently support gzip/bz2/lzma, lzma only available in py3
    '''
    in_f = open(filename, 'rb')
    sig = in_f.read(5)
    in_f.close()
    if sig[:3] == b'\x1f\x8b\x08':
        # this is a gzip file
        import gzip
        fobj = gzip.GzipFile(filename, 'rb')
    elif sig[:3] == b'BZh':
        # this is a bz2 file
        import bz2
        fobj = bz2.BZ2File(filename, 'r')
    elif sig[:5] == b'\xfd7zXZ':
        # this is a lzma file
        import lzma
        fobj = lzma.LZMAFile(filename, 'r')
    else:
        raise IOError('Unrecognized file type: "{}"'.format(sig))
    return fobj


def dump(obj, filename, bin=2, compress='gzip'):
    '''Saves a compressed object to disk
       binary protocol 2 is compatible with py2, 3 and 4 are for py3
    '''
    print('Dumping into "%s"...' % filename, end='')
    out_f = get_compressed_outfile(filename, compress=compress)
    pickle.dump(obj, out_f, protocol=bin)
    out_f.close()
    print('Done. [%s]' % os.stat(filename).st_size)


def dump2gridfs(object, filename, db, bin=2):
    '''Save a compressed (support gzip only) object to MongoDB gridfs.'''
    import gridfs
    import gzip
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
            fobj = open_compressed_file(filename)
            # fobj = gzip.GzipFile(filename, 'rb')
            # fobj = bz2.BZ2File(filename, 'r')
            # fobj = lzma.LZMAFile(filename, 'r')
        else:
            fobj = filename   # input is a file-like handler
    try:
        object = pickle.load(fobj)
    finally:
        fobj.close()
    return object


def list2dict(a_list, keyitem, alwayslist=False):
    '''Return a dictionary with specified keyitem as key, others as values.
       keyitem can be an index or a sequence of indexes.
       For example: li=[['A','a',1],
                        ['B','a',2],
                        ['A','b',3]]
                    list2dict(li,0)---> {'A':[('a',1),('b',3)],
                                         'B':('a',2)}
       if alwayslist is True, values are always a list even there is only one item in it.
                    list2dict(li,0,True)---> {'A':[('a',1),('b',3)],
                                              'B':[('a',2),]}
    '''
    _dict = {}
    for x in a_list:
        if isinstance(keyitem, int):      # single item as key
            key = x[keyitem]
            value = tuple(x[:keyitem] + x[keyitem + 1:])
        else:
            key = tuple([x[i] for i in keyitem])
            value = tuple([x[i] for i in range(len(a_list)) if i not in keyitem])
        if len(value) == 1:      # single value
            value = value[0]
        if key not in _dict:
            if alwayslist:
                _dict[key] = [value, ]
            else:
                _dict[key] = value
        else:
            current_value = _dict[key]
            if not isinstance(current_value, list):
                current_value = [current_value, ]
            current_value.append(value)
            _dict[key] = current_value
    return _dict

def get_random_string():
    return base64.b64encode(os.urandom(6), random.sample(string.letters, 2))

def get_timestamp():
    return time.strftime('%Y%m%d')
