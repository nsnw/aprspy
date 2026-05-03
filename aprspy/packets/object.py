#!/usr/bin/env python

import re
import logging

from ..exceptions import ParseError
from ..utils import APRSUtils
from .position import PositionPacket

logger = logging.getLogger(__name__)


class ObjectPacket(PositionPacket):
    """
    Class to represent object report packets.

    Object packets place a named point on the map, independent of any physical
    transmitter at that location. The data type identifier is ';'.

    Format: ;OBJECTNAME*DDHHMMzDDMM.hhN/DDDMM.hhW$CSE/SPD/comment

    See APRS 1.01 C11 P57.
    """

    @property
    def object_name(self) -> str | None:
        return getattr(self, '_object_name', None)

    @object_name.setter
    def object_name(self, value: str | None):
        self._object_name = value

    @property
    def alive(self) -> bool | None:
        return getattr(self, '_alive', None)

    @alive.setter
    def alive(self, value: bool | None):
        self._alive = value

    def parse(self) -> bool:
        if not self._info:
            return True

        if len(self._info) < 17:
            raise ParseError("Object packet too short", self)

        # First 9 characters are the object name, space-padded
        self.object_name = self._info[0:9].rstrip()

        # Character 10 is the live/killed indicator
        live_killed = self._info[9]
        if live_killed == '*':
            self.alive = True
        elif live_killed == '_':
            self.alive = False
        else:
            raise ParseError(f"Invalid live/killed indicator: {live_killed!r}", self)

        logger.debug(f"Object name: {self.object_name!r}, alive: {self.alive}")

        # Characters 11-17 are the timestamp (7 chars)
        try:
            self.timestamp, self.timestamp_type = APRSUtils.decode_timestamp(self._info[10:17])
        except ParseError:
            raise ParseError("Invalid timestamp in object packet", self)

        logger.debug(f"Timestamp: {self.timestamp}")

        # Remaining data is the position
        data = self._info[17:]

        if re.match(r'[0-9\s]{4}\.[0-9\s]{2}[NS].[0-9\s]{5}\.[0-9\s]{2}[EW]', data):
            self._parse_uncompressed(data)
        else:
            self._parse_compressed(data)

        return True

    def __repr__(self):
        if self.object_name:
            return f"<ObjectPacket: {self.object_name}>"
        elif self.source:
            return f"<ObjectPacket: {self.source}>"
        else:
            return "<ObjectPacket>"
