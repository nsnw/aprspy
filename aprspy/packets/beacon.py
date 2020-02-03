#!/usr/bin/env python

import logging

from ..exceptions import ParseError
from ..utils import APRSUtils
from .generic import GenericPacket

# Set up logging
logger = logging.getLogger(__name__)


class BeaconPacket(GenericPacket):
    """
    Class to represent beacon packets.

    See APRS 1.01 C4 P12
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._comment = None

    @property
    def comment(self) -> str:
        """Get the comment"""
        return self._comment

    @comment.setter
    def comment(self, value: str):
        """Set the comment"""
        self._comment = value

    def _parse(self) -> bool:
        """
        Parse a beacon packet.
        """

        self._comment = self._info
        logger.debug("Beacon packet comment is {}".format(self._comment))

        return True

    def __repr__(self):
        if self.source:
            return "<BeaconPacket: {}>".format(self.source)
        else:
            return "<BeaconPacket>"
