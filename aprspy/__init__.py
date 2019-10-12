#!/usr/bin/env python

import re
import logging
import math

from hashlib import md5
from datetime import datetime, timedelta
from geopy.point import Point

from typing import Union, List, Tuple, Optional

from .exceptions import ParseError, UnsupportedError
from .components import Path, Station

__version__ = "0.1.3"

# Set up logging
logger = logging.getLogger(__name__)


class APRSPacket:
    """
    Generic base class for APRS packets.

    This is the base class for representing an APRS packet. Anything that is common to all packets
    is defined in here.
    """

    def __init__(self, source: str = None, destination: str = None, path: str = None,
                 info: str = None):
        # list to hold the path hops
        self._path_hops = []
        self._source = None
        self._destination = None
        self._path = None
        self._info = None

        # Set source, destination, path and info (if given)
        self.source = source
        self.destination = destination
        self.path = path
        self.info = info

        self.checksum = None

    @property
    def source(self) -> Station:
        """Get the source address of the packet"""
        return self._source

    @source.setter
    def source(self, value: Union[str, Station]):
        """Set the source address of the packet"""
        if type(value) is str:
            # Passed a str
            if len(value) <= 9:
                self._source = value
            else:
                raise ValueError("Source must be a maximum of 9 characters")
        elif type(value) is Station:
            # Passed a Station
            self._source = value
        elif value is None:
            # Passed None
            self._source = None
        else:
            raise TypeError("Source must either be 'str' or 'Station' ({} given)".format(
                type(value)
            ))

    @property
    def destination(self) -> Station:
        """Get the destination address of the packet"""
        return self._destination

    @destination.setter
    def destination(self, value: Union[str, Station]):
        """Set the destination address of the packet"""
        if type(value) is str:
            # Passed a str
            if len(value) <= 9:
                self._destination = value
            else:
                raise ValueError("Destination must be a maximum of 9 character")
        elif type(value) is Station:
            # Passed a Station
            self._destination = value
        elif value is None:
            # Passed None
            self._destination = None
        else:
            raise TypeError("Destination must be of type 'str' and a maximum of 9 characters")

    @property
    def path(self) -> Path:
        """Get the path of the packet"""
        return self._path

    @path.setter
    def path(self, value: Union[str, Path]):
        """Set the path for the packet"""
        if type(value) is str:
            self._path = Path(path=value)
        elif type(value) is Path:
            self._path = value
        elif value is None:
            self._path = None
        else:
            raise TypeError("Path must be of type 'str' or 'Path' ({} given)".format(type(value)))

    @property
    def info(self) -> str:
        """Get the information field of the packet"""
        return self._info

    @info.setter
    def info(self, value: str):
        """Set the information field of the packet"""
        self._info = value

    @property
    def timestamp(self) -> str:
        """Get the timestamp of the packet"""
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value: str):
        """Set the timestamp of the packet"""
        self._timestamp = value

    @property
    def data_type_id(self) -> str:
        """Get the data type ID of the packet"""
        return self._data_type_id

    @data_type_id.setter
    def data_type_id(self, value: str):
        """Set the data type ID of the packet"""
        self._data_type_id = value

    @property
    def symbol_table(self) -> str:
        """Get the symbol table of the packet"""
        return self._symbol_table

    @symbol_table.setter
    def symbol_table(self, value: str):
        """Set the symbol table of the packet"""
        self._symbol_table = value

    @property
    def symbol_id(self) -> str:
        """Get the symbol ID of the packet"""
        return self._symbol

    @symbol_id.setter
    def symbol_id(self, value: str):
        """Set the symbol ID of the packet"""
        self._symbol = value

    def __repr__(self):
        if self.source:
            return "<APRSPacket: {}>".format(self.source)
        else:
            return "<APRSPacket>"


