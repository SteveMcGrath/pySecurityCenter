class APIError(Exception):
    """Raised when an error is received in an API response.

    :param code: internal error code
    :param message: error message in response
    """

    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return '[{0}] {1}'.format(self.code, self.message)

    def __repr__(self):
        return '{0}({1!r}, {2!r})'.format(self.__class__.__name__,
                                          self.code, self.message)


class CoreError(Exception):
    """Raised when something in the Python API wrapper goes wrong."""
    pass


def raise_for_error(data):
    """Check if there was an error in an API response.

    If an error is present, extract it and raise an ``APIError``.

    :param data: API response data
    :return: None if no error
    :raise: APIError if error is present
    """

    try:
        code = data['error_code']
    except KeyError:
        return

    message = data['error_msg']

    # code 0 is an OK response, all others are errors
    if not code:
        return

    raise APIError(code, message)
