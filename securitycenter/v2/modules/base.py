from functools import wraps


class Module(object):
    """API module that knows how to perform actions.

    :param sc: SecurityCenter connection
    """

    _name = ''
    """sc internal name of module"""

    def __init__(self, sc):
        self._sc = sc

    def _request(self, action, input=None, file=None, parse=True):
        """Make an API call to action under the current module.

        :param action: name of action in module
        :param input: any arguments to be passed to the module::action
        :type input: dict
        :param file: file data to upload
        :type file: file
        :param parse: if False, don't parse response as JSON

        :return: dict containing API response, or ``Response`` if parse
                is False
        """

        return self._sc._request(self._name, action, input, file, parse)


class _Empty(object):
    pass


def extract_value(key, default=_Empty, _all_key='_all'):
    """Extract the value of a key from a returned dict.

    Creates a decorator that will get the value of a key from a function
    returning a dictionary.

    When calling the decorated function, set ``_all`` to True to make
    this a no-op and return the entire dictionary.

    If the function requires that ``_all`` is set for some input, add
    the key _all to the returned dictionary.  For example, normally
    return a filename, but if called as ``f(..., verbose=True)``,
    return the file stats also.

    :param key: key to get from return
    :param default: if set, return this if key is not present, otherwise
            raise KeyError
    :param _all_key: name of param for '_all_' behavior (default '_all')

    :raise KeyError: if key not in dict and no default

    :return: extracted value
    """

    #TODO use generator send() to allow pre- and post-processing?

    def decorator(f):
        @wraps(f)
        def inner(*args, **kwargs):
            no_extract = kwargs.pop(_all_key, False)
            res = f(*args, **kwargs)
            no_extract = res.pop(_all_key, no_extract)
            if no_extract:
                return res
            if default is _Empty:
                return res.get(key)
            return res.get(key, default)
        return inner
    return decorator