class PositionPacket(APRSPacket):
    """
    Class to represent various kinds of position packets.

    This class represents packets which provide position information - including weather reports.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._point = Point()
        self._ambiguity = None
        self._course = None
        self._speed = None
        self._comment = None

        # PHG/RNG/DFS/BRG/NRQ
        self._power = None
        self._height = None
        self._gain = None
        self._directivity = None
        self._radio_range = None
        self._strength = None
        self._bearing = None
        self._number = None
        self._df_range = None
        self._quality = None

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
    def speed(self) -> int:
        """Get the speed of the station"""
        return self._speed

    @speed.setter
    def speed(self, value: int):
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
        lat, ambiguity = APRS.decode_uncompressed_latitude(data[0:8])

        # Decode the longitude
        lng = APRS.decode_uncompressed_longitude(data[9:18])

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
        latitude = APRS.decode_compressed_latitude(comp_lat)
        longitude = APRS.decode_compressed_longitude(comp_lng)

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

        # Check for comment
        if len(data) > 0:

            # Check for altitude
            # As per APRS 1.01 C6 P26, altitude as /A=nnnnnn may appear anywhere in the comment
            has_altitude = re.match('.*/A=([0-9]{6}).*', data)
            if has_altitude:
                # TODO - fix altitude format
                altitude = int(has_altitude.groups()[0])
                logger.debug("Altitude is {} ft".format(altitude))

            # Set the comment as the remainder of the information field
            comment = data
            logger.debug("Comment is {}".format(comment))

        return (phg, rng, dfs, course, speed, altitude, comment)

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
            self.timestamp = APRS.decode_timestamp(self.info[1:8])

        elif self.data_type_id == '=':
            # Packet has no timestamp, station has messaging capability
            self.timestamp = None
            self.messaging = True

        elif self.data_type_id == '@':
            # Packet has timestamp, station has messaging capability
            self.messaging = True

            # Parse timestamp
            self.timestamp = APRS.decode_timestamp(self.info[1:8])

        else:
            # This isn't a position packet
            raise ParseError("Unknown position data type: {}".format(self.data_type_id))

        if self.timestamp is None:
            data = self.info[1:]
        else:
            data = self.info[8:]

        # Check to see if the position data is compressed or uncompressed
        if re.match(r'[0-9\s]{4}\.[0-9\s]{2}[NS].[0-9\s]{5}\.[0-9\s]{2}[EW]', data):
            # Parse the uncompressed position values from the information field
            (self.latitude, self.longitude, self.ambiguity, self.symbol_table, self.symbol_id
             ) = self._parse_uncompressed_position(data)

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
                    (self.number, self.df_range, self.quality) = APRS.decode_nrq(comment[5:8])

                    # Strip the bearing/NRQ value from the comment
                    self.comment = comment[8:]

                elif self.symbol_table in ["/", "\\"] and self.symbol_id == "_":
                    # / or \, and _ for the symbol table and symbol implies a weather report
                    # TODO - Implementation
                    logger.debug("Symbol table and symbol indicates a weather report")

                elif phg:
                    # Decode the power, height, gain and directivity values
                    (self.power, self.height, self.gain, self.directivity) = APRS.decode_phg(phg)

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
                    (self.strength, self.height, self.gain, self.directivity) = APRS.decode_dfs(dfs)

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

            # Parse the symbol table and symbol ID
            self.symbol_table = data[0]
            self.symbol_id = data[9]

            self.comment = data[13:]
            logger.debug("Comment is {}".format(self.comment))

        # If we get this far, then we've parsed the packet
        return True

    def __repr__(self):
        if self.source:
            return "<PositionPacket: {}>".format(self.source)
        else:
            return "<PositionPacket>"


class MICEPacket(PositionPacket):
    """
    Class to represent Mic-E encoded position packets.

    Mic-E packets encode position data in both the APRS destination and information fields, enabling
    a large amount of information to be conveyed in a single packet.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def _decode_latitude(destination: str) -> Tuple[float, int, bool, str, int, int, int, bool]:
        """
        Decode the latitude.

        :param str destination: the destination field of a packet

        Mic-E packets encode the latitude in the destination field, along with the north/south,
        east/west, longitude offset and message identifier. In addition, the SSID can be used to
        denote a generic APRS digipeater path.

        For more information, seeee APRS 1.01 C10 P43.
        """

        latitude = ""
        north_south = ""
        east_west = ""
        # TODO - handle status types
        message_a = ""
        message_b = ""
        message_c = ""
        message_custom = False
        lng_offset = False

        # Iterate over each character of the destination address
        count = 0
        for i in destination[0:6]:
            count += 1
            if 48 <= ord(i) <= 57:
                # 0-9 are used as-is
                latitude += i
                enc_set = 1
            elif 65 <= ord(i) <= 74:
                latitude += str((ord(i) - 65))
                enc_set = 2
            elif 80 <= ord(i) <= 89:
                latitude += str((ord(i) - 80))
                enc_set = 3
            elif i in "KLZ":
                latitude += " "
                if i == "K":
                    enc_set = 2
                elif i == "L":
                    enc_set = 1
                elif i == "Z":
                    enc_set = 3
            else:
                raise ParseError("Unexpected character in Mic-E destination field")

            if count == 1:
                # The first field is changed depending on the message a-bit
                if enc_set == 1:
                    message_a = 0
                elif enc_set == 2:
                    message_a = 1
                    message_custom = True
                elif enc_set == 3:
                    message_a = 1
            elif count == 2:
                # The second field is changed depending on the message b-bit
                if enc_set == 1:
                    message_b = 0
                elif enc_set == 2:
                    message_b = 1
                    message_custom = True
                elif enc_set == 3:
                    message_b = 1
            elif count == 3:
                # The third field is changed depending on the message c-bit
                if enc_set == 1:
                    message_c = 0
                elif enc_set == 2:
                    message_c = 1
                    message_custom = True
                elif enc_set == 3:
                    message_c = 1
            elif count == 4:
                # The fourth field is changed to denote north/south
                if enc_set == 1:
                    north_south = "S"
                else:
                    north_south = "N"

                # Append a . to the latitude here, too
                latitude += "."
            elif count == 5:
                # The fifth field is changed to denote the longitude offset
                if enc_set == 1:
                    lng_offset = False
                else:
                    lng_offset = True
            elif count == 6:
                # The sixth field is changed to denote east/west
                if enc_set == 1:
                    east_west = "E"
                else:
                    east_west = "W"

        # TODO
        if len(destination) > 6:
            logger.debug("Mic-E destination has SSID: {}".format(destination.split('-')[1]))

        # Now that we have an uncompressed latitude, we can decode it like a standard uncompressed
        # packet
        decoded_latitude, ambiguity = APRS.decode_uncompressed_latitude(
            "{}{}".format(latitude, north_south)
        )

        logger.debug(
            "After destination field decoding, latitude is {}{} ({} - {}), longitude offset is {}, "
            "direction is {}, msg a/b/c is {}/{}/{}, msg custom is {}".format(
                latitude, north_south, decoded_latitude, ambiguity, lng_offset, east_west,
                message_a, message_b, message_c, message_custom
            ))

        # Return the decoded latitude, ambiguity, longitude offset, east/west direction and message
        # bits
        return (decoded_latitude, ambiguity, lng_offset, east_west, message_a, message_b,
                message_c, message_custom)

    @staticmethod
    def _decode_longitude(info: str, lng_offset: bool, east_west: str) -> float:
        """
        Decode the longitude.

        :param str info: the information field of a packet, minus the initial data type identifier
        :param bool lng_offset: whether the longitude offset should be applied or not
        :param str east_west: a single character (``E`` or ``W``) denoting an east or west latitude

        The longitude is stored in the 3 characters of the info field immediately following the data
        type identifier. Combined with the east/west and longitude offset values from decoding the
        latitude, we can decode the longitude.

        See also APRS 1.01 C10 P47.
        """

        logger.debug("Info input: {}".format(info))
        # The degrees, minutes and hundreths of minutes are obtained by subtracting 28 from the
        # ASCII values of the 3 characters
        lng_deg = ord(info[1]) - 28
        lng_min = ord(info[2]) - 28
        lng_hmin = ord(info[3]) - 28

        # If the longitude offset is set, apply it to the degrees value
        if lng_offset:
            lng_deg += 100

        # Next, if the value is between 180 and 189, subtract 80. If it's between 190 and 199,
        # subtract 190.
        if 180 <= lng_deg <= 189:
            lng_deg -= 80
        elif 190 <= lng_deg <= 199:
            lng_deg -= 190

        # If the minutes value is more than 60, subtract 60
        if lng_min >= 60:
            logger.debug("> 60 subtracted from lng_min")
            lng_min -= 60

        # Now that we have an uncompressed longitude, we can decode it
        longitude = APRS.decode_uncompressed_longitude("{}{}.{}{}".format(
            str(lng_deg).zfill(3),
            str(lng_min).zfill(2),
            str(lng_hmin).zfill(2),
            east_west
        ))
        logger.debug(
            "Longitude is {} {} {} ({})".format(lng_deg, lng_min, lng_hmin, longitude)
        )

        return longitude

    @staticmethod
    def _decode_speed_and_course(info: str):
        """
        Decode the speed and course.

        :param str info: the information field of a packet, minus the initial data type identifier

        The 3 characters after the longitude characters define the speed and course of the station.

        See also APRS 1.01 C10 P49.
        """

        try:
            # For each of the 3 characters, subtract 28 from the ASCII value
            sp = ord(info[4]) - 28
            dc = ord(info[5]) - 28
            se = ord(info[6]) - 28
        except IndexError:
            raise ParseError("Couldn't parse speed/course in Mic-E packet")

        # The speed is in knots, and is obtained by multiplying sp by 10, and adding the quotient of
        # dc divided by 10
        speed = (sp * 10) + int(dc / 10)

        # The course is in degrees, and is obtained by multiplying the remainder of dc divided by 10
        # by 100, and then adding the value of se
        course = ((dc % 10) * 100) + se

        # If the speed value is greater than or equal to 800, subtract 800 from it
        if speed >= 800:
            speed -= 800

        # If the course value is greater than or equal to 400, subtract 400 from it
        if course >= 400:
            course -= 400

        logger.debug("Speed is {} knots, course is {} degrees".format(speed, course))

        return (speed, course)

    def _parse(self) -> bool:
        """
        Parse a Mic-E packet.

        The parsed and decoded values are stored in the current object.
        """

        # Decode the latitude, ambiguity, the longitude offset, the east/west direction and the
        # message bits
        (self.latitude, self.ambiguity, lng_offset, east_west, message_a, message_b, message_c,
         message_custom) = self._decode_latitude(self.destination)

        # Decode the longitude, using the longitude offset and east/west direction from the previous
        # step
        self.longitude = self._decode_longitude(self.info, lng_offset, east_west)

        # Decode the speed and course from the info field
        (self.speed, self.course) = self._decode_speed_and_course(self.info)

        # Parse the symbol table and symbol from the info field
        try:
            self.symbol_id = self.info[7]
            logger.debug("Symbol ID is {}".format(self.symbol_id))
        except IndexError:
            raise ParseError("Missing symbol ID", self)

        try:
            self.symbol_table = self.info[8]
            logger.debug("Symbol table is {}".format(self.symbol_table))
        except IndexError:
            raise ParseError("Missing symbol table", self)

        # Next comes either the status text or telemetry (C10 P54)
        # Telemetry is indicated by setting the first character of the status field to dec 44
        # (a ',') or the unprintable 29.
        if len(self.info) >= 10:
            if ord(self.info[9]) == 44 or ord(self.info[9]) == 29:
                logger.debug("Packet contains telemetry data")
                # TODO
            else:
                logger.debug("Packet contains status text")
                status_text = self.info[10:]

                # The status text can contain an altitude value (C10 P55)
                # It's indicated by the first 4 characters, with the 4th being a '}'
                if len(status_text) >= 4 and status_text[3] == "}":
                    logger.debug("Status text contains altitude data")

                    # Decode the altitude
                    altitude = (
                        (ord(status_text[0])-33) * 91**2 +
                        (ord(status_text[1])-33) * 91 +
                        (ord(status_text[2])-33)
                    ) - 10000

                    self.altitude = altitude
                    logger.debug("Altitude is {}m".format(altitude))

                    # The remainder is the comment
                    self.comment = status_text[4:]
                    logger.debug("Comment is {}".format(self.comment))

                else:
                    self.comment = status_text
        else:
            logger.debug("Packet contains no further information.")

        return True

    def __repr__(self):
        if self.source:
            return "<MICEPacket: {}>".format(self.source)
        else:
            return "<MICEPacket>"


