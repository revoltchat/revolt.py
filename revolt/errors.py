__all__ = (
    "RevoltError",
    "HTTPError",
    "ServerError",
    "FeatureDisabled",
    "AutumnDisabled",
)

class RevoltError(Exception):
    "Base exception for revolt"

class HTTPError(RevoltError):
    "Base exception for http errors"

class ServerError(RevoltError):
    "Internal server error"

class FeatureDisabled(RevoltError):
    """Base class for any any feature disabled"""

class AutumnDisabled(FeatureDisabled):
    """The autumn feature is disabled"""
