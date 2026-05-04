#!/usr/bin/env python

import re
import logging

from hashlib import md5
from collections import namedtuple
from datetime import datetime
from typing import Type

from .exceptions import ParseError, UnsupportedError
from .packets.base import Packet
from .packets.generic import GenericPacket
from .packets.beacon import BeaconPacket
from .packets.position import PositionPacket
from .packets.status import StatusPacket
from .packets.mice import MICEPacket
from .packets.object import ObjectPacket
from .packets.message import MessagePacket
from .packets.telemetry import TelemetryPacket
from .packets.telemetry_definition import TelemetryParameterNamePacket, TelemetryUnitLabelPacket,\
    TelemetryEquationCoefficientsPacket, TelemetryBitSenseProjectNamePacket
from .packets.station_capability import StationCapabilityPacket
from .packets.user_defined import UserDefinedPacket
from .packets.item_report import ItemReportPacket
from .packets.nmea import NMEAPacket
from .packets.weather import WeatherPacket
from .packets.third_party import ThirdPartyPacket
from .packets.query import QueryPacket
from .packets.ultimeter import UltimeterPacket

# Set up logging
logger = logging.getLogger(__name__)

# Named tuple to hold original raw values
Raw = namedtuple('Raw', ['source', 'destination', 'path', 'information'])

BEACON_ADDRESSES = [
    'AIR', 'ALL', 'AP', 'BEACON', 'CQ', 'GPS', 'DF', 'DGPS', 'DRILL', 'DX', 'ID', 'JAVA', 'MAIL',
    'MICE', 'QST', 'QTH', 'RTCM', 'SKY', 'SPACE', 'SPC', 'SYM', 'TEL', 'TEST', 'TLM', 'WX', 'ZIP'
]


