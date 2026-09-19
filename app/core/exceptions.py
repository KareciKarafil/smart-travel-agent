class ApplicationError(Exception):
    """Base exception for application errors."""


class ExternalServiceError(ApplicationError):
    """Raised when an external API cannot complete a request."""


class LocationNotFoundError(ApplicationError):
    """Raised when a requested location cannot be found."""