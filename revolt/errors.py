class RevoltError(Exception):
    "Base exception for revolt"

class HTTPError(RevoltError):
    "Base exception for http errors"

class ServerError(RevoltError):
    "Internal server error"
