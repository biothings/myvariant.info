import sys
import time
from itertools import islice
import os.path
from shlex import shlex

str_types = str if sys.version_info.major == 3 else (str, unicode)


# ===============================================================================
# Misc. Utility functions
# ===============================================================================
def ask(prompt, options='YN'):
    '''Prompt Yes or No,return the upper case 'Y' or 'N'.'''
    options = options.upper()
    while 1:
        s = raw_input(prompt+'[%s]' % '|'.join(list(options))).strip().upper()
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
        in_f = gzip.GzipFile(infile, 'r')
    elif filetype == '.zip':
        import zipfile
        in_f = zipfile.ZipFile(infile, 'r').open(rawfile, 'r')
    else:
        in_f = file(infile, mode)
    return in_f


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
