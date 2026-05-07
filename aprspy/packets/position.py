#!/usr/bin/env python

import re
import logging
import math

from enum import Enum
from typing import Tuple, Optional, Union

from ..exceptions import ParseError, GenerateError
from ..utils import APRSUtils
from .generic import GenericPacket

logger = logging.getLogger(__name__)


class CompressionFix(Enum):
    """GPS fix type. See APRS 1.01 C9 P39."""
    OLD = 0b00000000
    CURRENT = 0b00100000


class CompressionSource(Enum):
    """NMEA source type. See APRS 1.01 C9 P39."""
    OTHER = 0b00000000
    GLL = 0b00001000
    GGA = 0b00010000
    RMC = 0b00011000


class CompressionOrigin(Enum):
    """Compression origin. See APRS 1.01 C9 P39."""
    COMPRESSED = 0b00000000
    TNC_BTEXT = 0b00000001
    SOFTWARE = 0b00000010
    TBD = 0b00000011
    KPC3 = 0b00000100
    PICO = 0b00000101
    OTHER = 0b00000110
    DIGIPEATER = 0b00000111


class PositionPacket(GenericPacket):
    """
    Class to represent various kinds of position packets.

    This class represents packets which provide position information - including weather reports.
    """

    # -------------------------------------------------------------------------
    # Data type ID helpers
    # -------------------------------------------------------------------------

    @property
    def offset(self) -> int | None:
        try:
            if offset := self.info.find("!", 0, 40) != -1:
                return offset
        except AttributeError:
            return None
        return None

    def set_data_type_id(self, with_timestamp: bool, messaging_capable: bool):
        if with_timestamp and messaging_capable:
            self.data_type_id = "@"
        elif with_timestamp and not messaging_capable:
            self.data_type_id = "/"
        elif not with_timestamp and messaging_capable:
            self.data_type_id = "="
        else:
            self.data_type_id = "!"

    @property
    def with_timestamp(self) -> bool:
        if self.offset:
            return False
        return self.data_type_id in ["@", "/"]

    @with_timestamp.setter
    def with_timestamp(self, value: bool):
        self.set_data_type_id(with_timestamp=value, messaging_capable=self.messaging_capable)

    @property
    def messaging_capable(self) -> bool:
        if self.offset:
            return False
        return self.data_type_id in ["@", "="]

    @messaging_capable.setter
    def messaging_capable(self, value: bool):
        self.set_data_type_id(with_timestamp=self.with_timestamp, messaging_capable=value)

    # -------------------------------------------------------------------------
    # Position properties
    # -------------------------------------------------------------------------

    @property
    def latitude(self) -> float | None:
        return getattr(self, '_latitude', None)

    @latitude.setter
    def latitude(self, value: float | None):
        self._latitude = value

    @property
    def longitude(self) -> float | None:
        return getattr(self, '_longitude', None)

    @longitude.setter
    def longitude(self, value: float | None):
        self._longitude = value

    @property
    def ambiguity(self) -> int:
        return getattr(self, '_ambiguity', 0)

    @ambiguity.setter
    def ambiguity(self, value: int):
        self._ambiguity = value

    @property
    def speed(self) -> float | None:
        return getattr(self, '_speed', None)

    @speed.setter
    def speed(self, value: float | None):
        self._speed = value

    @property
    def course(self) -> int | None:
        return getattr(self, '_course', None)

    @course.setter
    def course(self, value: int | None):
        self._course = value

    @property
    def altitude(self) -> int | None:
        return getattr(self, '_altitude', None)

    @altitude.setter
    def altitude(self, value: int | None):
        self._altitude = value

    @property
    def comment(self) -> str | None:
        return getattr(self, '_comment', None)

    @comment.setter
    def comment(self, value: str | None):
        self._comment = value

    @property
    def compressed(self) -> bool:
        return getattr(self, '_compressed', False)

    @compressed.setter
    def compressed(self, value: bool):
        self._compressed = value

    @property
    def compression_fix(self) -> Optional[CompressionFix]:
        return getattr(self, '_compression_fix', None)

    @compression_fix.setter
    def compression_fix(self, value: Optional[CompressionFix]):
        self._compression_fix = value

    @property
    def compression_source(self) -> Optional[CompressionSource]:
        return getattr(self, '_compression_source', None)

    @compression_source.setter
    def compression_source(self, value: Optional[CompressionSource]):
        self._compression_source = value

    @property
    def compression_origin(self) -> Optional[CompressionOrigin]:
        return getattr(self, '_compression_origin', None)

    @compression_origin.setter
    def compression_origin(self, value: Optional[CompressionOrigin]):
        self._compression_origin = value

    # PHG / RNG / DFS properties

    @property
    def power(self) -> int | None:
        return getattr(self, '_power', None)

    @power.setter
    def power(self, value: int | None):
        self._power = value

    @property
    def height(self) -> int | None:
        return getattr(self, '_height', None)

    @height.setter
    def height(self, value: int | None):
        self._height = value

    @property
    def gain(self) -> int | None:
        return getattr(self, '_gain', None)

    @gain.setter
    def gain(self, value: int | None):
        self._gain = value

    @property
    def directivity(self) -> int | None:
        return getattr(self, '_directivity', None)

    @directivity.setter
    def directivity(self, value: int | None):
        self._directivity = value

    @property
    def radio_range(self) -> int | None:
        return getattr(self, '_radio_range', None)

    @radio_range.setter
    def radio_range(self, value: int | None):
        self._radio_range = value

    @property
    def strength(self) -> int | None:
        return getattr(self, '_strength', None)

    @strength.setter
    def strength(self, value: int | None):
        self._strength = value

    @property
    def bearing(self) -> int | None:
        return getattr(self, '_bearing', None)

    @bearing.setter
    def bearing(self, value: int | None):
        self._bearing = value

    @property
    def number(self) -> float | None:
        return getattr(self, '_number', None)

    @number.setter
    def number(self, value: float | None):
        self._number = value

    @property
    def df_range(self) -> int | None:
        return getattr(self, '_df_range', None)

    @df_range.setter
    def df_range(self, value: int | None):
        self._df_range = value

    @property
    def quality(self) -> int | None:
        return getattr(self, '_quality', None)

    @quality.setter
    def quality(self, value: int | None):
        self._quality = value

    # -------------------------------------------------------------------------
    # Parsing helpers
    # -------------------------------------------------------------------------

    @staticmethod
    def _parse_uncompressed_position(data: str) -> Tuple[float, float, int, str, str]:
        """Parse lat, lng, ambiguity, symbol_table, symbol_id from uncompressed position data."""
        try:
            lat, ambiguity = APRSUtils.decode_uncompressed_latitude(data[0:8])
        except ValueError as e:
            raise ParseError("Invalid latitude: {}".format(e))

        try:
            lng = APRSUtils.decode_uncompressed_longitude(data[9:18], ambiguity)
        except ValueError as e:
            raise ParseError("Invalid longitude: {}".format(e))

        logger.debug("Latitude: {} ({}) Longitude: {}".format(lat, ambiguity, lng))

        symbol_table = data[8]
        logger.debug("Symbol table: {}".format(symbol_table))

        try:
            symbol_id = data[18]
            logger.debug("Symbol: {}".format(symbol_id))
        except IndexError:
            symbol_id = None
            logger.debug("Symbol identifier missing (truncated packet)")

        return (lat, lng, ambiguity, symbol_table, symbol_id)

    @staticmethod
    def _parse_compressed_byte(compression_byte: str) -> Tuple[
        'CompressionFix', 'CompressionSource', 'CompressionOrigin'
    ]:
        """Parse the compression type byte into fix, source, and origin enums."""
        t = ord(compression_byte) - 33

        for fix in iter(CompressionFix):
            if t | fix.value:
                break
        else:
            raise ParseError("Could not determine compression fix type ({})".format(bin(t)))

        for source in iter(CompressionSource):
            if t | source.value:
                break
        else:
            raise ParseError("Could not determine compression source type ({})".format(bin(t)))

        for origin in iter(CompressionOrigin):
            if t | origin.value:
                break
        else:
            raise ParseError("Could not determine compression origin type ({})".format(bin(t)))

        return (fix, source, origin)

    @classmethod
    def _parse_compressed_position(cls, data: str) -> Tuple[
        float, float,
        Optional[float], Optional[int], Optional[float], Optional[float],
        Optional['CompressionFix'], Optional['CompressionSource'], Optional['CompressionOrigin']
    ]:
        """Parse lat, lng, and optional altitude/course/speed/range from compressed position data."""
        if len(data) < 13:
            raise ValueError("Compressed position data must be at least 13 characters")

        logger.debug("Compressed lat/lng: {}".format(data))

        latitude = APRSUtils.decode_compressed_latitude(data[1:5])
        longitude = APRSUtils.decode_compressed_longitude(data[5:9])

        logger.debug("Latitude: {} Longitude: {}".format(latitude, longitude))

        comp_type = "{:0>8b}".format(ord(data[12]) - 33)[::-1]

        altitude = None
        course = None
        speed = None
        radio_range = None

        if data[10] == " ":
            fix = source = origin = None
            logger.debug("No course, speed or range data")

        elif comp_type[3] == "0" and comp_type[4] == "1":
            c = ord(data[10]) - 33
            s = ord(data[11]) - 33
            altitude = round(1.002 ** (c * 91 + s), 2)
            fix, source, origin = cls._parse_compressed_byte(data[12])
            logger.debug("Altitude: {}".format(altitude))

        elif 0 <= (ord(data[10]) - 33) <= 89:
            c = ord(data[10]) - 33
            course = c * 4
            s = ord(data[11]) - 33
            speed = round((1.08 ** s) - 1, 1)
            fix, source, origin = cls._parse_compressed_byte(data[12])
            logger.debug("Course: {} Speed: {}".format(course, speed))

        elif data[10] == "{":
            s = ord(data[11]) - 33
            radio_range = round(2 * (1.08 ** s), 2)
            fix, source, origin = cls._parse_compressed_byte(data[12])
            logger.debug("Radio range: {}".format(radio_range))

        else:
            raise ValueError(
                "Invalid character when looking for course/speed or range: {}".format(data[10])
            )

        return (latitude, longitude, altitude, course, speed, radio_range, fix, source, origin)

    @staticmethod
    def _parse_data(data: str) -> Tuple[
        Optional[str], Optional[str], Optional[str],
        Optional[int], Optional[int], Optional[int], Optional[str]
    ]:
        """Parse PHG/RNG/DFS/course/speed/altitude/comment from the trailing info field."""
        phg = rng = dfs = course = speed = altitude = comment = None

        if re.match(r'^PHG[0-9]{4}', data[:7]):
            phg = data[3:7]
            logger.debug("PHG: {}".format(phg))
            data = data[7:]

        elif re.match(r'^RNG[0-9]{4}', data[:7]):
            rng = data[3:7]
            logger.debug("RNG: {}".format(rng))
            data = data[7:]

        elif re.match(r'^DFS[0-9]{4}', data[:7]):
            dfs = data[3:7]
            logger.debug("DFS: {}".format(dfs))
            data = data[7:]

        elif re.match(r'^[0-9]{3}/[0-9]{3}', data[:7]):
            course = int(data[:3])
            speed = int(data[4:7])
            logger.debug("Course: {} Speed: {}".format(course, speed))
            data = data[7:]

        if data:
            has_altitude = re.match(r'.*/A=([0-9]{6}).*', data)
            if has_altitude:
                altitude = int(has_altitude.group(1))
                logger.debug("Altitude: {} ft".format(altitude))
                data = re.sub(r'/A=[0-9]{6}', "", data)
            comment = data
            logger.debug("Comment: {}".format(comment))

        return (phg, rng, dfs, course, speed, altitude, comment)

    # -------------------------------------------------------------------------
    # Parse
    # -------------------------------------------------------------------------

    def parse(self) -> bool:
        """Parse a position packet, populating lat/lng/symbol/comment and related fields."""
        if not self._info:
            return True

        data = self._info

        if self.data_type_id in ['@', '/']:
            if len(data) < 7:
                raise ParseError("Missing timestamp in position packet", self)
            try:
                self.timestamp, self.timestamp_type = APRSUtils.decode_timestamp(data[0:7], self._parse_warnings)
                data = data[7:]
            except ParseError:
                # Invalid or placeholder timestamp (e.g. '<data>z', '......z', or omitted
                # entirely). Try full data first (handles no-timestamp '/' packets), then
                # skip 7 chars (handles fixed-width placeholders like '<data>z').
                self.timestamp = None
                self.timestamp_type = None
                logger.debug(f"Unrecognised timestamp {data[0:7]!r}, attempting position recovery")
                for candidate in (data, data[7:] if len(data) > 7 else None):
                    if candidate is None:
                        continue
                    try:
                        self._parse_position_data(candidate)
                        return True
                    except ParseError:
                        continue
                raise ParseError("No valid timestamp or position data found", self)

        self._parse_position_data(data)
        return True

    def _parse_position_data(self, data: str):
        """Parse position data as uncompressed, compressed, or X1J-offset fallback."""
        if re.match(r'[0-9\s]{4}\.[0-9\s]{2}[NS].[0-9\s]{5}\.[0-9\s]{2}[EW]', data):
            self._parse_uncompressed(data)
            return

        try:
            self._parse_compressed(data)
            return
        except ParseError:
            pass

        # X1J-style fallback: some TNC firmware (e.g. Kenwood X1J) prepends a header
        # before the actual position, delimited by '!'. Only try this for '!' DTI.
        if self.data_type_id == '!':
            excl_idx = self._info.find('!', 1, 40)
            if excl_idx > 0:
                x1j_data = self._info[excl_idx + 1:]
                if re.match(r'[0-9\s]{4}\.[0-9\s]{2}[NS].[0-9\s]{5}\.[0-9\s]{2}[EW]', x1j_data):
                    self._parse_uncompressed(x1j_data)
                    return
                self._parse_compressed(x1j_data)
                return

        raise ParseError("Couldn't parse position data", self)

    def _parse_uncompressed(self, data: str):
        (self.latitude, self.longitude, self.ambiguity,
         self.symbol_table, self.symbol_id) = self._parse_uncompressed_position(data)
        self.compressed = False

        if len(data) <= 19:
            return

        phg, rng, dfs, self.course, self.speed, self.altitude, comment = self._parse_data(
            data[19:]
        )

        if phg:
            self.power, self.height, self.gain, self.directivity = APRSUtils.decode_phg(phg)
        elif rng:
            self.radio_range = int(rng)
        elif dfs:
            self.strength, self.height, self.gain, self.directivity = APRSUtils.decode_dfs(dfs)

        self.comment = comment
        self._decode_weather_if_present()

    def _parse_compressed(self, data: str):
        try:
            (self.latitude, self.longitude, self.altitude, self.course, self.speed,
             self.radio_range, self.compression_fix, self.compression_source,
             self.compression_origin) = self._parse_compressed_position(data[0:13])
        except Exception as e:
            raise ParseError("Couldn't parse compressed position: {}".format(e))

        self.compressed = True
        self.symbol_table = data[0]
        self.symbol_id = data[9]
        self.ambiguity = 0
        self.comment = data[13:] if len(data) > 13 else None
        self._decode_weather_if_present()

    def _decode_weather_if_present(self):
        """If the symbol indicates a weather station, parse weather fields from comment."""
        if self.symbol_id != '_' or not self.comment:
            return
        # Lazy import to avoid circular dependency (weather.py extends PositionPacket)
        from .weather import parse_weather_data
        fields = parse_weather_data(self.comment)
        for key, val in fields.items():
            setattr(self, key, val)
