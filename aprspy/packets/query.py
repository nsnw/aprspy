#!/usr/bin/env python

import re
import logging

from ..exceptions import ParseError
from .generic import GenericPacket

logger = logging.getLogger(__name__)


class QueryPacket(GenericPacket):
    """
    Class to represent general query packets (DTI '?').

    Format: ?QueryType?{Target}
    where QueryType is a keyword (APRS, WX, IGATE, SERVERS, etc.)
    and the optional Target is a callsign suffix for directed queries.

    See APRS 1.01 C15 P85.
    """

    @property
    def query_type(self) -> str | None:
        return getattr(self, '_query_type', None)

    @query_type.setter
    def query_type(self, value: str | None):
        self._query_type = value

    @property
    def target(self) -> str | None:
        return getattr(self, '_target', None)

    @target.setter
    def target(self, value: str | None):
        self._target = value

    def parse(self) -> bool:
        if not self._info:
            return True

        # Info field is everything after the leading '?' DTI, e.g. "APRS?" or "APRS?XX1XX-9"
        m = re.match(r'^([A-Za-z0-9]+)\?(.*)$', self._info)
        if not m:
            raise ParseError(f"Could not parse query packet info: {self._info!r}", self)

        self.query_type = m.group(1).upper()
        target = m.group(2).strip()
        self.target = target if target else None

        return True

    def __repr__(self):
        if self.query_type:
            return f"<QueryPacket: {self.query_type}>"
        elif self.source:
            return f"<QueryPacket: {self.source}>"
        return "<QueryPacket>"
