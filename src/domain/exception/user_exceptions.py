class UserDomainException(Exception):
    """Base exception for user domain errors."""

    pass


class UserNotFoundException(UserDomainException):
    """Raised when a user is not found with an email address."""

    pass


class UserAlreadyActiveException(UserDomainException):
    """Raised when trying to activate an already active user."""

    pass


class InvalidActivationCodeException(UserDomainException):
    """Raised when the provided activation code is invalid."""

    pass


class ExpiredActivationCodeException(UserDomainException):
    """Raised when the provided activation code is expired."""

    pass


class EmailAlreadyExistsException(UserDomainException):
    """Raised when trying to register an email that already exists."""

    pass


class InvalidCredentialsException(UserDomainException):
    """Raised when trying to activate an account with invalid user password"""

    pass
