#!/usr/bin/env python

import re
import logging
import math

from enum import Enum
from geopy.point import Point

from typing import Tuple, Optional, Union

from ..exceptions import ParseError, GenerateError
from ..utils import APRSUtils
from .generic import GenericPacket

# Set up logging
logger = logging.getLogger(__name__)


class CompressionFix(Enum):
    """
    Enum to represent GPS fix types.

    See APRS 1.01 C9 P39.

    * `OLD` - old (last) GPS fix
    * `CURRENT` - current GPS fix
    """
    OLD = 0b00000000
    CURRENT = 0b00100000


class CompressionSource(Enum):
    """
    Enum to represent NMEA sources.

    See APRS 1.01 C9 P39.

    * `OTHER` - other
    * `GLL` - GPS GLL
    * `GGA` - GPS GGA
    * `RMC` - GPS RMC

    See https://www.gpsinformation.org/dale/nmea.htm for an explanation of the various GPS
    sentence types.
    """
    OTHER = 0b00000000
    GLL = 0b00001000
    GGA = 0b00010000
    RMC = 0b00011000


class CompressionOrigin(Enum):
    """
    Enum to represent the compression origin.

    See APRS 1.01 C9 P39.

    * `COMPRESSED` - Compressed
    * `TNC_BTEXT` - TNC BText
    * `SOFTWARE` - Software applications
    * `TBD` - TBD
    * `KPC3` - KPC3 TNC
    * `PICO` - Pico
    * `OTHER` - Other trackers
    * `DIGIPEATER` - Digipeater conversion
    """
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

    def __init__(self, latitude: float = 0.0, longitude: float = 0.0, ambiguity: int = 0,
                 course: int = None, speed: float = None, altitude: int = None, comment: str = None,
                 power: int = None, height: int = None, gain: int = None, directivity: int = None,
                 radio_range: int = None, strength: int = None, bearing: int = None,
                 number: float = None, df_range: int = None, quality: int = None,
                 compressed: bool = False, messaging: bool = False, data_type_id: str = "!",
                 compression_fix: CompressionFix = None,
                 compression_source: CompressionSource = None,
                 compression_origin: CompressionOrigin = None,
                 *args, **kwargs):

        super().__init__(*args, **kwargs, data_type_id=data_type_id)
        self._point = Point()
        self.latitude = latitude
        self.longitude = longitude
        self.ambiguity = ambiguity
        self.course = course
        self.speed = speed
        self.altitude = altitude
        self.comment = comment
        self.messaging = messaging

        # PHG/RNG/DFS/BRG/NRQ
        self.power = power
        self.height = height
        self.gain = gain
        self.directivity = directivity
        self.radio_range = radio_range
        self.strength = strength
        self.bearing = bearing
        self.number = number
        self.df_range = df_range
        self.quality = quality

        # Compression
        self.compressed = compressed
        self.compression_fix = compression_fix
        self.compression_source = compression_source
        self.compression_origin = compression_origin

    @property
    def point(self) -> Point:
        """Get a point representing the latitude, longitude and optionally the altitude"""
        return self._point

    @point.setter
    def point(self, value: Point):
        """Set a point representing the latitude, longitude and optionally the altitude"""
        self._point = value

    @property
    def latitude(self) -> float:
        """Get the latitude of the station"""
        return round(self._point.latitude, 6)

    @latitude.setter
    def latitude(self, value: float):
        """Set the latitude of the station"""
        self._point.latitude = value

    @property
    def longitude(self) -> float:
        """Get the longitude of the station"""
        return round(self._point.longitude, 6)

    @longitude.setter
    def longitude(self, value: float):
        """Set the longitude of the station"""
        self._point.longitude = value

    @property
    def ambiguity(self) -> int:
        """Get the ambiguity level of the packet"""
        return self._ambiguity

    @ambiguity.setter
    def ambiguity(self, value: int):
        """Set the ambiguity level of the packet"""
        self._ambiguity = value

    @property
    def course(self) -> int:
        """Get the course of the station"""
        return self._course

    @course.setter
    def course(self, value: int):
        """Set the course of the station"""
        self._course = value

    @property
    def speed(self) -> float:
        """Get the speed of the station"""
        return self._speed

    @speed.setter
    def speed(self, value: float):
        """Set the speed of the station"""
        self._speed = value

    @property
    def altitude(self) -> int:
        """Get the altitude of the station"""
        return self._point.altitude

    @altitude.setter
    def altitude(self, value: int):
        """Set the altitude of the station"""
        self._point.altitude = value

    @property
    def comment(self) -> str:
        """Get the packet's comment"""
        return self._comment

    @comment.setter
    def comment(self, value: str):
        """Set the packet's comment"""
        self._comment = value

    @property
    def power(self) -> int:
        """Get the power (in watts)"""
        return self._power

    @power.setter
    def power(self, value: int):
        """Set the power (in watts)"""
        self._power = value

    @property
    def height(self) -> int:
        """Get the antenna height above average terrain (in feet)"""
        return self._height

    @height.setter
    def height(self, value: int):
        """Set the antenna height above average terrain (in feet)"""
        self._height = value

    @property
    def gain(self) -> int:
        """Get the antenna gain (in dB)"""
        return self._gain

    @gain.setter
    def gain(self, value: int):
        """Set the antenna gain (in dB)"""
        self._gain = value

    @property
    def directivity(self) -> int:
        """Get the antenna directivity (in degrees)"""
        return self._directivity

    @directivity.setter
    def directivity(self, value: int):
        """Set the antenna directivity (in degrees)"""
        self._directivity = value

    @property
    def radio_range(self) -> int:
        """Get the radio range (in miles)"""
        return self._radio_range

    @radio_range.setter
    def radio_range(self, value: int):
        """Set the radio range (in miles)"""
        self._radio_range = value

    @property
    def strength(self) -> int:
        """Get the DF signal strength (in S-points)"""
        return self._strength

    @strength.setter
    def strength(self, value: int):
        """Set the DF signal strength (in S-points)"""
        self._strength = value

    @property
    def bearing(self) -> int:
        """Get the DF signal bearing (in degrees)"""
        return self._bearing

    @bearing.setter
    def bearing(self, value: int):
        """Set the DF signal bearing (in degrees)"""
        self._bearing = value

    @property
    def number(self) -> float:
        """Get the DF hit ratio percentage"""
        return self._number

    @number.setter
    def number(self, value: float):
        """Set the DF hit ratio percentage"""
        # TODO - Ensure this is a multiple of 12.5%
        self._number = value

    @property
    def df_range(self) -> int:
        """Get the DF range (in miles)"""
        return self._df_range

    @df_range.setter
    def df_range(self, value: int):
        """Set the DF range (in miles)"""
        self._df_range = value

    @property
    def quality(self) -> int:
        """Get the DF bearing accuracy (in degrees)"""
        return self._quality

    @quality.setter
    def quality(self, value: int):
        """Set the DF bearing accuracy (in degrees)"""
        # TODO - Ensure that this is valid
        self._quality = value

    @property
    def messaging(self) -> bool:
        """Get whether this station is message-capable or not"""
        return self._messaging

    @messaging.setter
    def messaging(self, value: bool):
        """Set whether this station is using message-capable or not"""
        if type(value) is not bool:
            raise TypeError("Value must be of type 'bool' ('{}' given)".format(type(value)))

        self._messaging = value

    @property
    def compressed(self) -> bool:
        """Get whether this packet is using compressed positions or not"""
        return self._compressed

    @compressed.setter
    def compressed(self, value: bool):
        """Set whether this packet is using compressed positions or not"""
        if type(value) is not bool:
            raise TypeError("Value must be of type 'bool' ('{}' given)".format(type(value)))

        self._compressed = value

    @property
    def compression_fix(self) -> CompressionFix:
        """Get the compression fix type."""
        return self._compression_fix

    @compression_fix.setter
    def compression_fix(self, value: Union[CompressionFix, None]):
        """Set the compression fix type."""
        if value is None or type(value) is CompressionFix:
            self._compression_fix = value
        else:
            raise TypeError("Compression fix must be of type 'CompressionFix' ('{}' given)".format(
                type(value)
            ))

    @property
    def compression_source(self) -> CompressionSource:
        """Get the compression source type."""
        return self._compression_source

    @compression_source.setter
    def compression_source(self, value: Union[CompressionSource, None]):
        """Set the compression source type."""
        if value is None or type(value) is CompressionSource:
            self._compression_source = value
        else:
            raise TypeError(
                "Compression source must be of type 'CompressionSource' ('{}' given)".format(
                    type(value)
                )
            )

    @property
    def compression_origin(self) -> CompressionOrigin:
        """Get the compression origin type."""
        return self._compression_origin

    @compression_origin.setter
    def compression_origin(self, value: Union[CompressionOrigin, None]):
        """Set the compression origin type."""
        if value is None or type(value) is CompressionOrigin:
            self._compression_origin = value
        else:
            raise TypeError(
                "Compression origin must be of type 'CompressionOrigin' ('{}' given)".format(
                    type(value)
                )
            )

    @staticmethod
    def _parse_uncompressed_position(data: str) -> Tuple[float, float, int, str, str]:
        """
        Parse uncompressed position data from a packet.

        :param str data: the information field of a packet, minus the initial data type identifier

        Given the information field of a packet with the initial data type identifier stripped, this
        will parse the latitude, longitude, position ambiguity, symbol table and symbol ID, and
        return them in a tuple.
        """
        # Decode the latitude and ambiguity
        try:
            lat, ambiguity = APRSUtils.decode_uncompressed_latitude(data[0:8])

        except ValueError as e:
            raise ParseError("Invalid latitude: {}".format(e))

        # Decode the longitude
        try:
            lng = APRSUtils.decode_uncompressed_longitude(data[9:18])

        except ValueError as e:
            raise ParseError("Invalid longitude: {}".format(e))

        logger.debug("Latitude: {} ({}) Longitude: {}".format(
            lat, ambiguity, lng
        ))

        # Parse the symbol table
        symbol_table = data[8]
        logger.debug("Symbol table: {}".format(symbol_table))

        try:
            # Parse the symbol ID
            symbol_id = data[18]
            logger.debug("Symbol: {}".format(symbol_id))
        except IndexError:
            raise ParseError("Missing symbol identifier")

        return (lat, lng, ambiguity, symbol_table, symbol_id)

    @staticmethod
    def _parse_compressed_byte(compression_byte: str) -> Tuple[CompressionFix, CompressionSource,
                                                               CompressionOrigin]:
        """
        Parse the compression byte.

        :param str compression_byte: the compression byte

        This will return a tuple of Enums denoting the compression fix, source and origin.

        For more information, see APRS 1.01 C9 P39.
        """

        t = ord(compression_byte) - 33

        # Determine the fix type
        for fix in iter(CompressionFix):
            if t | fix.value:
                break
        else:
            raise ParseError("Could not determine the compression fix type ({})".format(bin(t)))

        # Determine the source type
        for source in iter(CompressionSource):
            if t | source.value:
                break
        else:
            raise ParseError("Could not determine the compression source type ({})".format(bin(t)))

        # Determine the origin type
        for origin in iter(CompressionOrigin):
            if t | origin.value:
                break
        else:
            raise ParseError("Could not determine the compression origintype ({})".format(bin(t)))

        return [fix, source, origin]

    @classmethod
    def _parse_compressed_position(cls, data: str) -> Tuple[
        float, float, Optional[float], Optional[float], Optional[float], Optional[float],
        Optional[CompressionFix], Optional[CompressionSource], Optional[CompressionOrigin]
    ]:
        """
        Parse compressed position data from a packet.

        :param str data: the information field of a packet, minus the initial data type identifier

        Given the information field of a packet with the initial data type identifier stripped, this
        will parse the latitude and longitude, and optionally the altitude, course, speed and radio
        range.
        """

        if len(data) < 13:
            raise ValueError("Compressed position data must be at least 13 character")

        logger.debug("Compressed lat/lng is: {}".format(data))

        # Parse the compressed latitude and longitude character from the packet
        comp_lat = data[1:5]
        comp_lng = data[5:9]

        # Decode the latitude and longitude
        latitude = APRSUtils.decode_compressed_latitude(comp_lat)
        longitude = APRSUtils.decode_compressed_longitude(comp_lng)

        logger.debug("Latitude: {} Longitude: {}".format(latitude, longitude))

        # Decode the compression type, which determines what other data the packet provides.
        comp_type = "{:0>8b}".format(ord(data[12])-33)[::-1]

        altitude = None
        course = None
        speed = None
        radio_range = None

        # Check for altitude, course/speed or radio range
        if data[10] == " ":
            # If the 11th character is blank, then don't do any further parsing

            fix = None
            source = None
            origin = None

            logger.debug("No course, speed or range data")

        elif comp_type[3] == "0" and comp_type[4] == "1":
            # The altitude is obtained by subtracting 33 from the ASCII value for the c and s
            # characters, multiplying c by 91, adding s, and then raising 1.002 to the power of the
            # result.
            # See APRS 1.01 C9 P40
            c = ord(data[10]) - 33
            s = ord(data[11]) - 33
            altitude = round((1.002 ** (c * 91 + s)), 2)

            fix, source, origin = cls._parse_compressed_byte(data[12])

            logger.debug("Altitude: {}".format(altitude))

        elif 0 <= (ord(data[10])-33) <= 89:
            # The course is obtained by subtracting 33 from the ASCII value of c and then
            # multiplying it by 4
            c = ord(data[10]) - 33
            course = c * 4

            # The speed is obtained by subtracting 33 from the ASCII value of s and then raising
            # 1.08 to the power of the result, and finally subtracting 1.
            # We round the result to 1 decimal place.
            s = ord(data[11]) - 33
            speed = round((1.08 ** s) - 1, 1)

            fix, source, origin = cls._parse_compressed_byte(data[12])

            logger.debug("Course: {} Speed: {}".format(course, speed))

        elif data[10] == "{":
            # The radio range is obtained by subtracting 33 from the ASCII value of s, raising 1.08
            # to the power of the result, and finally multiplying it by 2.
            s = ord(data[11]) - 33
            radio_range = round(2 * (1.08 ** s), 2)

            fix, source, origin = cls._parse_compressed_byte(data[12])

            logger.debug("Radio range: {}".format(radio_range))
        else:
            raise ValueError("Invalid character when looking for course/speed or range: {}".format(
                data[10]
            ))

        return (latitude, longitude, altitude, course, speed, radio_range, fix, source, origin)

    @staticmethod
    def _generate_uncompressed_position(latitude: float, longitude: float, symbol_table: str,
                                        symbol_id: str, ambiguity: int = 0) -> str:
        """
        Generate uncompressed position data for a packet.

        :param float latitude: the position's latitude
        :param float longitude: the position's longitude
        :param int ambiguity: the level of ambiguity for the position
        :param str symbol_table: the symbol table reference
        :param str symbol_id: the symbol ID

        Given the latitude, longitude, symbol table, symbol ID and an optional ambiguity value, this
        will return an information field containing these values in an uncompressed format.
        """
        # Encode the latitude
        lat = APRSUtils.encode_uncompressed_latitude(latitude, ambiguity)

        # Encode the longitude
        lng = APRSUtils.encode_uncompressed_longitude(longitude, ambiguity)

        logger.debug("Latitude: {} ({}) Longitude: {}".format(
            lat, ambiguity, lng
        ))

        # Parse the symbol table
        logger.debug("Symbol table: {}".format(symbol_table))
        logger.debug("Symbol ID: {}".format(symbol_id))

        info = f"{lat}{symbol_table}{lng}{symbol_id}"

        return info

    @staticmethod
    def _generate_compressed_byte(fix: CompressionFix, source: CompressionSource,
                                  origin: CompressionOrigin) -> str:
        """
        Generate the compression byte based on the fix, source and origin values.

        :param CompressionFix fix: the fix status
        :param CompressionSource source: the NMEA source
        :param CompressionOrigin origin: the compression origin

        For more information, see APRS 1.01 C9 P39.
        """

        # Generate the byte by ORing the values
        t = fix.value | source.value | origin.value

        # Add 33, convert to an ASCII character
        compression_byte = chr(t + 33)

        return compression_byte

    @classmethod
    def _generate_compressed_position(cls, latitude: float, longitude: float, symbol_table: str,
                                      symbol_id: str, altitude: int = None, course: int = None,
                                      speed: int = None, radio_range: int = None,
                                      fix: CompressionFix = CompressionFix.OLD,
                                      source: CompressionSource = CompressionSource.OTHER,
                                      origin: CompressionOrigin = CompressionOrigin.SOFTWARE
                                      ) -> str:
        """
        Generate compressed position data for a packet.

        :param float latitude: the position's latitude
        :param float longitude: the position's longitude
        :param str symbol_table: the symbol table reference
        :param str symbol_id: the symbol ID
        :param int altitude: the altitude, in feet
        :param int course: the course, in degrees
        :param int speed: the speed, in knots
        :param int radio_range: the radio range, in miles
        :param str fix: the GPS fix type
        :param str source: the NMEA source
        :param str origin: the compression origin

        Given the latitude, longitude, symbol table, symbol ID, this will return an information
        field containing these values in an uncompressed format.

        Additional (mutually exclusive) optional values can also be added:-
        * course and speed
        * altitude
        * radio range

        The `fix`, `source` and `origin` values are used to generate the 'Compression byte' (see
        APRS 1.01 C9 P39). See :class:`CompressionFix`, :class:`CompressionSource` and
        :class:`CompressionOrigin`.

        If altitude is specified, then `source` will be overridden.
        """

        lat = APRSUtils.encode_compressed_latitude(latitude)
        lng = APRSUtils.encode_compressed_longitude(longitude)

        if course is not None and speed is not None:
            c = chr((course // 4) + 33)
            s = chr(round(math.log((speed + 1), 1.08)) + 33)
            t = cls._generate_compressed_byte(fix, source, origin)

        elif altitude is not None and altitude >= 1.0:
            # First get the exponent
            exp = round(math.log(altitude, 1.002))

            # The exponent is converted back into two numbers that fit the following equation:-
            # a * 91 + b = exp
            # Values must translate (after having 33 added to them) to a printable ASCII character.
            # This means we're limited to between 0 and 93 (33 and 126).
            a = None
            for b in range(0, 94):
                if (exp - b) % 91 == 0 and (exp - b) // 91 < 94:
                    a = (exp - b) // 91
                    break
            else:
                raise GenerateError("Could not encode altitude ({}ft)".format(altitude))

            c = chr(a + 33)
            s = chr(b + 33)

            source = CompressionSource.GGA
            t = cls._generate_compressed_byte(fix, source, origin)

        elif radio_range is not None:
            # The first character is always {
            c = "{"

            # The range is encoded as the exponent of the following:-
            # 2 * (1.08 ** exp)
            exp = round(math.log((radio_range/2), 1.08))
            s = chr(exp + 33)

            t = cls._generate_compressed_byte(fix, source, origin)

        else:
            c = " "
            s = "s"
            t = "T"

        return f"{symbol_table}{lat}{lng}{symbol_id}{c}{s}{t}"

    @staticmethod
    def _parse_data(data: str) -> Tuple[str, str, str, int, int, int, str]:
        """
        Parse additional information from the information field.

        :param str data: the information field of a packet, minus the initial data type identifier

        Position packets can have additional information in them, such as station power, antenna
        height, antenna gain, etc. These are described in APRS 1.01 C7. This will parse out the raw
        values, but not decode them.
        """

        phg = None
        rng = None
        dfs = None
        course = None
        speed = None
        altitude = None
        comment = None

        if re.match(r'^PHG[0-9]{4}', data[:7]):
            # Packet has a PHG (power, antenna height/gain/directivity) value
            phg = data[3:7]
            logger.debug("PHG is {}".format(phg))
            data = data[7:]

        elif re.match('^RNG[0-9]{4}', data[:7]):
            # Packet has an RNG (radio range) value
            rng = data[3:7]
            logger.debug("RNG is {}".format(rng))
            data = data[7:]

        elif re.match('^DFS[0-9]{4}', data[:7]):
            # Packet has a DFS (DF signal strength, antenna height/gain/directivity) value
            dfs = data[3:7]
            logger.debug("DFS is {}".format(dfs))
            data = data[7:]

        elif re.match('^[0-9]{3}/[0-9]{3}', data[:7]):
            # Packet has course and speed values
            course = int(data[:3])
            speed = int(data[4:7])
            logger.debug("Course is {}, speed is {}".format(course, speed))
            data = data[7:]

        # TODO - parse BRG/NRQ

        # Check for comment
        if len(data) > 0:

            # Check for altitude
            # As per APRS 1.01 C6 P26, altitude as /A=nnnnnn may appear anywhere in the comment
            has_altitude = re.match('.*/A=([0-9]{6}).*', data)
            if has_altitude:
                # TODO - fix altitude format
                altitude = int(has_altitude.groups()[0])
                logger.debug("Altitude is {} ft".format(altitude))

                # Strip out the altitude from the comment
                data = re.sub(r'/A=[0-9]{6}', "", data)

            # Set the comment as the remainder of the information field
            comment = data
            logger.debug("Comment is {}".format(comment))

        return (phg, rng, dfs, course, speed, altitude, comment)

    @staticmethod
    def _generate_data(phg: str = None, rng: str = None, dfs: str = None, course: int = None,
                       speed: int = None, altitude: int = None, comment: str = None) -> str:
        """
        Generate additional information for the information field.

        :param str phg: a PHG value
        :param str rng: an RNG value
        :param str dfs: a DFS value
        :param int course: course, in degrees
        :param int speed: speed, in knots
        :param int altitude: altitude, in feet
        :param str comment: a comment

        Position packets can have additional information in them, such as station power, antenna
        height, antenna gain, etc. These are described in APRS 1.01 C7. This will generate an
        information field based on these values.

        Note that PHG, RNG, DFS and course/speed are mutually exclusive. Altitude is specified as
        part of the comment and so can coexist with any of the other values.
        """

        data = ""
        if phg:
            data += phg
        elif rng:
            data += rng
        elif dfs:
            data += dfs
        elif course and speed:
            data += "{}/{}".format(
                str(course).zfill(3), str(speed).zfill(3)
            )

        if altitude:
            data += "/A={}".format(
                str(altitude).zfill(6)
            )

        if comment:
            data += comment

        return data

    def _parse(self) -> bool:
        """
        Parse a position packet.

        There are a number of different position packet types - with or without a timestamp, and
        with or without messaging capability. The data type ID is used to distinguish between them.

        The position data itself can either be compressed or uncompressed, regardless of the data
        type ID.

        The parsed and decoded values are stored in the current object.
        """

        # First, check if this packet has a '!' at an offset position
        # This is allowed as per APRS 1.01 C5 P18
        if hasattr(self, '_offset'):
            # Packets with the '!' offset do not have a timestamp or messaging capabilities
            # Chop everything off the info field before the '!'
            self._info = self._info[self._offset:]

        elif self.data_type_id == '!':
            # Packet has no timestamp, station has no messaging capability
            self.timestamp = None
            self.messaging = False

        elif self.data_type_id == '/':
            # Packet has timestamp, station has no messaging capability
            self.messaging = False

            # Parse timestamp
            (self.timestamp, self.timestamp_type) = APRSUtils.decode_timestamp(self._info[0:8])

        elif self.data_type_id == '=':
            # Packet has no timestamp, station has messaging capability
            self.timestamp = None
            self.messaging = True

        elif self.data_type_id == '@':
            # Packet has timestamp, station has messaging capability
            self.messaging = True

            # Parse timestamp
            (self.timestamp, self.timestamp_type) = APRSUtils.decode_timestamp(self._info[0:8])

        else:
            # This isn't a position packet
            raise ParseError("Unknown position data type: {}".format(self.data_type_id))

        if self.timestamp is None:
            data = self._info
        else:
            data = self._info[7:]

        # Check to see if the position data is compressed or uncompressed
        if re.match(r'[0-9\s]{4}\.[0-9\s]{2}[NS].[0-9\s]{5}\.[0-9\s]{2}[EW]', data):
            # Parse the uncompressed position values from the information field
            (self.latitude, self.longitude, self.ambiguity, self.symbol_table, self.symbol_id
             ) = self._parse_uncompressed_position(data)

            # Ensure compressed is set to False
            self.compressed = False

            if len(data) > 19:
                # This packet has additional data in the information field, so attempt to parse it
                (phg, radio_range, dfs, self.course, self.speed, self.altitude,
                 comment) = self._parse_data(data[19:])

                if self.symbol_table == "/" and self.symbol_id == "\\":
                    # If the symbol table is /, and the symbol ID is \, it implies a DF report
                    # 26th and 30th characters should be /
                    logger.debug("Symbol table and symbol indicates a DF report")

                    if len(comment) < 8:
                        # Packets with DF information must be at least 8 characters long
                        raise ParseError("Missing DF values")

                    if comment[0] != "/" or comment[4] != "/":
                        # Packets with DF information must also include the bearing and NRQ values
                        # See APRS 1.01 C7 P30
                        raise ParseError(
                            "Invalid DF values (character in position 0 and 4 should be '/'"
                        )

                    # Extract the bearing
                    self.bearing = int(comment[1:4])
                    logger.debug(f"DF bearing is {self.bearing} degrees")

                    # Decode the NRQ value
                    (self.number, self.df_range, self.quality) = APRSUtils.decode_nrq(comment[5:8])

                    # Strip the bearing/NRQ value from the comment
                    self.comment = comment[8:]

                elif self.symbol_table in ["/", "\\"] and self.symbol_id == "_":
                    # / or \, and _ for the symbol table and symbol implies a weather report
                    # TODO - Implementation
                    logger.debug("Symbol table and symbol indicates a weather report")

                elif phg:
                    # Decode the power, height, gain and directivity values
                    (self.power, self.height, self.gain, self.directivity) = \
                        APRSUtils.decode_phg(phg)

                    # The PHG value has already been stripped from the comment
                    self.comment = comment

                elif radio_range:
                    # The radio range is specified as 4 digits, which denote the range in miles
                    self.radio_range = int(radio_range)
                    logger.debug(f"Radio range is {radio_range} miles")

                    # The PHG value has already been stripped from the comment
                    self.comment = comment

                elif dfs:
                    # Decode the signal strength, height, gain and directivity values
                    (self.strength, self.height, self.gain, self.directivity) = \
                        APRSUtils.decode_dfs(dfs)

                    # The PHG value has already been stripped from the comment
                    self.comment = comment

                else:
                    # No additional data found
                    self.comment = comment

        else:
            # Parse the compressed position values from the information field

            # Get the compressed position
            compressed_position = data[0:13]

            try:
                (self.latitude, self.longitude, self.altitude, self.course, self.speed,
                self.radio_range, self.compression_fix, self.compression_source,
                self.compression_origin) = self._parse_compressed_position(compressed_position)

            except Exception as e:
                # TODO Catch specific errors (for example, OverflowError)
                raise ParseError("Couldn't parse compressed position: {}".format(e))

            # Ensure compressed is set to True
            self.compressed = True

            # Parse the symbol table and symbol ID
            self.symbol_table = data[0]
            self.symbol_id = data[9]

            # TODO - parse altitude information

            self.comment = data[13:]
            logger.debug("Comment is {}".format(self.comment))

        # If we get this far, then we've parsed the packet
        return True

    @property
    def info(self) -> str:
        """Generate the information field for a position packet."""
        info = ""

        # Ensure we have a latitude and a longitude
        if self.latitude is None:
            raise GenerateError("Missing latitude")
        elif self.longitude is None:
            raise GenerateError("Missing longitude")

        # Ensure we have a symbol table and symbol ID
        if self.symbol_table is None:
            raise GenerateError("Missing symbol table")
        elif self.symbol_id is None:
            raise GenerateError("Missing symbol ID")

        # Set data type ID
        if self.timestamp is None:
            if self.messaging is False:
                self.data_type_id = "!"
            else:
                self.data_type_id = "="
        else:
            if self.messaging is False:
                self.data_type_id = "/"
            else:
                self.data_type_id = "@"

            # Set the timestamp
            info += APRSUtils.encode_timestamp(self.timestamp, self.timestamp_type)

        if self.compressed:
            # Add the position in a compressed format
            info += self._generate_compressed_position(
                self.latitude, self.longitude, self.symbol_table, self.symbol_id, self.altitude,
                self.course, self.speed, self.radio_range, self.compression_fix,
                self.compression_source, self.compression_origin)

            # PHG, etc is not supported for compressed formats (see APRS 1.01 C9 P36)
            if self.comment:
                info += self.comment

        else:
            # Add the position in an uncompressed format
            # TODO: handle BRG/NRQ
            info += self._generate_uncompressed_position(
                self.latitude, self.longitude, self.symbol_table, self.symbol_id, self.ambiguity
            )

            # Handle PHG
            if self.power is not None and self.height is not None and self.gain is not None \
                    and self.directivity is not None:
                phg = APRSUtils.encode_phg(self.power, self.height, self.gain, self.directivity)
                info += "PHG{}".format(
                    self._generate_data(phg=phg, altitude=self.altitude, comment=self.comment)
                )

            # Handle DFS
            elif self.strength is not None and self.height is not None and self.gain is not None \
                    and self.directivity is not None:
                dfs = APRSUtils.encode_dfs(self.strength, self.height, self.gain, self.directivity)
                info += "DFS{}".format(
                    self._generate_data(dfs=dfs, altitude=self.altitude, comment=self.comment)
                )

            # Handle course/speed
            elif self.course is not None and self.speed is not None:
                info += "{}/{}".format(
                    str(self.course).zfill(3),
                    str(self.speed).zfill(3)
                )
                info += self._generate_data(altitude=self.altitude, comment=self.comment)

            # Handle RNG
            elif self.radio_range is not None:
                info += "RNG{}".format(
                    str(self.radio_range).zfill(4)
                )
                info += self._generate_data(altitude=self.altitude, comment=self.comment)

            else:
                info += self._generate_data(altitude=self.altitude, comment=self.comment)

        return info

    def __repr__(self):
        if self.source:
            return "<PositionPacket: {}>".format(self.source)
        else:
            return "<PositionPacket>"
