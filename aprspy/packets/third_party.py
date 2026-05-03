#!/usr/bin/env python

import logging

from ..exceptions import ParseError
from .generic import GenericPacket

logger = logging.getLogger(__name__)


class ThirdPartyPacket(GenericPacket):
    """
    Class to represent third-party traffic packets (DTI '}').

    The information field contains a complete APRS packet relayed verbatim
    through a gateway. The inner packet is parsed recursively and exposed as
    the `inner_packet` attribute.

    See APRS 1.01 C17 P89.
    """

    @property
    def inner_raw(self) -> str | None:
        return getattr(self, '_inner_raw', None)

    @inner_raw.setter
    def inner_raw(self, value: str | None):
        self._inner_raw = value

    @property
    def inner_packet(self):
        return getattr(self, '_inner_packet', None)

    @inner_packet.setter
    def inner_packet(self, value):
        self._inner_packet = value

    def parse(self) -> bool:
        if not self._info:
            return True

        self.inner_raw = self._info

        # Lazy import avoids circular dependency (APRS.__init__ imports this module)
        from aprspy import APRS
        try:
            self.inner_packet = APRS.parse_packet(self._info)
        except Exception as e:
            raise ParseError(f"Could not parse inner packet in third-party traffic: {e}", self)

        return True

    def __repr__(self):
        if self.inner_packet:
            return f"<ThirdPartyPacket: {self.inner_packet!r}>"
        elif self.source:
            return f"<ThirdPartyPacket: {self.source}>"
        return "<ThirdPartyPacket>"
