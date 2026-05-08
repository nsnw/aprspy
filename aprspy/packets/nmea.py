#!/usr/bin/env python

import logging
import re
from datetime import datetime, timezone

import pynmea2

from ..exceptions import ParseError
from ..warnings import ParseWarningCode
from .position import PositionPacket

logger = logging.getLogger(__name__)

SUPPORTED_SENTENCE_TYPES = {'GPRMC', 'GPGGA', 'GPGLL'}


class NMEAPacket(PositionPacket):
    """
    Class to represent raw NMEA position report packets.

    The data type identifier is '$'. The information field is a raw NMEA
    sentence (GPRMC, GPGGA, GPGLL are parsed; others are stored but not decoded).

    See APRS 1.01 C12 P64.
    """

    @property
    def sentence_type(self) -> str | None:
        return getattr(self, '_sentence_type', None)

    @sentence_type.setter
    def sentence_type(self, value: str | None):
        self._sentence_type = value

    @property
    def nmea_sentence(self) -> str | None:
        return getattr(self, '_nmea_sentence', None)

    @nmea_sentence.setter
    def nmea_sentence(self, value: str | None):
        self._nmea_sentence = value

    @property
    def checksum_valid(self) -> bool | None:
        return getattr(self, '_checksum_valid', None)

    @checksum_valid.setter
    def checksum_valid(self, value: bool | None):
        self._checksum_valid = value

    @staticmethod
    def _strip_checksum(sentence: str) -> str:
        """Return the sentence with the *XX checksum removed."""
        idx = sentence.rfind('*')
        return sentence[:idx] if idx != -1 else sentence

    @staticmethod
    def _truncate_after_checksum(sentence: str) -> tuple[str, str]:
        """Return (truncated_sentence, trailing_suffix).

        Strips any data after the 2-char hex checksum (*XX). Some stations
        append APRS path/comment suffixes (e.g. /W1) directly after the
        NMEA checksum; pynmea2 rejects these.
        """
        m = re.search(r'(\*[0-9A-Fa-f]{2})(.+)$', sentence)
        if m:
            return sentence[:m.end(1)], m.group(2)
        return sentence, ''

    def parse(self) -> bool:
        if not self._info:
            return True

        # Reconstruct the full NMEA sentence (data_type_id '$' was stripped)
        sentence = '$' + self._info

        # Strip any trailing non-NMEA suffix after the *XX checksum
        sentence, trailing = self._truncate_after_checksum(sentence)
        if trailing:
            self._warn(ParseWarningCode.NMEA_TRAILING_DATA,
                       f"Trailing data after NMEA checksum stripped: {trailing!r}")
        self.nmea_sentence = sentence

        # pynmea2 always validates a checksum when one is present, regardless
        # of the check= flag. Parse once to determine validity, then parse
        # without the checksum suffix for data extraction.
        try:
            msg = pynmea2.parse(sentence)
            self.checksum_valid = True
        except pynmea2.ChecksumError:
            self.checksum_valid = False
            self._warn(ParseWarningCode.NMEA_CHECKSUM_INVALID, f"NMEA checksum invalid for: {sentence!r}")
            # Re-parse without the checksum so we can still extract data
            try:
                msg = pynmea2.parse(self._strip_checksum(sentence))
            except (pynmea2.ParseError, pynmea2.SentenceTypeError) as e:
                raise ParseError(f"Could not parse NMEA sentence: {e}", self)
        except pynmea2.SentenceTypeError:
            # Unknown sentence type with valid or missing checksum — store raw and move on
            self.checksum_valid = None
            self.sentence_type = self._info.split(',')[0]
            logger.debug(f"Unknown NMEA sentence type: {self.sentence_type!r} — skipping decode")
            return True
        except pynmea2.ParseError as e:
            raise ParseError(f"Could not parse NMEA sentence: {e}", self)

        self.sentence_type = msg.sentence_type
        logger.debug(f"NMEA sentence type: {self.sentence_type}")

        if self.sentence_type == 'RMC':
            self._parse_rmc(msg)
        elif self.sentence_type == 'GGA':
            self._parse_gga(msg)
        elif self.sentence_type == 'GLL':
            self._parse_gll(msg)
        else:
            logger.debug(f"Unsupported NMEA sentence type: {self.sentence_type!r} — skipping decode")


        return True

    def _parse_rmc(self, msg):
        """Parse GPRMC: position, speed, course, datetime."""
        try:
            self.latitude = msg.latitude
            self.longitude = msg.longitude
        except AttributeError as e:
            raise ParseError(f"Missing position in GPRMC: {e}", self)

        try:
            if msg.spd_over_grnd is not None:
                self.speed = float(msg.spd_over_grnd)
        except (AttributeError, ValueError):
            pass

        try:
            if msg.true_course is not None:
                self.course = int(float(msg.true_course))
        except (AttributeError, ValueError):
            pass

        # Combine date + time into a UTC datetime if both are present
        try:
            if msg.datestamp and msg.timestamp:
                self.timestamp = datetime.combine(
                    msg.datestamp, msg.timestamp, tzinfo=timezone.utc
                )
                self.timestamp_type = 'zulu'
        except (AttributeError, ValueError, TypeError):
            pass

        self.compressed = False

    def _parse_gga(self, msg):
        """Parse GPGGA: position, altitude, fix quality."""
        try:
            self.latitude = msg.latitude
            self.longitude = msg.longitude
        except AttributeError as e:
            raise ParseError(f"Missing position in GPGGA: {e}", self)

        try:
            if msg.altitude is not None:
                # pynmea2 gives altitude in metres; convert to feet for consistency
                # with uncompressed APRS position packets
                self.altitude = round(float(msg.altitude) * 3.28084)
        except (AttributeError, ValueError):
            pass

        try:
            if msg.timestamp:
                self.timestamp = datetime.combine(
                    datetime.now(timezone.utc).date(), msg.timestamp, tzinfo=timezone.utc
                )
                self.timestamp_type = 'zulu'
        except (AttributeError, ValueError, TypeError):
            pass

        self.compressed = False

    def _parse_gll(self, msg):
        """Parse GPGLL: position and time."""
        try:
            self.latitude = msg.latitude
            self.longitude = msg.longitude
        except AttributeError as e:
            raise ParseError(f"Missing position in GPGLL: {e}", self)

        try:
            if msg.timestamp:
                self.timestamp = datetime.combine(
                    datetime.now(timezone.utc).date(), msg.timestamp, tzinfo=timezone.utc
                )
                self.timestamp_type = 'zulu'
        except (AttributeError, ValueError, TypeError):
            pass

        self.compressed = False

    def __repr__(self):
        if self.sentence_type:
            return f"<NMEAPacket: {self.sentence_type}>"
        elif self.source:
            return f"<NMEAPacket: {self.source}>"
        else:
            return "<NMEAPacket>"
