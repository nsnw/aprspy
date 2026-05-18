#!/usr/bin/env python

import re
import logging

from ..exceptions import ParseError
from ..utils import APRSUtils
from ..warnings import ParseWarningCode, ParseWarningSeverity
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

        # Locate the live/killed indicator ('*' or '_'). The spec requires a
        # 9-char space-padded name, but many senders omit the padding, so we
        # scan up to position 9 inclusive. Prefer '*' over '_' because '_' may
        # legitimately appear in object names.
        search_range = self._info[:min(11, len(self._info))]
        star_idx = search_range.find('*')
        kill_idx = search_range.find('_')

        if star_idx != -1:
            indicator_idx = star_idx
        elif kill_idx != -1:
            indicator_idx = kill_idx
        else:
            indicator_idx = None

        nonstandard_indicator = False
        if indicator_idx is None and len(self._info) >= 17:
            # Some firmware uses non-standard characters as the live/killed indicator.
            # Accept any character at position 9 if what follows looks like a valid
            # timestamp (6 digits + h/z//).
            if re.match(r'\d{6}[hz/]', self._info[10:17]):
                indicator_idx = 9
                nonstandard_indicator = True

        if indicator_idx is None:
            # No live/killed indicator at all — some older or hand-rolled stations
            # use ';' as a freeform bulletin/announcement channel. Treat the post-';'
            # text as the comment, default alive=True, and emit a LENIENT warning.
            self.object_name = None
            self.alive = True
            self.comment = self._info
            self._warn(
                ParseWarningCode.OBJECT_MISSING_INDICATOR,
                "No live/killed indicator; treating as freeform object/bulletin",
                ParseWarningSeverity.LENIENT,
            )
            return True

        self.object_name = self._info[:indicator_idx].rstrip()
        if nonstandard_indicator:
            self.alive = True
            self._warn(
                ParseWarningCode.OBJECT_NONSTANDARD_INDICATOR,
                f"Non-standard live/killed indicator {self._info[9:10]!r}; treating as live",
                ParseWarningSeverity.LENIENT,
            )
        else:
            self.alive = self._info[indicator_idx] == '*'
        logger.debug(f"Object name: {self.object_name!r}, alive: {self.alive}")

        # 7-char timestamp immediately follows the indicator
        ts_start = indicator_idx + 1
        ts_end = ts_start + 7

        if len(self._info) < ts_end:
            raise ParseError("Object packet too short", self)

        try:
            self.timestamp, self.timestamp_type = APRSUtils.decode_timestamp(
                self._info[ts_start:ts_end], self._parse_warnings, try_alternate_format=True
            )
        except ParseError as e:
            # Bad/placeholder timestamps (e.g. 111111z, 043516z with hour>23) are
            # common in the wild. Store None and continue to parse the position.
            logger.debug(f"Invalid timestamp in object packet, ignoring: {e}")
            self.timestamp = None
            self.timestamp_type = None

        logger.debug(f"Timestamp: {self.timestamp}")

        data = self._preprocess_position_data(self._info[ts_end:])
        if not data:
            return True

        if re.match(r'[0-9\s]{4}\.[0-9\s]{2}[NS].[0-9\s]{5}\.[0-9\s]{2}[EW]', data):
            self._parse_uncompressed(data)
        else:
            try:
                self._parse_compressed(data)
            except ParseError:
                # Non-position body (e.g. embedded telemetry T#...). Store raw.
                logger.debug(f"Couldn't parse object body as position, storing as comment")
                self.comment = data

        return True

    def __repr__(self):
        if self.object_name:
            return f"<ObjectPacket: {self.object_name}>"
        elif self.source:
            return f"<ObjectPacket: {self.source}>"
        else:
            return "<ObjectPacket>"
