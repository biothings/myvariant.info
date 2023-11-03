import orjson
from biothings.utils.dotfield import merge_object


def make_object(attr, value):
    """
    Create dictionary following the input dot notation and the value
    Example::

        make_object('a.b.c', 100) --> {a:{b:{c:100}}}, or
        make_object(['a','b','c'], 100) --> {a:{b:{c:100}}}

    This is an orjson implementation of biothings.utils.dotfield.make_object, for better performance.
    TODO Merge into biothings.utils.dotfield if necessary. (And delete this function then.)
    """
    attr_list = attr.split(".")
    s = ""
    for k in attr_list:
        s += '{"' + k + '":'
    s += orjson.dumps(value).decode("utf-8")  # decoding is necessary because orjson dumps into bytes
    s += "}" * (len(attr_list))
    return orjson.loads(s)


def parse_dot_fields(genedoc):
    """
    parse_dot_fields({'a': 1, 'b.c': 2, 'b.a.c': 3})
     should return
        {'a': 1, 'b': {'a': {'c': 3}, 'c': 2}}

    This is a copy of biothings.utils.dotfield.parse_dot_fields. However here it uses the orjson make_object() function.
    TODO If orjson make_object() function is merged to biothings.utils.dotfield, this function can be deleted.
    """
    dot_fields = []
    expanded_doc = {}
    for key in genedoc:
        if key.find(".") != -1:
            dot_fields.append(key)
            expanded_doc = merge_object(expanded_doc, make_object(key, genedoc[key]))
    genedoc.update(expanded_doc)
    for key in dot_fields:
        del genedoc[key]
    return genedoc
