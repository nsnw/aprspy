#!/usr/bin/env python

import re
import logging

from ..exceptions import ParseError
from .position import PositionPacket

logger = logging.getLogger(__name__)


class ItemReportPacket(PositionPacket):
    """
    Class to represent item report packets.

    Items are a lightweight alternative to objects — no timestamp, variable-length
    name (3–9 chars). The data type identifier is ')'.

    Format: )ITEMNAME!DDMM.hhN/DDDMM.hhW$comment

    See APRS 1.01 C11 P59.
    """

    @property
    def item_name(self) -> str | None:
        return getattr(self, '_item_name', None)

    @item_name.setter
    def item_name(self, value: str | None):
        self._item_name = value

    @property
    def alive(self) -> bool | None:
        return getattr(self, '_alive', None)

    @alive.setter
    def alive(self, value: bool | None):
        self._alive = value

    def parse(self) -> bool:
        if not self._info:
            return True

        # Item name is 3-9 chars per spec, but senders occasionally use 10.
        m = re.match(r'^([^!_]{3,10})([!_])(.*)$', self._info)
        if not m:
            raise ParseError("Could not parse item name and status", self)

        name, live_killed, data = m.groups()
        self.item_name = name
        self.alive = live_killed == '!'

        logger.debug(f"Item name: {self.item_name!r}, alive: {self.alive}")

        if not data:
            raise ParseError("Missing position data in item report", self)

        self._parse_position_data(data)

        return True

    def __repr__(self):
        if self.item_name:
            return f"<ItemReportPacket: {self.item_name}>"
        elif self.source:
            return f"<ItemReportPacket: {self.source}>"
        else:
            return "<ItemReportPacket>"
