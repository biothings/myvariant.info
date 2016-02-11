import json
import datetime
import tornado.web
import traceback
from utils.ga import GAMixIn
from collections import OrderedDict

SUPPORT_MSGPACK = True
if SUPPORT_MSGPACK:
    import msgpack

    def msgpack_encode_datetime(obj):
        if isinstance(obj, datetime.datetime):
            return {'__datetime__': True, 'as_str': obj.strftime("%Y%m%dT%H:%M:%S.%f")}
        return obj


class DateTimeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        else:
            return super(DateTimeJSONEncoder, self).default(obj)


class BaseHandler(tornado.web.RequestHandler, GAMixIn):
    jsonp_parameter = 'callback'
    cache_max_age = 604800  # 7days
    disable_caching = False
    boolean_parameters = set(['raw', 'rawquery', 'fetch_all', 'explain', 'jsonld', 'hg38'])

    def write_error(self, status_code, **kwargs):
        """Override to implement custom error pages.

        ``write_error`` may call `write`, `render`, `set_header`, etc
        to produce output as usual.

        If this error was caused by an uncaught exception (including
        HTTPError), an ``exc_info`` triple will be available as
        ``kwargs["exc_info"]``.  Note that this exception may not be
        the "current" exception for purposes of methods like
        ``sys.exc_info()`` or ``traceback.format_exc``.
        """
        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            # in debug mode, try to send a traceback
            self.set_header('Content-Type', 'text/plain')
            for line in traceback.format_exception(*kwargs["exc_info"]):
                self.write(line)
            self.finish()
        else:
            if status_code == 404:
                #self.finish("<html><title>Special 404 Page</title>"
                #            "<body>This is a special 404 page.  We"
                #            " can put other stuff here, or make a special "
                #            "404 error template.</body></html>")
                self.return_json({'notfound': True, 'error': 'input id is invalid'})
            else:
                self.finish("<html><title>%(code)d: %(message)s</title>"
                            "<body>%(code)d: %(message)s</body></html>" % {
                                "code": status_code,
                                "message": self._reason,
                            })

    def _check_fields_param(self, kwargs):
        '''support "filter" as an alias of "fields" parameter for back-compatability.'''
        if 'filter' in kwargs and 'fields' not in kwargs:
            #support filter as an alias of "fields" parameter (back compatibility)
            kwargs['fields'] = kwargs['filter']
            del kwargs['filter']
        return kwargs

    def _check_paging_param(self, kwargs):
        '''support paging parameters, limit and skip as the aliases of size and from.'''
        if 'limit' in kwargs and 'size' not in kwargs:
            kwargs['size'] = kwargs['limit']
            del kwargs['limit']
        if 'skip' in kwargs and 'from' not in kwargs:
            kwargs['from'] = kwargs['skip']
            del kwargs['skip']
        if 'from' in kwargs:
            kwargs['from_'] = kwargs['from']   # elasticsearch python module using from_ for from parameter
            del kwargs['from']
        return kwargs

    def _check_boolean_param(self, kwargs):
        '''Normalize the value of boolean parameters.
           if 1 or true, set to True, otherwise False.
        '''
        for k in kwargs:
            if k in self.boolean_parameters:
                kwargs[k] = kwargs[k].lower() in ['1', 'true']
        return kwargs

    def get_query_params(self):
        _args = {}
        for k in self.request.arguments:
            v = self.get_arguments(k)
            if len(v) == 1:
                _args[k] = v[0]
            else:
                _args[k] = v
        _args.pop(self.jsonp_parameter, None)   # exclude jsonp parameter if passed.
        _args['host'] = self.request.host
        if SUPPORT_MSGPACK:
            _args.pop('msgpack', None)
        self._check_fields_param(_args)
        self._check_paging_param(_args)
        self._check_boolean_param(_args)
        return _args

    # def get_current_user(self):
    #     user_json = self.get_secure_cookie("user")
    #     if not user_json:
    #         return None
    #     return tornado.escape.json_decode(user_json)

    def _sort_response_object(self, d, depth=0):
        '''sort this dictionary.  max_depth is how many levels deep we should sort
           dictionary keys.  lists are included as a level.
           depth is the current depth, pretty basic recursion
        '''
        max_depth = 6
        depth += 1
        if (depth <= max_depth) and isinstance(d, list):
            return [self._sort_response_object(ds, depth) for ds in d]
        elif (depth <= max_depth) and isinstance(d, dict):
            return OrderedDict([(k, self._sort_response_object(d[k], depth)) for k in sorted(d)])
        else:
            return d

    def return_json(self, data, encode=True, indent=None):
        '''return passed data object as JSON response.
           if <jsonp_parameter> is passed, return a valid JSONP response.
           if encode is False, assumes input data is already a JSON encoded
           string.
        '''
        # call the recursive function to sort the data by keys
        data = self._sort_response_object(data, depth=0)

        indent = indent or 2   # tmp settings
        jsoncallback = self.get_argument(self.jsonp_parameter, '')  # return as JSONP
        if SUPPORT_MSGPACK:
            use_msgpack = self.get_argument('msgpack', '')
        if SUPPORT_MSGPACK and use_msgpack:
            _json_data = msgpack.packb(data, use_bin_type=True, default=msgpack_encode_datetime)
            self.set_header("Content-Type", "application/x-msgpack")
        else:
            _json_data = json.dumps(data, cls=DateTimeJSONEncoder, indent=indent) if encode else data
            self.set_header("Content-Type", "application/json; charset=UTF-8")
        if not self.disable_caching:
            #get etag if data is a dictionary and has "etag" attribute.
            etag = data.get('etag', None) if isinstance(data, dict) else None
            self.set_cacheable(etag=etag)
        self.support_cors()
        if jsoncallback:
            self.write('%s(%s)' % (jsoncallback, _json_data))
        else:
            self.write(_json_data)

    def set_cacheable(self, etag=None):
        '''set proper header to make the response cacheable.
           set etag if provided.
        '''
        self.set_header("Cache-Control", "max-age={}, public".format(self.cache_max_age))
        if etag:
            self.set_header('Etag', etag)

    def support_cors(self, *args, **kwargs):
        '''Provide server side support for CORS request.'''
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.set_header("Access-Control-Allow-Headers",
                        "Content-Type, Depth, User-Agent, X-File-Size, X-Requested-With, If-Modified-Since, X-File-Name, Cache-Control")
        self.set_header("Access-Control-Allow-Credentials", "false")
        self.set_header("Access-Control-Max-Age", "60")

    def options(self, *args, **kwargs):
        self.support_cors()


def add_apps(prefix='', app_list=[]):
    '''
    Add prefix to each url handler specified in app_list.

    add_apps('test', [('/', testhandler,
                      ('/test2', test2handler)])

    will return:
                     [('/test/', testhandler,
                      ('/test/test2', test2handler)])
    '''
    if prefix:
        return [('/'+prefix+url, handler) for url, handler in app_list]
    else:
        return app_list
