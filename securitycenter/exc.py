class APIError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return "[{}] {}".format(self.code, self.message)

    def __repr__(self):
        return "{}({!r}, {!r})".format(self.__class__.__name__, self.code, self.message)


def raise_for_error(data):
    code = data["error_code"]
    message = data["error_msg"]

    if not code:
        return

    raise APIError(code, message)
