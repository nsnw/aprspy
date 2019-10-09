#!/usr/bin/env python

import logging

# Set up logging
logger = logging.getLogger(__name__)


class ParseError(Exception):
    """
    Parsing exception
    """
    def __init__(self, message: str, packet=None):
        super(ParseError, self).__init__(message)

        self.packet = packet


class UnsupportedError(Exception):
    """
    Thrown when packets are of an unsupported format
    """
    def __init__(self, message: str, packet=None):
        super(UnsupportedError, self).__init__(message)

        self.packet = packet