class APRS:
    """
    Main APRS class.

    This class provides functions for parsing and decoding different kinds of APRS packets.
    Packet type-specific functions are defined under the different :class:`APRSPacket` subclasses.
    """
    @classmethod
    def handle_exception(cls, exception: Exception, packet: str, strict_mode: bool = True):
        if not strict_mode:
            logger.warning("Returning generic packet for: {}".format(packet))
        else:
            raise exception

    @classmethod
    def validate_source(cls, source: str, strict: bool = False) -> bool:
        """
        Validate the source callsign.

        In strict mode, enforces the ham radio callsign format: uppercase alphanumeric, up to 6
        characters, with an optional numeric SSID of 1-2 digits.

        In lenient mode (default), accepts the wider variety of callsigns seen on APRS-IS in
        practice: case-insensitive, up to 9 characters, with an optional alphanumeric SSID of
        up to 3 characters (covering D-Star/YSF gateway suffixes like -B, -N, -R1, etc.).
        """
        if strict:
            if re.match(r'^[A-Z0-9]{1,6}$', source):
                return True
            elif re.match(r'^[A-Z0-9]{1,6}-[0-9]{1,2}$', source):
                return True
            else:
                raise ParseError(f"Invalid source callsign: {source}")
        else:
            if re.match(r'^[A-Za-z0-9]{1,9}(-[A-Za-z0-9]{1,3})?$', source):
                return True
            else:
                raise ParseError(f"Invalid source callsign: {source}")

    @classmethod
    def validate_destination(cls, destination: str, strict: bool = False) -> bool:
        """
        Validate the destination callsign or tocall.

        In strict mode, enforces uppercase alphanumeric up to 6 characters with an optional
        numeric SSID. In lenient mode (default), accepts the same relaxed format as
        validate_source.
        """
        if strict:
            if re.match(r'^[A-Z0-9]{1,6}$', destination):
                return True
            elif re.match(r'^[A-Z0-9]{1,6}-[0-9]{1,2}$', destination):
                return True
            else:
                raise ParseError(f"Invalid destination callsign or data: {destination}")
        else:
            if re.match(r'^[A-Za-z0-9]{1,9}(-[A-Za-z0-9]{1,3})?$', destination):
                return True
            else:
                raise ParseError(f"Invalid destination callsign or data: {destination}")

    @classmethod
    def parse_basic_data(cls, packet: str, strict: bool = False) -> tuple[str, str, str, str, str]:
        """
        Parse the basic data from an APRS packet:-

        * the source callsign
        * the destination callsign
        * the packet's path
        * the data type ID
        * the information field

        ...and return them as a tuple of strings.
        """
        try:
            (source, destination, path, data_type_id, info) = re.match(
                r'([A-Za-z0-9\-]+)>([A-Za-z0-9\-]+),([A-Za-z0-9\-*,]+):(.)(.*)',
                packet
            ).groups()

        except AttributeError:
            raise ParseError("Could not parse packet details", packet)

        cls.validate_source(source, strict=strict)
        cls.validate_destination(destination, strict=strict)

        return source, destination, path, data_type_id, info

    @classmethod
    def is_beacon_destination(cls, destination: str) -> bool:
        """
        Check if the destination callsign is one of the common beacon addresses.
        """
        return destination in BEACON_ADDRESSES

    @classmethod
    def is_position_data_type_id(cls, data_type_id: str) -> bool:
        """
        Check if the data type ID indicates a position packet.
        """
        return data_type_id in '!/=@'

    @classmethod
    def is_mic_e_data_type_id(cls, data_type_id: str) -> bool:
        """
        Check if the data type ID indicates a Mic-E packet.
        """
        return data_type_id in "`'"

    @classmethod
    def is_object_data_type_id(cls, data_type_id: str) -> bool:
        """
        Check if the data type ID indicates an object packet.
        """
        return data_type_id == ";"

    @classmethod
    def is_item_report_data_type_id(cls, data_type_id: str) -> bool:
        """
        Check if the data type ID indicates an item report packet.
        """
        return data_type_id == ")"

    @classmethod
    def is_message_data_type_id(cls, data_type_id: str) -> bool:
        """
        Check if the data type ID indicates a message packet.
        """
        return data_type_id == ":"

    @classmethod
    def is_telemetry_data_type_id(cls, data_type_id: str) -> bool:
        """
        Check if the data type ID indicates a telemetry packet.
        """
        return data_type_id == "T"

    @classmethod
    def is_status_data_type_id(cls, data_type_id: str) -> bool:
        """
        Check if the data type ID indicates a status packet.
        """
        return data_type_id == ">"

    @classmethod
    def is_station_capability_data_type_id(cls, data_type_id: str) -> bool:
        """
        Check if the data type ID indicates a station capability packet.
        """
        return data_type_id == "<"

    @classmethod
    def is_raw_nmea_position_report_data_type_id(cls, data_type_id: str) -> bool:
        """
        Check if the data type ID indicates a raw NMEA position report packet.
        """
        return data_type_id == "$"

    @classmethod
    def is_positionless_weather_report_data_type_id(cls, data_type_id: str) -> bool:
        """
        Check if the data type ID indicates a positionless weather report packet.
        """
        return data_type_id == "_"

    @classmethod
    def is_complete_weather_report_data_type_id(cls, data_type_id: str) -> bool:
        """
        Check if the data type ID indicates a complete weather report packet.
        """
        return data_type_id == "*"

    @classmethod
    def is_user_defined_data_type_id(cls, data_type_id: str) -> bool:
        """
        Check if the data type ID indicates a user-defined packet.
        """
        return data_type_id == "{"

    @classmethod
    def is_telemetry_parameter_name_packet(cls, packet: str) -> bool:
        """
        Check if the packet is a telemetry parameter name packet.
        """
        if re.search(r'::[A-Za-z0-9\-]+\s*:PARM\.', packet):
            return True

        return False

    @classmethod
    def is_telemetry_unit_label_packet(cls, packet: str) -> bool:
        """
        Check if the packet is a telemetry unit label packet.
        """
        if re.search(r'::[A-Za-z0-9\-]+\s*:UNIT\.', packet):
            return True

        return False

    @classmethod
    def is_telemetry_equation_coefficients_packet(cls, packet: str) -> bool:
        """
        Check if the packet is a telemetry equation coefficients packet.
        """
        if re.search(r'::[A-Za-z0-9\-]+\s*:EQNS\.', packet):
            return True

        return False

    @classmethod
    def is_telemetry_bit_sense_project_name_packet(cls, packet: str) -> bool:
        """
        Check if the packet is a telemetry bit sense project name packet.
        """
        if re.search(r'::[A-Za-z0-9\-]+\s*:BITS\.', packet):
            return True

        return False

    @classmethod
    def is_position_info_with_offset(cls, info: str) -> bool:
        """
        Check if the packet is a position packet with an offset.
        """
        if 0 <= info.find('!') <= 40:
            return True

        return False

    @classmethod
    def get_packet_type(
            cls, packet: str, source: str, destination: str, path: str, data_type_id: str,
            info: str
    ) -> Type[Packet]:
        # Determine the type of packet this is.
        # There's a ton of different packet types and many different ways in which they're
        # identified. The APRS spec is at worst a suggestion and there's a lot of variation in
        # how different packet types are constructed.

        # By default, assume the packet is a generic packet.
        packet_type = GenericPacket

        # This is used for position packets where the data is offset.
        offset = None

        # First, check if the destination is one of the common beacon addresses.
        # If it is, we can be fairly certain that this is a beacon packet.
        if cls.is_beacon_destination(destination):
            logger.debug("Packet is a beacon packet")
            packet_type = BeaconPacket

        # Next, check the data type ID to see if it matches those used by position packets.
        elif cls.is_position_data_type_id(data_type_id):
            logger.debug("Packet is a position packet")
            packet_type = PositionPacket

        # Check if the data type ID indicates a Mic-E packet.
        elif cls.is_mic_e_data_type_id(data_type_id):
            logger.debug("Packet is a Mic-E packet")
            packet_type = MICEPacket

        # Check if the data type ID indicates an object packet.
        elif cls.is_object_data_type_id(data_type_id):
            logger.debug("Packet is an object packet")
            packet_type = ObjectPacket

        # Check if the data type ID indicates an item report packet.
        elif cls.is_item_report_data_type_id(data_type_id):
            logger.debug("Packet is an item report packet")
            packet_type = ItemReportPacket

        # Check if the data type ID indicates a message packet — but first check if it's
        # actually a telemetry definition packet (PARM/UNIT/EQNS/BITS), which also uses ':' DTI.
        elif cls.is_telemetry_parameter_name_packet(packet):
            logger.debug("Packet is a telemetry parameter name packet")
            packet_type = TelemetryParameterNamePacket

        elif cls.is_telemetry_unit_label_packet(packet):
            logger.debug("Packet is a telemetry unit label packet")
            packet_type = TelemetryUnitLabelPacket

        elif cls.is_telemetry_equation_coefficients_packet(packet):
            logger.debug("Packet is a telemetry equation coefficients packet")
            packet_type = TelemetryEquationCoefficientsPacket

        elif cls.is_telemetry_bit_sense_project_name_packet(packet):
            logger.debug("Packet is a telemetry bit sense project name packet")
            packet_type = TelemetryBitSenseProjectNamePacket

        elif cls.is_message_data_type_id(data_type_id):
            logger.debug("Packet is a message packet")
            packet_type = MessagePacket

        # Check if the data type ID indicates a telemetry packet.
        # In addiition, the first character of the information field should be a '#'.
        # This _should_ be the only packet type that uses A-z for the data type ID,
        # which can clash with X1J-style position packets.
        elif cls.is_telemetry_data_type_id(data_type_id) and info[0] == "#":
            logger.debug("Packet is a telemetry packet")
            packet_type = TelemetryPacket

        # Check if the data type ID indicates a status packet.
        elif cls.is_status_data_type_id(data_type_id):
            logger.debug("Packet is a status packet")
            packet_type = StatusPacket

        # Check if the data type ID indicates a station capability packet.
        elif cls.is_station_capability_data_type_id(data_type_id):
            logger.debug("Packet is a station capability packet")
            packet_type = StationCapabilityPacket

        # Partially-supported packet types.
        # Check if the data type ID indicates a user-defined packet.
        elif cls.is_user_defined_data_type_id(data_type_id):
            logger.debug("Packet is a user-defined packet")
            logger.warning(
                "User-defined packets are not fully supported."
            )
            packet_type = UserDefinedPacket

        # Unsupported packet types.
        # Check if the data type ID indicates a raw NMEA position report packet.
        elif cls.is_raw_nmea_position_report_data_type_id(data_type_id):
            logger.debug("Packet is a raw NMEA position report packet")
            packet_type = NMEAPacket

        # Check if the data type ID indicates a positionless weather report packet.
        elif cls.is_positionless_weather_report_data_type_id(data_type_id):
            logger.debug("Packet is a positionless weather report packet")
            packet_type = WeatherPacket

        # Check if the data type ID indicates a third-party traffic packet.
        elif data_type_id == "}":
            logger.debug("Packet is a third-party traffic packet")
            packet_type = ThirdPartyPacket

        # Check if the data type ID indicates a general query packet.
        elif data_type_id == "?":
            logger.debug("Packet is a general query packet")
            packet_type = QueryPacket

        # Check if the data type ID indicates a Peet Bros Ultimeter II packet.
        # '*' = MPH variant, '#' = KPH variant (distinction uncertain per APRS spec).
        elif data_type_id in ('*', '#'):
            logger.debug("Packet is a Peet Bros Ultimeter II weather packet")
            packet_type = UltimeterPacket

        # As per APRS 1.01 C5 P18, position-without-timestamp packets may have the '!' located
        # anywhere up to the 40th character in the information field. If we're here, test for
        # that now.
        elif cls.is_position_info_with_offset(info):
            logger.debug("Packet is a position packet with an offset")
            packet_type = PositionPacket

            # Find and store the offset
            offset = info.find('!')

            # Because we normally assume the first character of the info field is the data type ID,
            # update the info field to include it
            info = data_type_id + info

            # Set the data type ID
            data_type_id = '!'

        # The end of the road. Anything still unmatched is unsupported (at the moment).
        # This is mostly packet types that do not conform to the APRS spec.
        else:
            raise ParseError(
                "Could not determine packet type"
            )

        return packet_type

    @classmethod
    def parse_packet(cls, packet: str, strict: bool = False) -> Packet | PositionPacket:
        """
        Parse an APRS packet, and return an instance of a subclass of :class:`Packet` appropriate for the
        packet type.

        :param str packet: a raw packet
        :param bool strict: if True, enforce strict ham-radio callsign format (uppercase,
            max 6 chars, numeric SSID only). Defaults to False, which accepts the wider variety
            of callsigns found on APRS-IS in practice.

        Given a raw packet, this function will return an object that is a subclass of
        :class:`Packet`.
        """
        logger.debug("Raw packet: {}".format(packet))

        # Parse out the basic details of the packet.
        (source, destination, path, data_type_id, info) = cls.parse_basic_data(
            packet=packet, strict=strict
        )

        # Create a checksum, to provide a quick comparison against other packets
        checksum = md5((source + info).encode()).hexdigest()
        logger.debug("Packet checksum is {}".format(checksum))

        packet_type = cls.get_packet_type(
            packet=packet,
            source=source,
            destination=destination,
            path=path,
            data_type_id=data_type_id,
            info=info
        )

        # For X1J-style offset packets, get_packet_type rewrites info and data_type_id locally
        # but doesn't return them. Replicate that here so the packet is constructed correctly.
        # Guard with is_position_data_type_id to avoid misidentifying compressed packets whose
        # base-91 encoded data happens to contain '!'.
        if (packet_type is PositionPacket
                and not cls.is_position_data_type_id(data_type_id)
                and cls.is_position_info_with_offset(info)):
            info = data_type_id + info
            data_type_id = '!'

        # Set the source, destination, path and information fields, along with the checksum, data
        # type ID and the raw packet
        packet = packet_type(
            source=source,
            destination=destination,
            path=path,
            data_type_id=data_type_id,
            info=info
        )

        packet.parse()

        return packet