class StatusPacket(APRSPacket):
    """
    Class to represent status report packets.

    As per APRS 1.01, status reports "announce(s) the station's current mission or any other single
    line status to everyone". The data type identifier for status reports is ">".

    See APRS 1.01 C16 P80
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._status_message = None
        self._maidenhead_locator = None

    @property
    def status_message(self) -> str:
        """Get the status message"""
        return self._status_message

    @status_message.setter
    def status_message(self, value: str):
        """Set the status message"""
        self._status_message = value

    @property
    def maidenhead_locator(self) -> str:
        """Get the Maidenhead locator (if set)"""
        return self._maidenhead_locator

    @maidenhead_locator.setter
    def maidenhead_locator(self, value: str):
        """Set the Maidenhead locator"""
        self._maidenhead_locator = value

    def _parse(self) -> bool:
        """
        Parse a status report packet.

        Status reports contain a status message and optionally a timestamp or Maidenhead locator
        (but not both), and/or a beam heading and ERP value.

        Parse and decoded values are stored in the current object.
        """

        # Maidenhead locators, if present, must be first, and can be 4 or 6 characters.
        # They must also include a symbol table and symbol code (P81).
        # Therefore, if the status report matches [A-Z]{2}[0-9]{2}([A-Z]{2})? and a valid symbol
        # table and id, then it's a Maidenhead locator.
        # Valid symbol table IDs: /, \, 0-9, A-Z (C20 P91)
        if len(self.info) >= 7:
            mh_4 = self.info[1:7]
            logger.debug("Considering as Maidenhead locator: {}".format(mh_4))
        else:
            mh_4 = None

        if len(self.info) >= 9:
            mh_6 = self.info[1:9]
            logger.debug("Considering as Maidenhead locator: {}".format(mh_6))
        else:
            mh_6 = None

        message = None

        if mh_6 is not None and re.match("[A-Z]{2}[0-9]{2}[A-Z]{2}[/\\\0-9A-Z].", mh_6):
            # Maidenhead locator (GGnngg)
            self.maidenhead_locator = mh_6[0:6]

            self.symbol_table = mh_6[6]
            self.symbol_id = mh_6[7]

            logger.debug("Status with Maidenhead locator {}, symbol {} {}".format(
                self.maidenhead_locator, self.symbol_table, self.symbol_id
            ))

            if len(self.info) != 9:
                # First character of the text must be " " (C16 P82)
                if self.info[9] != " ":
                    # TODO
                    raise ParseError("Status message is invalid", self)
                else:
                    self.status_message = self.info[10:]
                    logger.debug("Status message is {}".format(self.status_message))
            else:
                logger.debug("No status message")

        elif mh_4 is not None and re.match(r'[A-Z]{2}[0-9]{2}[/\\\0-9A-Z].', mh_4):
            # Maidenhead locator (GGnn)
            self.maidenhead_locator = mh_4[0:4]

            self.symbol_table = mh_4[4]
            self.symbol_id = mh_4[5]

            logger.debug("Status with Maidenhead locator {}, symbol {} {}".format(
                self.maidenhead_locator, self.symbol_table, self.symbol_id
            ))

            if len(self.info) != 7:

                # First character of the text must be " " (C16 P82)
                if self.info[7] != " ":
                    # TODO
                    raise ParseError("Status message is invalid", self)
                else:
                    self.status_message = self.info[8:]
                    logger.debug("Status message is {}".format(self.status_message))
            else:
                logger.debug("No status message")

        else:
            # Check for a timestamp
            if re.match("^[0-9]{6}z", self.info[1:]):
                self.timestamp = APRS.decode_timestamp(self.info[1:8])
                # Sanity check the timestamp type - status reports can only use zulu
                # or local, so if hms is used, throw an error.
                # if timestamp_type == 'h' and data_type_id == '>':
                #     logger.error("Timestamp type 'h' cannot be used for status reports")
                #     raise ParseError("Timestamp type 'h' cannot be used for status reports")
                self.status_message = self.info[8:]
                logger.debug("Status message timestamp is {}".format(self.timestamp))
                logger.debug("Status message is {}".format(self.status_message))
            else:
                self.status_message = self.info[1:]
                logger.debug("No timestamp found")
                logger.debug("Status message is {}".format(self.status_message))

        # Check for a beam heading and ERP
        # TODO - Parse and decode the beam and ERP values
        if self.status_message and re.match(r'[\^].{2}', self.status_message[-3:]):
            logger.debug("Status message heading and power: {}".format(self.status_message[-2:]))

        return True

    def __repr__(self):
        if self.source:
            return "<StatusPacket: {}>".format(self.source)
        else:
            return "<StatusPacket>"


class MessagePacket(APRSPacket):
    """
    Class to represent APRS message packets.

    APRS message packets can be from one station to another, or general bulletins or announcements
    which are intended for a wider audience.

    See also APRS 1.01 C14 P71
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._addressee = None
        self._message = None
        self._message_id = None
        self._bulletin = False
        self._bulletin_id = None
        self._announcement_id = None
        self._group_bulletin = None

    @property
    def addressee(self) -> str:
        """Get the addressee of the message"""
        return self._addressee

    @addressee.setter
    def addressee(self, value: str):
        """Set the addressee of the message"""
        self._addressee = value

    @property
    def message(self) -> str:
        """Get the message"""
        return self._message

    @message.setter
    def message(self, value: str):
        """Set the message"""
        self._message = value

    @property
    def message_id(self) -> str:
        """Get the message ID"""
        return self._message_id

    @message_id.setter
    def message_id(self, value: str):
        """Set the message ID"""
        self._message_id = value

    @property
    def bulletin(self) -> bool:
        return self._bulletin

    @bulletin.setter
    def bulletin(self, value: bool):
        self._bulletin = value

    @property
    def bulletin_id(self) -> int:
        """Get the bulletin ID"""
        return self._bulletin_id

    @bulletin_id.setter
    def bulletin_id(self, value: int):
        """Set the bulletin ID"""
        self._bulletin_id = value

    @property
    def announcement_id(self) -> str:
        """Get the announcement ID"""
        return self._announcement_id

    @announcement_id.setter
    def announcement_id(self, value: str):
        """Set the announcement ID"""
        self._announcement_id = value

    @property
    def group_bulletin(self) -> str:
        """Get the group bulletin name"""
        return self._group_bulletin

    @group_bulletin.setter
    def group_bulletin(self, value: str):
        """Set the group bulletin name"""
        self._group_bulletin = value

    def _parse(self) -> bool:
        """
        Parse a message packet.

        The parsed values are stored within the current object.
        """

        # If this is a message, then ':" MUST be in the 9th position (C14 P71)
        if self.info[10] != ":":
            raise ParseError("Invalid message packet", self)

        # Split the message into the addressee and the actual message
        addressee = self.info[1:10]
        self.addressee = addressee.rstrip()
        message = self.info[11:]

        logger.debug("Message is addressed to {}, message is {}".format(addressee, message))

        # Is this a bulletin/announcement?
        if addressee[0:3] == "BLN":
            logger.debug("Message is a bulletin")
            self.bulletin = True

            if re.match("[0-9]", addressee[3]):
                # Bulletins have the format BLNn or BLNnaaaaa, where n is a digit between 0 and 9
                # and aaaaa is an optional group bulletin identifier
                if addressee[4:9] == "     ":
                    # Bulletin
                    self.bulletin_id = int(addressee[3])
                    logger.debug("Bulletin {}".format(self.bulletin_id))
                else:
                    # Group bulletin
                    self.group_bulletin = addressee[4:9].rstrip()
                    self.bulletin_id = int(addressee[3])

                    logger.debug("Group bulletin {} ({})".format(
                        self.group_bulletin, self.bulletin_id
                    ))

            elif re.match("[A-Z]", addressee[3]):
                # Announcements have the format BLNa, where a is a character between A and Z
                if addressee[4:9] == "     ":
                    # Announcement
                    self.announcement_id = addressee[3]
                    logger.debug("Announcement {}".format(self.announcement_id))
                else:
                    # Incorrectly-formatted bulletin
                    raise ParseError("Incorrectly-formatted bulletin: {}".format(addressee), self)

            else:
                # Incorrectly-formatted bulletin
                raise ParseError("Incorrectly-formatted bulletin: {}".format(addressee), self)

        if '{' in message:
            # Check for a message ID
            message, message_id = message.split("{")
            logger.debug("Message has message ID {}".format(message_id))

            # Message IDs must not be longer than 5 characters (C14 P71)
            if len(message_id) > 5:
                raise ParseError("Invalid message ID: {}".format(message_id), self)

            self.message = message
            self.message_id = message_id
        else:
            self.message = message

        return True

    def __repr__(self):
        if self.source:
            if self.group_bulletin:
                return "<MessagePacket: {} -> Group Bulletin {} #{}>".format(
                    self.source, self.group_bulletin, self.bulletin_id
                )
            elif self.bulletin_id:
                return "<MessagePacket: {} -> Bulletin #{}>".format(self.source, self.bulletin_id)
            elif self.announcement_id:
                return "<MessagePacket: {} -> Announcement {}>".format(
                    self.source, self.announcement_id
                )
            elif self.addressee:
                return "<MessagePacket: {} -> {}>".format(self.source, self.addressee)
            else:
                return "<MessagePacket: {}>".format(self.source)
        else:
            return "<MessagePacket>"


