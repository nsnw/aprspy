#!/usr/bin/env python

import re
import logging

from ..exceptions import ParseError
from ..utils import APRSUtils
from .generic import GenericPacket

# Set up logging
logger = logging.getLogger(__name__)


class StationCapabilityPacket(GenericPacket):
    """
    Class to represent station capability packet.

    See APRS 1.01 C15 P77
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._status_message = None
        self._maidenhead_locator = None
        self.capabilities = []

    def _parse(self) -> bool:
        """ TODO """
        capabilities = self._info.split(",")

        for capability in capabilities:
            if "=" in capability:
                (token, value) = capability.split("=")
                self.capabilities.append((token, value))
            else:
                self.capabilities.append((capability,))

        return True

    def __repr__(self):
        if self.source:
            return "<StationCapabilityPacket: {}>".format(self.source)
        else:
            return "<StationCapabilityPacket>"
