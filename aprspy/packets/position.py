#!/usr/bin/env python

import re
import logging

from geopy.point import Point

from typing import Tuple, Optional

from ..exceptions import ParseError, GenerateError
from ..utils import APRSUtils
from .generic import GenericPacket

# Set up logging
logger = logging.getLogger(__name__)


class PositionPacket(GenericPacket):
    """
    Class to represent various kinds of position packets.

    This class represents packets which provide position information - including weather reports.
    """

    def __init__(self, latitude: float = 0.0, longitude: float = 0.0, ambiguity: int = 0,
                 course: int = None, speed: float = None, comment: str = None, power: int = None,
                 height: int = None, gain: int = None, directivity: int = None,
                 radio_range: int = None, strength: int = None, bearing: int = None,
                 number: float = None, df_range: int = None, quality: int = None,
                 compressed: bool = False, messaging: bool = False, data_type_id: str = "!",
                 *args, **kwargs):

        super().__init__(*args, **kwargs, data_type_id=data_type_id)
        self._point = Point()
        self.latitude = latitude
        self.longitude = longitude
        self.ambiguity = ambiguity
        self.course = course
        self.speed = speed
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

        # Compressed
        self.compressed = compressed

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
        lat, ambiguity = APRSUtils.decode_uncompressed_latitude(data[0:8])

        # Decode the longitude
        lng = APRSUtils.decode_uncompressed_longitude(data[9:18])

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
    def _parse_compressed_position(data: str) -> Tuple[
            float, float, Optional[float], Optional[float], Optional[float], Optional[float]]:
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
            logger.debug("No course, speed or range data")

        elif comp_type[3] == "0" and comp_type[4] == "1":
            # The altitude is obtained by subtracting 33 from the ASCII value for the c and s
            # characters, multiplying c by 91, adding s, and then raising 1.002 to the power of the
            # result.
            # See APRS 1.01 C9 P40
            c = ord(data[10]) - 33
            s = ord(data[11]) - 33
            altitude = round((1.002 ** (c * 91 + s)), 2)

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

            logger.debug("Course: {} Speed: {}".format(course, speed))

        elif data[10] == "{":
            # The radio range is obtained by subtracting 33 from the ASCII value of s, raising 1.08
            # to the power of the result, and finally multiplying it by 2.
            s = ord(data[11]) - 33
            radio_range = round(2 * (1.08 ** s), 2)

            logger.debug("Radio range: {}".format(radio_range))

        else:
            raise ValueError("Invalid character when looking for course/speed or range: {}".format(
                data[10]
            ))

        return (latitude, longitude, altitude, course, speed, radio_range)

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

        if self.data_type_id == '!':
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
                        raise ParseError("Missing DF values", self)

                    if comment[0] != "/" or comment[4] != "/":
                        # Packets with DF information must also include the bearing and NRQ values
                        # See APRS 1.01 C7 P30
                        raise ParseError("Invalid DF values", self)

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
            compressed_position = data[0:13]
            (self.latitude, self.longitude, self.altitude, self.course, self.speed,
             self.radio_range) = self._parse_compressed_position(compressed_position)

            # Ensure compressed is set to True
            self.compressed = True

            # Parse the symbol table and symbol ID
            self.symbol_table = data[0]
            self.symbol_id = data[9]

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
            # Compressed positions are currently unsupported
            # TODO: implement compressed position generation
            raise GenerateError("Compressed positions are currently unsupported")
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
                info += self._generate_data(phg=phg, altitude=self.altitude, comment=self.comment)

            # Handle DFS
            elif self.strength is not None and self.height is not None and self.gain is not None \
                    and self.directivity is not None:
                dfs = APRSUtils.encode_dfs(self.strength, self.height, self.gain, self.directivity)
                info += self._generate_data(dfs=dfs, altitude=self.altitude, comment=self.comment)

            # Handle course/speed
            elif self.course is not None and self.speed is not None:
                info += "{}/{}".format(
                    str(self.course).zfill(3),
                    str(self.speed).zfill(3)
                )
                info += self._generate_data(altitude=self.altitude, comment=self.comment)

            # Handle RNG
            elif self.radio_range is not None:
                info += "DFS{}".format(
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
