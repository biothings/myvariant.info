from __future__ import print_function
#from __future__ import unicode_literals
import itertools
import csv
from utils.common import open_anyfile, is_str
"""
Utility functions for parsing flatfiles,
mapping to JSON, cleaning.
"""


# remove keys whos values are ".", "-", "", "NA", "none", " "
# and remove empty dictionaries
def dict_sweep(d, vals=[".", "-", "", "NA", "none", " ", "Not Available", "unknown"]):
    """
    @param d: a dictionary
    @param vals: a string or list of strings to sweep
    """
    for key, val in d.items():
        if val in vals:
            del d[key]
        elif isinstance(val, list):
            for item in val:
                if item in vals:
                    val.remove(item)
                elif isinstance(item, dict):
                    dict_sweep(item, vals)
            if len(val) == 0:
                del d[key]
        elif isinstance(val, dict):
            dict_sweep(val, vals)
            if len(val) == 0:
                del d[key]
    return d


def to_number(val):
    """convert an input string to int/float."""
    if is_str(val):
        try:
            return int(val)
        except ValueError:
            try:
                return float(val)
            except ValueError:
                pass
    return val


def value_convert(d):
    """convert string numbers into integers or floats"""
    for key, val in d.items():
        if isinstance(val, dict):
            value_convert(val)
        elif isinstance(val, list):
            d[key] = [to_number(x) for x in val]
        elif isinstance(val, tuple):
            d[key] = tuple([to_number(x) for x in val])
        else:
            d[key] = to_number(val)
    return d


# if dict value is a list of length 1, unlist
def unlist(d):
    for key, val in d.items():
            if isinstance(val, list):
                if len(val) == 1:
                    d[key] = val[0]
            elif isinstance(val, dict):
                unlist(val)
    return d


# split fields by sep into comma separated lists, strip.
def list_split(d, sep):
    for key, val in d.items():
        if isinstance(val, dict):
            list_split(val, sep)
        try:
            if len(val.split(sep)) > 1:
                d[key] = val.rstrip().rstrip(sep).split(sep)
        except (AttributeError):
            pass
    return d


def id_strip(id_list):
    id_list = id_list.split("|")
    ids = []
    for id in id_list:
        ids.append(id.rstrip().lstrip())
    return ids


def merge_duplicate_rows(rows, db):
    """
    @param rows: rows to be grouped by
    @param db: database name, string
    """
    rows = list(rows)
    first_row = rows[0]
    other_rows = rows[1:]
    for row in other_rows:
        for i in first_row[db]:
            if i in row[db]:
                if row[db][i] != first_row[db][i]:
                    aa = first_row[db][i]
                    if not isinstance(aa, list):
                        aa = [aa]
                    aa.append(row[db][i])
                    first_row[db][i] = aa
            else:
                continue
    return first_row


def unique_ids(src_module):
    i = src_module.load_data()
    out = list(i)
    id_list = [a['_id'] for a in out if a]
    myset = set(id_list)
    print(len(out), "Documents produced")
    print(len(myset), "Unique IDs")
    return out


def rec_handler(infile, block_end='\n', skip=0, include_block_end=False, as_list=False):
    '''A generator to return a record (block of text)
       at once from the infile. The record is separated by
       one or more empty lines by default.
       skip can be used to skip top n-th lines
       if include_block_end is True, the line matching block_end will also be returned.
       if as_list is True, return a list of lines in one record.
    '''
    rec_separator = lambda line: line == block_end
    with open_anyfile(infile) as in_f:
        if skip:
            for i in range(skip):
                in_f.readline()
        for key, group in itertools.groupby(in_f, rec_separator):
            if not key:
                if include_block_end:
                    _g = itertools.chain(group, (block_end,))
                yield (list(_g) if as_list else ''.join(_g))


def tabfile_feeder(datafile, header=1, sep='\t',
                   includefn=None,
                   # coerce_unicode=True,   # no need here because importing unicode_literals at the top
                   assert_column_no=None):
    '''a generator for each row in the file.'''

    with open_anyfile(datafile) as in_f:
        reader = csv.reader(in_f, delimiter=sep)
        lineno = 0
        try:
            for i in range(header):
                reader.next()
                lineno += 1

            for ld in reader:
                if assert_column_no:
                    if len(ld) != assert_column_no:
                        err = "Unexpected column number:" \
                              " got {}, should be {}".format(len(ld), assert_column_no)
                        raise ValueError(err)
                if not includefn or includefn(ld):
                    lineno += 1
                    # if coerce_unicode:
                    #     yield [unicode(x, encoding='utf-8', errors='replace') for x in ld]
                    # else:
                    #     yield ld
                    yield ld
        except ValueError:
            print("Error at line number:", lineno)
            raise
