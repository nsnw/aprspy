import logging

# Set up logging
logger = logging.getLogger(__name__)


class APRSException(Exception):
    pass


class ParseError(APRSException):
    """
    Parsing exception
    """
    def __init__(self, message: str, packet=None):
        super().__init__(message)

        self.packet = packet


class GenerateError(APRSException):
    """
    Generating exception
    """
    def __init__(self, message: str, packet=None):
        super().__init__(message)

        self.packet = packet


class UnsupportedError(APRSException):
    """
    Thrown when packets are of an unsupported format
    """
    def __init__(self, message: str, packet=None):
        super().__init__(message)

        self.packet = packet


class InvalidSourceException(APRSException):
    """
    Thrown when a source value is invalid.
    """
    pass


class InvalidDestinationException(APRSException):
    """
    Thrown when a destination value is invalid.
    """
    pass
