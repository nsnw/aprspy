#!/usr/bin/env python

import logging

from typing import Tuple

from ..exceptions import ParseError
from ..utils import APRSUtils
from .position import PositionPacket

# Set up logging
logger = logging.getLogger(__name__)


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
        # TODO - A-K not used for 4-6
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
        try:
            decoded_latitude, ambiguity = APRSUtils.decode_uncompressed_latitude(
                "{}{}".format(latitude, north_south)
            )

        except ValueError as e:
            raise ParseError(e)

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

        try:
            lng_deg = ord(info[0]) - 28
            lng_min = ord(info[1]) - 28
            lng_hmin = ord(info[2]) - 28

        except IndexError as e:
            raise ParseError("Invalid longitude: {}".format(e))

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
        try:
            longitude = APRSUtils.decode_uncompressed_longitude("{}{}.{}{}".format(
                str(lng_deg).zfill(3),
                str(lng_min).zfill(2),
                str(lng_hmin).zfill(2),
                east_west
            ))

        except ValueError as e:
            raise ParseError(e)

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
            sp = ord(info[3]) - 28
            dc = ord(info[4]) - 28
            se = ord(info[5]) - 28
        except IndexError:
            raise ParseError("Couldn't parse speed/course in Mic-E packet")

        # The speed is in knots, and is obtained by multiplying sp by 10, and adding the quotient of
        # dc divided by 10
        # TODO - handle other speed encoding scheme (see C10 P50)
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
        self.longitude = self._decode_longitude(self._info, lng_offset, east_west)

        # Decode the speed and course from the info field
        (self.speed, self.course) = self._decode_speed_and_course(self._info)

        # Parse the symbol table and symbol from the info field
        try:
            self.symbol_id = self._info[6]
            logger.debug("Symbol ID is {}".format(self.symbol_id))
        except IndexError:
            raise ParseError("Missing symbol ID", self)

        try:
            self.symbol_table = self._info[7]
            logger.debug("Symbol table is {}".format(self.symbol_table))
        except IndexError:
            raise ParseError("Missing symbol table", self)

        # Next comes either the status text or telemetry (C10 P54)
        # Telemetry is indicated by setting the first character of the status field to dec 44
        # (a ',') or the unprintable 29.
        if len(self._info) >= 10:
            if ord(self._info[8]) == 44 or ord(self._info[8]) == 29:
                logger.debug("Packet contains telemetry data")
                # TODO
            else:
                logger.debug("Packet contains status text")
                status_text = self._info[9:]

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
