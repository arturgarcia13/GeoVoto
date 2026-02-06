class GeoVotoError(Exception):
    """Base exception for GeoVoto application."""
    pass


class ConfigurationError(GeoVotoError):
    """Raised when there is a configuration error."""
    pass


class ValidationError(GeoVotoError):
    """Raised when data validation fails."""
    pass


class AuthenticationError(GeoVotoError):
    """Raised when authentication fails."""
    pass


class DatabaseError(GeoVotoError):
    """Raised when a database operation fails."""
    pass


class ResourceNotFoundError(GeoVotoError):
    """Raised when a requested resource is not found."""
    pass
