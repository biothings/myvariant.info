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


def dump(obj, filename, bin=2, compress='gzip', verbose=False):
    '''Saves a compressed object to disk
       binary protocol 2 is compatible with py2, 3 and 4 are for py3
    '''
    if verbose:
        print('Dumping into "%s"...' % filename, end='')
    out_f = get_compressed_outfile(filename, compress=compress)
    pickle.dump(obj, out_f, protocol=bin)
    out_f.close()
    if verbose:
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

class LogPrint:
    def __init__(self, log_f, log=1, timestamp=0):
        '''If this class is set to sys.stdout, it will output both log_f and __stdout__.
           log_f is a file handler.
        '''
        self.log_f = log_f
        self.log = log
        self.timestamp = timestamp
        if self.timestamp:
            self.log_f.write('*'*10 + 'Log starts at ' + time.ctime() + '*'*10 + '\n')

    def write(self, text):
        sys.__stdout__.write(text)
        if self.log:
            self.log_f.write(text)
            self.flush()

    def flush(self):
        self.log_f.flush()

    def start(self):
        sys.stdout = self

    def pause(self):
        sys.stdout = sys.__stdout__

    def resume(self):
        sys.stdout = self

    def close(self):
        if self.timestamp:
            self.log_f.write('*'*10 + 'Log ends at ' + time.ctime() + '*'*10 + '\n')
        sys.stdout = sys.__stdout__
        self.log_f.close()

    def fileno(self):
        return self.log_f.fileno()


def safewfile(filename, prompt=True, default='C', mode='w'):
    '''return a file handle in 'w' mode,use alternative name if same name exist.
       if prompt == 1, ask for overwriting,appending or changing name,
       else, changing to available name automatically.'''
    suffix = 1
    while 1:
        if not os.path.exists(filename):
            break
        print('Warning:"%s" exists.' % filename, end='')
        if prompt:
            option = ask('Overwrite,Append or Change name?', 'OAC')
        else:
            option = default
        if option == 'O':
            if not prompt or ask('You sure?') == 'Y':
                print("Overwritten.")
                break
        elif option == 'A':
            print("Append to original file.")
            f = open(filename, 'a')
            f.write('\n' + "=" * 20 + 'Appending on ' + time.ctime() + "=" * 20 + '\n')
            return f, filename
        print('Use "%s" instead.' % addsuffix(filename, '_' + str(suffix)))
        filename = addsuffix(filename, '_' + str(suffix))
        suffix += 1
    return open(filename, mode), filename


def find_doc(k,keys):
    ''' Used by jsonld insertion in www.api.es._insert_jsonld '''
    n = len(keys)
    for i in range(n):
        # if k is a dictionary, then directly get its value
        if type(k) == dict:
            k = k[keys[i]]
        # if k is a list, then loop through k
        elif type(k) == list:
            tmp = []
            for item in k:
                try:
                    if type(item[keys[i]]) == dict:
                        tmp.append(item[keys[i]])
                    elif type(item[keys[i]]) == list:
                        for _item in item[keys[i]]:
                            tmp.append(_item)
                except:
                    continue
            k = tmp
    return k

