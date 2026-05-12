#!/usr/bin/env python

import logging
import re

from typing import List, Optional, Tuple

from ..exceptions import ParseError
from ..utils import APRSUtils
from ..warnings import ParseWarning, ParseWarningCode
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
    def _decode_latitude(destination: str, _warnings: list = None) -> Tuple[float, int, bool, str, int, int, int, bool]:
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
        message_a = ""
        message_b = ""
        message_c = ""
        message_custom = False
        lng_offset = False

        # Iterate over each character of the destination address
        count = 0
        for i in destination[0:6]:
            count += 1
            # Non-standard: some firmware outputs lowercase destination chars. Map to uppercase
            # so the encoding ranges below still apply.
            if i.islower():
                _w = ParseWarning(
                    code=ParseWarningCode.MICE_INVALID_DEST_CHAR,
                    message="Lowercase character '{}' in Mic-E destination position {} "
                            "(non-standard, treating as uppercase)".format(i, count)
                )
                logger.info(str(_w))
                if _warnings is not None:
                    _warnings.append(_w)
                i = i.upper()
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

            # A-J are only valid in positions 1-3 (message bits); K is allowed everywhere as ambiguity.
            # In positions 4-6, A-J is spec-invalid but produces the same result as P-Z (enc_set 3),
            # so we warn and continue rather than rejecting the packet.
            if 65 <= ord(i) <= 74 and count > 3:
                _w = ParseWarning(
                    code=ParseWarningCode.MICE_INVALID_DEST_CHAR,
                    message="Custom message character '{}' in Mic-E destination position {} "
                            "(spec-invalid, treating as standard)".format(i, count)
                )
                logger.info(str(_w))
                if _warnings is not None:
                    _warnings.append(_w)

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
        if len(destination) > 6 and '-' in destination:
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

        # sp encodes the hundreds of speed; dc upper digit encodes units; dc lower digit encodes
        # hundreds of course; se encodes the remaining course degrees.
        speed = (sp * 10) + int(dc / 10)
        course = ((dc % 10) * 100) + se

        # Some devices encode 0 knots as sp=80 (raw), giving speed=800 here; subtracting 800 maps
        # it back to 0. The same wrap-around applies to course values >= 400.
        if speed >= 800:
            speed -= 800
        if course >= 400:
            course -= 400

        logger.debug("Speed is {} knots, course is {} degrees".format(speed, course))

        return (speed, course)

    # Device prefix characters inserted at the start of status text (APRS 1.2 C10).
    # > and ] are Kenwood (handheld/mobile); ` and ' are used by other manufacturers
    # (messaging-capable and non-messaging respectively).
    _DEVICE_PREFIXES = frozenset({'>', ']', '`', "'"})

    # Device suffix → model name, sourced from https://github.com/aprsorg/aprs-deviceid
    # Check 2-char suffixes before 1-char to avoid partial matches.
    _DEVICE_SUFFIX_MAP = {
        # Yaesu (all use _ prefix)
        '_ ': 'Yaesu VX-8',
        '_"': 'Yaesu FTM-350',
        '_#': 'Yaesu VX-8G',
        '_$': 'Yaesu FT1D',
        '_(': 'Yaesu FT2D',
        '_)': 'Yaesu FTM-100D',
        '_0': 'Yaesu FT3D',
        '_1': 'Yaesu FTM-300D',
        '_2': 'Yaesu FTM-200D',
        '_3': 'Yaesu FT5D',
        '_4': 'Yaesu FTM-500D',
        '_5': 'Yaesu FTM-510D',
        '_6': 'Yaesu FTX-1',
        '_7': 'Yaesu FTM-310D',
        '_%': 'Yaesu FTM-400DR',
        # Anytone
        '(5': 'Anytone D578UV',
        '(8': 'Anytone D878UV',
        # Byonics
        '|3': 'Byonics TinyTrak3',
        '|4': 'Byonics TinyTrak4',
        # Others
        '^v': 'HinzTec anyfrog',
        '*v': 'KissOZ Tracker',
        '*9': 'NOR AVRT9',
        ':2': 'SQ8L VP-Tracker',
        ' X': 'SainSonic AP510',
        '[1': 'APRSdroid',
        # Kenwood (single char; listed last so 2-char check takes priority)
        '=': 'Kenwood TH-D72/TM-D710',
        '^': 'Kenwood TH-D74',
        '&': 'Kenwood TH-D75',
    }

    _STANDARD_MESSAGE_TYPES = {
        (1, 1, 1): "M0: Off Duty",
        (1, 1, 0): "M1: En Route",
        (1, 0, 1): "M2: In Service",
        (1, 0, 0): "M3: Returning",
        (0, 1, 1): "M4: Committed",
        (0, 1, 0): "M5: Special",
        (0, 0, 1): "M6: Priority",
        (0, 0, 0): "Emergency",
    }

    _CUSTOM_MESSAGE_TYPES = {
        (1, 1, 1): "Custom-0",
        (1, 1, 0): "Custom-1",
        (1, 0, 1): "Custom-2",
        (1, 0, 0): "Custom-3",
        (0, 1, 1): "Custom-4",
        (0, 1, 0): "Custom-5",
        (0, 0, 1): "Custom-6",
        (0, 0, 0): "Emergency",
    }

    @property
    def message_bits(self) -> dict | None:
        """Raw Mic-E message bits decoded from the destination field.

        Returns a dict with keys ``a``, ``b``, ``c`` (each 0 or 1) and ``custom`` (bool),
        or ``None`` if not yet parsed.
        """
        return getattr(self, '_message_bits', None)

    @property
    def message_type(self) -> str | None:
        """Human-readable Mic-E message type derived from the message bits.

        Standard types: ``"M0: Off Duty"``, ``"M1: En Route"``, etc., or ``"Emergency"``.
        Custom types: ``"Custom-0"`` through ``"Custom-6"``, or ``"Emergency"``.
        Returns ``None`` if message bits have not been parsed.
        """
        bits = self.message_bits
        if bits is None:
            return None
        key = (bits["a"], bits["b"], bits["c"])
        table = self._CUSTOM_MESSAGE_TYPES if bits["custom"] else self._STANDARD_MESSAGE_TYPES
        return table.get(key)

    @staticmethod
    def _decode_telemetry(info: str, status_offset: int = 8) -> Tuple[dict, str]:
        """
        Decode Mic-E telemetry data.

        Returns a (telemetry, comment) tuple. Each analog channel value and the digital byte are
        encoded as a single byte with offset 28. Up to 5 analog channels and 1 digital byte are
        read; any remaining bytes become the comment.

        Two separator bytes are defined (APRS 1.01 C10 P54):
        - ASCII 44 (','): type 1
        - ASCII 29 (GS): type 2

        Both use the same single-byte offset-28 encoding.
        """
        data = info[status_offset + 1:]
        analog: List[int] = []
        for i in range(5):
            if i >= len(data):
                break
            analog.append(ord(data[i]) - 28)
        consumed = len(analog)
        digital: int = 0
        if consumed < len(data):
            digital = ord(data[consumed]) - 28
            consumed += 1
        return {"analog": analog, "digital": digital}, data[consumed:]

    @property
    def telemetry(self) -> Optional[dict]:
        """Telemetry data encoded in the status text, or ``None`` if absent.

        Returns a dict with keys ``analog`` (list of up to 5 int values) and
        ``digital`` (int), following APRS 1.01 C10 P54.
        """
        return getattr(self, '_telemetry', None)

    @property
    def frequency(self) -> Optional[float]:
        """Operating frequency in MHz parsed from the comment, or ``None`` if absent.

        Encoded as ``FFF.FFFMHz`` at the start of the status text per APRS 1.2 C18.
        """
        return getattr(self, '_frequency', None)

    @property
    def device_id(self) -> Optional[str]:
        """Device model name identified from the status text suffix, or ``None`` if unknown.

        Sourced from the `aprs-deviceid <https://github.com/aprsorg/aprs-deviceid>`_ database.
        Examples: ``"Kenwood TH-D74"``, ``"Yaesu FT3D"``, ``"Anytone D878UV"``.
        """
        return getattr(self, '_device_id', None)

    def parse(self) -> bool:
        """
        Parse a Mic-E packet.

        The parsed and decoded values are stored in the current object.
        """

        # Decode the latitude, ambiguity, the longitude offset, the east/west direction and the
        # message bits
        (self.latitude, self.ambiguity, lng_offset, east_west, message_a, message_b, message_c,
         message_custom) = self._decode_latitude(str(self.destination), self._parse_warnings)

        self._message_bits = {
            "a": message_a,
            "b": message_b,
            "c": message_c,
            "custom": message_custom,
        }

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

        # Detect a dropped non-printable SE+28 byte: if the symbol table is not a valid APRS
        # table identifier (/ \ or an alphanumeric overlay character), a gateway likely stripped
        # the SE+28 course byte because it was a non-printable control character. Recover by
        # reading the symbol one position earlier and adjusting all subsequent offsets.
        _status_offset = 8
        if self.symbol_table not in '/\\' and not self.symbol_table.isalnum():
            logger.debug(
                "Symbol table '{}' is not a valid APRS table ID; "
                "SE+28 byte was likely stripped by a gateway".format(self.symbol_table)
            )
            try:
                self.symbol_id = self._info[5]
                self.symbol_table = self._info[6]
            except IndexError:
                raise ParseError("Missing symbol ID", self)
            _status_offset = 7
            # Recompute course using only SP and DC bytes; SE is gone
            dc = ord(self._info[4]) - 28
            course = (dc % 10) * 100
            if course >= 400:
                course -= 400
            self.course = course
            logger.debug(
                "Symbol ID is {} symbol table is {} (shifted)".format(
                    self.symbol_id, self.symbol_table)
            )

        # Next comes either telemetry or status text (C10 P54).
        # The byte at _status_offset is either a telemetry flag (ASCII 44 or 29) or the start of
        # status text, which may open with a device prefix character (> or ]).
        if len(self._info) > _status_offset:
            status_char = self._info[_status_offset]

            if ord(status_char) in (44, 29):
                logger.debug("Packet contains telemetry data")
                self._telemetry, self.comment = self._decode_telemetry(self._info, _status_offset)
            else:
                logger.debug("Packet contains status text")

                # Strip device prefix (APRS 1.2 C10: Kenwood inserts > or ] before status text)
                text_start = _status_offset
                if status_char in self._DEVICE_PREFIXES:
                    text_start += 1

                status_text = self._info[text_start:]

                # The status text can contain an altitude value (C10 P55)
                # It's indicated by the first 4 characters, with the 4th being a '}'
                if len(status_text) >= 4 and status_text[3] == "}":
                    logger.debug("Status text contains altitude data")

                    altitude = (
                        (ord(status_text[0])-33) * 91**2 +
                        (ord(status_text[1])-33) * 91 +
                        (ord(status_text[2])-33)
                    ) - 10000

                    self.altitude = altitude
                    logger.debug("Altitude is {}m".format(altitude))
                    comment = status_text[4:]
                else:
                    comment = status_text

                # Strip old Mic-E comment terminator (0x0D) used by some devices
                comment = comment.rstrip('\r')

                # Strip device suffix (APRS 1.2 C10: manufacturer model identifier)
                suffix2 = comment[-2:] if len(comment) >= 2 else ''
                suffix1 = comment[-1] if comment else ''
                if suffix2 in self._DEVICE_SUFFIX_MAP:
                    self._device_id = self._DEVICE_SUFFIX_MAP[suffix2]
                    comment = comment[:-2]
                elif suffix1 in self._DEVICE_SUFFIX_MAP:
                    self._device_id = self._DEVICE_SUFFIX_MAP[suffix1]
                    comment = comment[:-1]

                # Extract frequency specification from start of comment (APRS 1.2 C18).
                # Format is FFF.FFFMHz — exactly 10 bytes. An optional space delimiter follows.
                freq_match = re.match(r'^(\d{3}\.\d{3})[Mm][Hh][Zz] ?', comment)
                if freq_match:
                    self._frequency = float(freq_match.group(1))
                    comment = comment[freq_match.end():]
                    logger.debug("Frequency is {} MHz".format(self._frequency))

                self.comment = comment
                logger.debug("Comment is {}".format(self.comment))
        else:
            logger.debug("Packet contains no further information.")

        return True

    def __repr__(self):
        if self.source:
            return "<MICEPacket: {}>".format(self.source)
        else:
            return "<MICEPacket>"
