

class PypherException(Exception):
    pass


class PypherAliasException(PypherException):
    pass


class PypherArgumentException(PypherException, ValueError):
    pass
