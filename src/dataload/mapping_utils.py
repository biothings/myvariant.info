# -*- coding: utf-8 -*-

"""
Utility functions for parsing flatfiles, 
mapping to JSON, cleaning.
"""
        
# remove keys whos values are ".", "-", "", "NA", "none", " "
# and remove empty dictionaries
def dict_sweep(d, vals):
    for key, val in d.items():
        if val in vals:
            del d[key]
        elif isinstance(val, list):
            d[key] = [dict_sweep(item, vals) for item in val if isinstance(item, dict)]
            if len(val) == 0:
                del d[key]
        elif isinstance(val, dict):
            dict_sweep(val, vals)
            if len(val) == 0:
                del d[key]
    return d

# convert string numbers into integers or floats
def value_convert(d):
    for key, val in d.items():
        try:
            d[key] = int(val)
        except (ValueError, TypeError):
            try:
                d[key] = float(val)
            except (ValueError, TypeError):
                pass
        if isinstance(val, dict):
            value_convert(val)
        elif isinstance(val, list):
            try:
                d[key] = [int(x) for x in val]
            except (ValueError, TypeError):
                try:
                    d[key] = [float(x) for x in val]
                except (ValueError, TypeError):
                    pass
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
            list_split(val)
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
    