class ObjectPacket(APRSPacket):

    def __init__(self):
        APRSPacket.__init__(self)

    def __repr__(self):
        if self.source:
            return "<ObjectPacket: {}>".format(self.source)
        else:
            return "<ObjectPacket>"


class APRS:
    """
    Main APRS class.

    This class provides functions for parsing and decoding different kinds of APRS packets.
    Packet type-specific functions are defined under the different :class:`APRSPacket` subclasses.
    """

    @staticmethod
    def decode_uncompressed_latitude(latitude: str) -> Tuple[Union[int, float], int]:
        """
        Convert an uncompressed latitude string to a latitude and an ambiguity
        value.

        :param str latitude: an uncompressed latitude, in the form ``DDMM.HHC``

        Uncompressed latitudes have the format DDMM.HHC, where:-
         * DD are the degrees
         * MM are the minutes
         * HH are the hundredths of minutes
         * C is either N (for the northern hemisphere) or S (southern)

        MM and HH can be replaced with spaces (" ") to provide positional
        ambiguity (C6 P24).

        See also APRS 1.01 C6 P23.
        """
        logger.debug("Input latitude: {}".format(latitude))

        # Regex match to catch any obviously-invalid latitudes
        if not re.match(r'^[0-9]{2}[\s0-9]{2}\.[\s0-9]{2}[NS]$', latitude):
            raise ValueError("Invalid latitude: {}".format(latitude))

        # Determine the level of ambiguity, and replace the spaces with zeroes
        # See C6 P24
        ambiguity = latitude.count(' ')
        latitude = latitude.replace(' ', '0')
        logger.debug("Ambiguity: {}".format(ambiguity))

        try:
            # Extract the number of degrees
            degrees = int(latitude[:2])
            if degrees > 90:
                raise ValueError("Invalid degrees: {}".format(degrees))

            logger.debug("Degrees: {}".format(degrees))

            # Extract the number of minutes, convert it to a fraction of a degree,
            # and round it to 6 decimal places
            minutes = round(float(latitude[2:-1])/60, 6)
            logger.debug("Minutes: {}".format(minutes))

            # Extract the north/south
            direction = latitude[-1]
            logger.debug("Direction: {}".format(direction))

        except ValueError:
            raise

        except Exception as e:
            raise ParseError("Couldn't parse latitude {}: {}".format(
                latitude, e
            ))

        # Add the degrees and minutes to give the latitude
        lat = degrees + minutes

        # If the latitude is south of the equator, make it negative
        if direction == "S":
            lat *= -1

        logger.debug("Output latitude: {}, ambiguity: {}".format(
            lat, ambiguity
        ))
        return (lat, ambiguity)

    @staticmethod
    def encode_uncompressed_latitude(latitude: Union[float, int], ambiguity: int=0) -> str:
        """
        Encode a latitude into an uncompressed latitude format.

        :param float/int latitude: a latitude
        :param int ambiguity: an optional ambiguity level

        For more information see :func:`decode_uncompressed_latitude`
        """

        # The latitude must be a float
        if type(latitude) is not float:
            if type(latitude) is int:
                latitude = float(latitude)
            else:
                raise TypeError("Latitude must be an float ({} given)".format(type(latitude)))

        # The latitude must be between -90 and 90 inclusive
        if not -90 <= latitude <= 90:
            raise ValueError("Latitude must be between -90 and 90 inclusive ({} given)".format(
                latitude
            ))

        # The ambiguity must be an int
        if ambiguity and type(ambiguity) is not int:
            raise TypeError("Ambiguity must be an int ({} given)".format(type(ambiguity)))

        # The ambiguity must be between 0 and 4 inclusive
        if ambiguity < 0 or ambiguity > 4:
            raise ValueError("Ambiguity must be between 0 and 4 inclusive ({} given)".format(
                ambiguity
            ))

        # Determine if the latitude is north or south
        if latitude < 0:
            # Direction is south
            direction = "S"
            latitude *= -1
        else:
            direction = "N"

        # Get the degrees of latitude
        degrees = math.floor(latitude)

        # Get the minutes of latitude
        minutes = "{:0.2f}".format(round((latitude - degrees) * 60, 2)).zfill(5)

        # Apply ambiguity
        if ambiguity == 0:
            lat = "{}{}".format(degrees, minutes)
        elif ambiguity == 1:
            lat = "{}{} ".format(degrees, minutes[:-1])
        elif ambiguity == 2:
            lat = "{}{}  ".format(degrees, minutes[:-2])
        elif ambiguity == 3:
            lat = "{}{} .  ".format(degrees, minutes[:-4])
        elif ambiguity == 4:
            lat = "{}  .  ".format(degrees)

        return f"{lat}{direction}"

    @staticmethod
    def encode_uncompressed_longitude(longitude: float, ambiguity: int=0) -> str:
        """
        Encode a longitude into an uncompressed longitude format.

        :param float longitude: a longitude
        :param int ambiguity: an optional ambiguity level

        For more information see :func:`decode_uncompressed_latitude`
        """

        # The longitude must be a float
        if type(longitude) is not float:
            if type(longitude) is int:
                longitude = float(longitude)
            else:
                raise TypeError("Longitude must be a float ({} given)".format(type(longitude)))

        # The longitude must be between -180 and 180 inclusive
        if not -180 <= longitude <= 180:
            raise ValueError("Longitude must be between -180 and 180 inclusive ({} given)".format(
                longitude
            ))

        # The ambiguity must be an int
        if ambiguity and type(ambiguity) is not int:
            raise TypeError("Ambiguity must be an int ({} given)".format(type(ambiguity)))

        # The ambiguity must be between 0 and 4 inclusive
        if ambiguity < 0 or ambiguity > 4:
            raise ValueError("Ambiguity must be between 0 and 4 inclusive ({} given)".format(
                ambiguity
            ))

        # Determine if the longitude is east or west
        if longitude < 0:
            # Direction is south
            direction = "W"
            longitude *= -1
        else:
            direction = "E"

        # Get the degrees of longitude
        degrees = math.floor(longitude)

        # Get the minutes of longitude
        minutes = "{:0.2f}".format(round((longitude - degrees) * 60, 2)).zfill(5)

        # Apply ambiguity
        if ambiguity == 0:
            lng = "{}{}".format(degrees, minutes)
        elif ambiguity == 1:
            lng = "{}{} ".format(degrees, minutes[:-1])
        elif ambiguity == 2:
            lng = "{}{}  ".format(degrees, minutes[:-2])
        elif ambiguity == 3:
            lng = "{}{} .  ".format(degrees, minutes[:-4])
        elif ambiguity == 4:
            lng = "{}  .  ".format(degrees)

        return f"{lng}{direction}"

    @staticmethod
    def decode_uncompressed_longitude(longitude: str, ambiguity: int = 0) -> float:
        """
        Convert an uncompressed longitude string to a longitude value, with an
        optional ambiguity level applied.

        :param str longitude: the longitude, in the format ``DDDMM.HHC``
        :param int ambiguity: the level of ambiguity, between 1 and 4

        Uncompressed longitudes have the format DDDMM.HHC, where:-
         * DD are the degrees
         * MM are the minutes
         * HH are the hundreths of minutes
         * C is either W (for west of the meridian) or E (for east)

        Positional ambiguity is handled by the latitude, and so should be
        honoured regardless of the precision of the longitude given (as per C6 P24).
        """
        logger.debug("Input longitude: {}, ambiguity: {}".format(
            longitude, ambiguity
        ))

        # Regex match to catch any obviously-invalid longitudes
        if not re.match(r'^[0-1][0-9]{2}[\s0-9]{2}\.[\s0-9]{2}[EW]$', longitude):
            raise ValueError("Invalid longitude: {}".format(longitude))

        # If the ambiguity value is more than 0, replace longitude digits with
        # spaces as required.
        if 0 <= ambiguity <= 4:
            longitude = longitude.replace(' ', '0')
        else:
            raise ValueError("Invalid ambiguity level: {} (maximum is 4)".format(
                ambiguity
            ))

        # Extract the number of degrees
        degrees = int(longitude[:3])
        if degrees > 180:
            raise ValueError("Invalid degrees: {}".format(degrees))

        logger.debug("Degrees: {}".format(degrees))

        # Since we don't want to replace the '.', if the ambiguity is more than
        # 2, increment it by 1.
        if ambiguity > 2:
            ambiguity_level = ambiguity + 1
        else:
            ambiguity_level = ambiguity

        # Extract the number of minutes, and round it to 6 decimal places
        if ambiguity == 1:
            mins = longitude[3:-2] + "0"
        elif ambiguity == 2:
            mins = longitude[3:-3] + "00"
        elif ambiguity == 3:
            mins = longitude[3:-5] + "0.00"
        elif ambiguity == 4:
            mins = longitude[3:-6] + "00.00"
        else:
            mins = longitude[3:-1]

        minutes = round(float(mins)/60, 6)
        logger.debug("Ambiguity level: {}".format(ambiguity_level))
        logger.debug("Minutes: {}".format(minutes))

        # Extract the east/west
        direction = longitude[-1]

        logger.debug("Direction: {}".format(direction))

        # Add the degrees and minutes to give the longitude
        lng = degrees + minutes

        # If the longitude is west of the meridian, make it negative
        if direction == "W":
            lng *= -1

        logger.debug("Output longitude: {}".format(lng))
        return lng

    @staticmethod
    def decode_compressed_latitude(latitude: str) -> float:
        """
        Convert a compressed latitude string to a latitude value.

        :param str latitude: a latitude in a compressed format

        Compressed latitudes have the format YYYY, where all values are base-91
        printable ASCII characters.

        See also APRS 1.01 C9 P38.
        """
        logger.debug("Input compressed latitude: {}".format(latitude))

        # The compressed latitude string must be 4 characters
        if len(latitude) != 4:
            raise ValueError("Input compressed latitude must be 4 characters ({} given)".format(
                len(latitude)
            ))

        try:
            # As per APRS 1.01, if the compressed latitude is y1y2y3y4, the latitude
            # can be determined with:-
            # 90 - ((y1-33) x 913 + (y2-33) x 912 + (y3-33) x 91 + y4-33) / 380926
            lat = 90 - (
                (ord(latitude[0])-33) * 91**3 +
                (ord(latitude[1])-33) * 91**2 +
                (ord(latitude[2])-33) * 91 +
                (ord(latitude[3])-33)
            ) / 380926
            lat = round(lat, 6)
        except IndexError:
            raise ParseError("Couldn't parse compressed latitude {}".format(
                latitude
            ))

        # Return latitude
        logger.debug("Output latitude: {}".format(lat))
        return lat

    @staticmethod
    def decode_compressed_longitude(longitude: str) -> float:
        """
        Convert a compressed longitutde string latitude value.

        :param str longitude: a longitude in compressed format

        Compressed longitude have the format XXXX, where all values are base-91
        printable ASCII characters

        See also APRS 1.01 C9 P38
        """
        logger.debug("Input compressed longitude: {}".format(longitude))

        try:
            # If the compressed longitude is x1x2x3x4, the longitude can be determined
            # with:-
            # -180 + ((x1-33) x 913 + (x2-33) x 912  + (x3-33) x 91 + x4-33) / 190463
            lng = -180 + (
                (ord(longitude[0])-33) * 91**3 +
                (ord(longitude[1])-33) * 91**2 +
                (ord(longitude[2])-33) * 91 +
                (ord(longitude[3])-33)
            ) / 190463
            lng = round(lng, 6)
        except IndexError:
            raise ParseError("Couldn't parse compressed longitude {}".format(longitude))

        # Return longitude
        logger.debug("Output longitude: {}".format(lng))
        return lng

    @staticmethod
    def decode_timestamp(raw_timestamp: str) -> int:
        """
        Decode a timestamp.

        :param str raw_timestamp: a string representing a timestamp

        Timestamps can take a number of different forms:-
         * Zulu, identified with a trailing 'z', which refers to zulu time
         * Local, identified with a trailing '/', which has no timezone information
         * A hour/minute/second timestamp without any date information
        """

        logger.debug("Raw timestamp is {}".format(raw_timestamp))
        ts = re.match(r'^(\d{6})([\/hz])', raw_timestamp)
        if ts:
            timestamp, timestamp_type = ts.groups()

            # Parse the timestamp type
            if timestamp_type == 'z':
                timestamp_type = 'zulu'
                logger.debug("Timestamp is zulu time")
            elif timestamp_type == '/':
                timestamp_type = 'local'
                logger.debug("Timestamp is local time")
            elif timestamp_type == 'h':
                timestamp_type = 'hms'
                logger.debug("Timestamp is hhmmss time")
            else:
                logger.error("Invalid timestamp type: {}".format(timestamp_type))
                raise ParseError("Invalid timestamp type: {}".format(timestamp_type))

            # Get the current UTC ('zulu') time for comparison. Since timestamps in HHMMSS format
            # have no date information, we need to determine if the timestamp is for today or
            # yesterday
            utc = datetime.utcnow()

            if timestamp_type == 'hms':
                # HHMMSS format

                # Parse out the hour, minute and second
                hour = int(timestamp[0:2])
                minute = int(timestamp[2:4])
                second = int(timestamp[4:6])

                try:
                    # Generate a datetime object
                    ts = datetime(utc.year, utc.month, utc.day, hour, minute, second)
                except ValueError as e:
                    raise ParseError("Error parsing timestamp '{}': {}".format(raw_timestamp, e))

                # Check it's not in the future
                if ts > utc:
                    # The timestamp is in the future, so go back a day
                    ts -= timedelta(days=1)

                # Convert to seconds
                timestamp = int(ts.timestamp())
                logger.debug("Timestamp is {}".format(ts.strftime("%Y%m%d%H%M%S")))

            elif timestamp_type == 'zulu' or timestamp_type == 'local':
                if timestamp_type == 'local':
                    # Assume local time is zulu time
                    # NOTE: this is against the spec, but without knowing the local
                    # timezone, it's impossible to work out. APRS 1.01 C6 P22 states "It is
                    # recommended that future APRS implementations only transmit zulu format on the
                    # air", so hopefully this shouldn't be a problem in reality.
                    logger.info("Local time specified in timestamp, assuming UTC.")

                # DDHHMM
                day = int(timestamp[0:2])
                hour = int(timestamp[2:4])
                minute = int(timestamp[4:6])

                # TODO - handle broken timestamps a bit nicer
                try:
                    ts = datetime(utc.year, utc.month, day, hour, minute, 0)
                except ValueError:
                    raise ParseError("Error parsing timestamp: {}".format(timestamp))

                # Check it's not in the future
                if ts > utc:
                    logger.debug("Timestamp day in previous month.")
                    # The time is in the future, so go back a month
                    # timedelta doesn't support subtracting months, so here be
                    # dirty hacks.
                    if 1 < ts.month <= 12:
                        month = ts.month - 1
                        ts = datetime(utc.year, month, day, hour, minute, 0)
                    elif ts.month == 1:
                        year = ts.year - 1
                        month = 12
                        ts = datetime(year, month, day, hour, minute, 0)
                    else:
                        raise ParseError("Error parsing ddhhmm timestamp: {}".format(timestamp))

                # Convert to seconds
                timestamp = int(ts.timestamp())
                logger.debug("Timestamp is {}".format(ts.strftime("%Y%m%d%H%M%S")))

            return timestamp

        else:
            raise ParseError("No timestamp found in packet")

    @staticmethod
    def decode_phg(phg: str) -> Tuple[int, int, int, Optional[int]]:
        """
        Decode a PHG (Power, Effective Antenna Height/Gain/Directivity) value and return the
        individual values.

        :param str phg: a PHG value, minus the initial ``PHG`` identifier

        The PHG extension provides a way of specifying approximate values for:-
         * Power (in watts)
         * Height above average local terrain (in feet)
         * Antenna gain (in dB)
         * Directivity (in degrees)

        PHG values are 4 characters long, and each digit is responsible for one of the above values.
        As per the APRS spec, the height value can be any ASCII character from 0 upwards.

        See APRS 1.01 C7 P28
        """

        # Ensure this is a valid PHG value
        if not re.match(r'^[0-9]\w[0-9]{2}$', phg):
            raise ValueError(f"Invalid PHG value: {phg}")

        # Decode the power value
        # To get this, we square the value
        power = int(phg[0])**2
        logger.debug(f"Power is {power} watts")

        # Decode the height value
        # To get this, we raise 2 to the power of the ASCII value of the character, minus 48, then
        # times it by 10
        height = (2 ** (ord(phg[1])-48)) * 10
        logger.debug(f"Height is {height} feet")

        # Decode the gain value
        # The gain is just the digit, in dB
        gain = int(phg[2])
        logger.debug(f"Gain is {gain}dB")

        # Decode the directivity
        # The directivity is 360 divided by 8, times the directivity value
        # A value of 0 implies an omnidirectional antenna
        if int(phg[3]) == 0:
            directivity = None
            logger.debug(f"Directivity is omnidirectional")
        else:
            directivity = int((360/8) * int(phg[3]))
            logger.debug(f"Directivity is {directivity} degrees")

        return (power, height, gain, directivity)

    @staticmethod
    def encode_phg(power: int, height: int, gain: int, directivity: Union[int, str]) -> str:
        """
        Encode a PHG (Power, Effective Antenna Height/Gain/Directivity) value from individual
        values.

        :param int power: the power, in watts
        :param int height: the antenna height, in feet
        :param int gain: the antenna gain, in dB
        :param int/str directivity: the antenna directivity, in degrees

        For more information, see :func:`decode_phg`.
        """

        # Validate the given values
        # Power must be a value between 0 to 9 squared
        if type(power) is not int:
            raise TypeError("Power must be of type 'int' ({} given)".format(type(power)))
        elif power not in [v ** 2 for v in range(0, 10)]:
            raise ValueError("Power must be one of {} ({} given)".format(
                [v ** 2 for v in range(0, 10)], power
            ))
        else:
            p = int(math.sqrt(power))
            logger.debug(f"Encoded power {power} is {p}")

        # Antenna height must be a value that is 2 raised to the power of the ASCII value higher
        # than or equal to '0' minus 48, then multiplied by 10
        if type(height) is not int:
            raise TypeError("Height must be of type 'int' ({} given)".format(type(height)))
        elif height not in [(2 ** (v-48))*10 for v in range(48, 127)]:
            raise ValueError("Height must be one of {} ({} given)".format(
                [(2 ** (v-48))*10 for v in range(48, 127)], height
            ))
        else:
            h = chr(int((math.log((height/10), 2)+48)))

        # Antenna gain must be a number between 0 and 9 inclusive
        if type(gain) is not int:
            raise TypeError("Gain must be of type 'int' ({} given)".format(type(gain)))
        elif not 0 <= gain <= 9:
            raise ValueError("Gain must be between 0 and 9 inclusive ({} given)".format(
                gain
            ))
        else:
            g = gain

        # Directivity must be a multiple of 45
        if directivity is None:
            d = 0
        elif type(directivity) is int:
            if directivity % (360/8) != 0.0:
                raise ValueError("Directivity must be a multiple of 45 ({} given)".format(
                    directivity
                ))
            else:
                d = int(directivity / 45)
        else:
            raise TypeError(
                "Directivity must either be of type 'int' or None ({} given)".format(
                    type(directivity)
                ))

        # Return the encoded PHG value
        return f"{p}{h}{g}{d}"

    @staticmethod
    def decode_dfs(dfs: str) -> Tuple[int, int, int, Optional[int]]:
        """
        Decode a DFS (Omni-DF Signal Strength) value and return the individual values.

        :param str dfs: a DFS value, minus the initial ``DFS`` identifier

        The DFS extension provides a way of specifying approximate values for:-
         * Received signal strength (in S-points)
         * Antenna height above average terrain (in feet)
         * Antenna gain (in dB)
         * Directivity (in degrees)

        Like PHG values, DFS values are 4 characters long, and each digit is responsible for one of
        the above values. The APRS spec does not specify it, but it is assumed that - like the PHG
        value - the antenna height can be any ASCII value from 0 upwards.

        See APRS 1.01 C7 P29
        """

        # Ensure this is a valid DFS value
        if not re.match(r'^[0-9]\w[0-9]{2}$', dfs):
            raise ValueError(f"Invalid DFS value: {dfs}")

        # Decode the strength value
        # This just the digit, in dB
        strength = int(dfs[0])
        logger.debug(f"Strength is S{strength}")

        # Decode the height value
        # To get this, we raise 2 to the power of the ASCII value of the character, minus 48, then
        # times it by 10
        height = (2 ** (ord(dfs[1])-48)) * 10
        logger.debug(f"Height is {height} feet")

        # Decode the gain value
        # The gain is just the digit, in dB
        gain = int(dfs[2])
        logger.debug(f"Gain is {gain}dB")

        # Decode the directivity
        # The directivity is 360 divided by 8, times the directivity value
        # A value of 0 implies an omnidirectional antenna
        if int(dfs[3]) == 0:
            directivity = None
            logger.debug(f"Directivity is omnidirectional")
        else:
            directivity = (360/8) * int(dfs[3])
            logger.debug(f"Directivity is {directivity} degrees")

        return (strength, height, gain, directivity)

    @staticmethod
    def encode_dfs(strength: int, height: int, gain: int, directivity: int = None) -> str:
        """
        Encode a DFS (Omni-DF Signal Strength) value from individual values.

        :param int strength: the received signal strength, in S-points
        :param int height: the antenna height, in feet
        :param int gain: the antenna gain, in dB
        :param int/str directivity: the antenna directivity, in degrees, or ``omni``

        For more information, see :func:`decode_dfs`.
        """

        # Signal strength must be a digit between 0 and 9 inclusive

        if type(strength) is not int:
            raise TypeError("Signal strength must be of type 'int' ({} given)".format(
                type(strength)
            ))
        elif not 0 <= strength <= 9:
            raise ValueError(
                "Signal strength must be between 0 and 9 inclusive ({} given)".format(
                    strength
                ))
        else:
            s = strength

        # Antenna height must be a value that is 2 raised to the power of the ASCII value higher
        # than or equal to '0' minus 48, then multiplied by 10
        if type(height) is not int:
            raise TypeError("Height must be of type 'int' ({} given)".format(type(height)))
        elif height not in [(2 ** (v-48))*10 for v in range(48, 127)]:
            raise ValueError("Height must be one of {} ({} given)".format(
                [(2 ** (v-48))*10 for v in range(48, 127)], height
            ))
        else:
            h = chr(int((math.log((height/10), 2)+48)))

        # Antenna gain must be a number between 0 and 9 inclusive
        if type(gain) is not int:
            raise TypeError("Gain must be of type 'int' ({} given)".format(type(gain)))
        if not 0 <= gain <= 9:
            raise ValueError("Gain must be between 0 and 9 inclusive ({} given)".format(
                gain
            ))
        else:
            g = gain

        # Directivity must be a multiple of 45
        if directivity is None:
            d = 0
        elif type(directivity) is int:
            if directivity % (360/8) != 0.0:
                raise ValueError("Directivity must be a multiple of 45 ({} given)".format(
                    directivity
                ))
            else:
                d = int(directivity / 45)
        else:
            raise TypeError(
                "Directivity must either be of type 'int' or None ({} given)".format(
                    type(directivity)
                ))

        return f"{s}{h}{g}{d}"

    @staticmethod
    def decode_nrq(nrq: str) -> Tuple[Optional[Union[float, str]], Optional[int], Optional[int]]:
        """
        Parse an NRQ (Number/Range/Quality) value and return the individual values.

        :param str nrq: an NRQ value

        For direction-finding reports, the NRQ value provides:-
         * The number of hits per period relative to the length of the time period (as a percentage)
         * The range (in miles)
         * The bearing accuracy (in degrees)

        NRQ values are 3 digits long, and all digits from 0 to 9. An 'N' value of 0 implies that the
        rest of the values are meaningless. An 'N' value of 9 indicates that the report is manual.

        The bearing accuracy represents the degree of accuracy, so a 'Q' value of 3 is 64, meaning
        that the accuracy is to less than 64 degrees.

        See APRS 1.01 C7 P30
        """

        # Ensure this is a valid NRQ value
        if not re.match(r'^[0-9]{3}$', nrq):
            raise ValueError(f"Invalid NRQ value: {nrq}")

        # Decode the number of hits
        # We can get this by dividing 100 / 8, then multiplying by the value
        if nrq[0] == "0":
            number = None
            rng = None
            quality = None
        else:
            if nrq[0] == "9":
                number = "manual"
                logger.debug(f"NRQ value is manually reported")
            else:
                number = (100/8) * int(nrq[0])
                logger.debug(f"Number of hits is {number}%")

            # The range is 2 to the power of the range value
            rng = 2 ** int(nrq[1])
            logger.debug(f"Range is {rng} miles")

            # The quality is in degrees. 9 through 3 double the value each time, starting at 1.
            # 2 and 1 are 120 and 240 respectively. 0 implies a useless quality level.
            if int(nrq[2]) > 2:
                quality = 2 ** (9-int(nrq[2]))
            elif int(nrq[2]) == 2:
                quality = 120
            elif int(nrq[2]) == 1:
                quality = 240
            else:
                quality = None

            if quality:
                logger.debug(f"Bearing accuracy is < {quality} degrees")
            else:
                logger.debug("Bearing accuracy is useless")

        return (number, rng, quality)

    @staticmethod
    def parse(packet: str = None) -> "APRSPacket":
        """
        Parse an APRS packet, and return a subclass of :class:`APRSPacket` appropriate for the
        packet type.

        :param str packet: a raw packet

        Given a raw packet, this function will return a object that is a subclass of
        :class:`APRSPacket`.
        """

        try:
            # Parse out the source, destination, path and information fields
            (source, destination, path, info) = re.match(
                r'([\w\d\-]+)>([\w\d\-]+),([\w\d\-\*\,]+):(.*)',
                packet
            ).groups()
        except AttributeError:
            raise ParseError("Could not parse packet details", packet)

        # Create a checksum, to provide a quick comparison against other packets
        checksum = md5((source + info).encode()).hexdigest()
        logger.debug("Packet checksum is {}".format(checksum))

        logger.debug("Raw packet: {}".format(packet))

        # Do some basic sanity checking
        # The source and destination fields should be a maximum of 9 characters
        logger.debug("Destination length is {}".format(len(destination)))
        if len(source) > 9:
            raise ParseError("Source address is longer than 9 characters", packet)
        elif len(destination) > 9:
            raise ParseError("Destination address is longer than 9 characters", packet)

        # The destination field should be upper case
        if not re.match(r'^[A-Z0-9]{1,6}(\-[0-9]{1,2})?$', destination):
            raise ParseError("Destination address is invalid", packet)

        # Parse the information field
        data_type_id = info[0]

        if data_type_id in '!/=@':
            logger.debug("Packet is a position packet")
            p = PositionPacket()

            if len(info) < 5:
                # TODO - handle this properly
                raise ParseError("Packet is too short.")

        elif data_type_id in "`'":
            logger.debug("Packet is a Mic-E packet")
            p = MICEPacket()

        elif data_type_id == ";":
            logger.debug("Packet is an object packet")
            p = ObjectPacket()

        elif data_type_id == ":":
            logger.debug("Packet is a message packet")
            p = MessagePacket()

        elif data_type_id == "T":
            raise UnsupportedError("Unsupported data type: 'T' (Telemetry) - C13 P68")

        elif data_type_id == ">":
            logger.debug("Packet is a status packet")
            p = StatusPacket()

        elif data_type_id == "<":
            raise UnsupportedError("Unsupported data type: '<' (Station Capabilities) - C15 P77")

        elif 0 <= info.find('!') <= 40:
            # As per APRS 1.0 C5 P18, position-without-timestamp packets may have the '!' located
            # anywhere up to the 40th character in the information field. If we're here, test for
            # that now.
            logger.debug("Found ! in information field, parsing as position packet")
            p = PositionPacket()

        else:
            logger.error("Unknown data type: {} (raw: {})".format(data_type_id, packet))
            # Return a generic APRS Packet with the basic info
            p = APRSPacket()

        # Set the source, destination, path and information fields, along with the checksum, data
        # type ID and the raw packet
        p.source = source
        p.destination = destination
        p.path = path
        p.info = info
        p.checksum = checksum
        p.data_type_id = data_type_id
        p._raw = packet

        # Call the packet-specific parser
        p._parse()

        # Return the packet object
        return p

