"""Errors shared by Zentraly protocol and capability APIs."""


class ZentralyApiError(Exception):
    """Base Zentraly error."""


class ZentralyAuthenticationError(ZentralyApiError):
    """Authentication was rejected."""


class ZentralyConnectionError(ZentralyApiError):
    """The device could not be reached."""


class ZentralyConnectionBusyError(ZentralyConnectionError):
    """A request could not be sent because the local connection was saturated."""


class ZentralyInvalidResponseError(ZentralyApiError):
    """The device returned an invalid response."""


class ZentralyCommandRejectedError(ZentralyApiError):
    """The device rejected a command."""


class ZentralyValidationError(ZentralyApiError):
    """The requested value or operation is not supported by the model."""
