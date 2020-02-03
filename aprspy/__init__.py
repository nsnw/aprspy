#!/usr/bin/env python

import re
import logging

from hashlib import md5
from collections import namedtuple
from datetime import datetime

from .exceptions import ParseError, UnsupportedError
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

__version__ = "0.3.1"

# Set up logging
logger = logging.getLogger(__name__)

# Named tuple to hold original raw values
Raw = namedtuple('Raw', ['source', 'destination', 'path', 'information'])

BEACON_ADDRESSES = [
    'AIR', 'ALL', 'AP', 'BEACON', 'CQ', 'GPS', 'DF', 'DGPS', 'DRILL', 'DX', 'ID', 'JAVA', 'MAIL',
    'MICE', 'QST', 'QTH', 'RTCM', 'SKY', 'SPACE', 'SPC', 'SYM', 'TEL', 'TEST', 'TLM', 'WX', 'ZIP'
]


def _handle_err(exception: Exception, packet: str, strict_mode: bool = True):
    if not strict_mode:
        logger.warning("Returning generic packet for: {}".format(packet))
    else:
        raise exception


class APRS:
    """
    Main APRS class.

    This class provides functions for parsing and decoding different kinds of APRS packets.
    Packet type-specific functions are defined under the different :class:`APRSPacket` subclasses.
    """

    @staticmethod
    def parse(packet: str = None, timestamp: datetime = None,
              strict_mode: bool = True) -> GenericPacket:
        """
        Parse an APRS packet, and return a subclass of :class:`APRSPacket` appropriate for the
        packet type.

        :param str packet: a raw packet
        :param datetime timestamp: an (optional) timestamp indicating when the packet arrived

        Given a raw packet, this function will return a object that is a subclass of
        :class:`APRSPacket`.
        """

        try:
            # Parse out the source, destination, path and information fields
            (source, destination, path, data_type_id, info) = re.match(
                r'([\w\d\-]+)>([\w\d\-]+),([\w\d\-\*\,]+):(.)(.*)',
                packet
            ).groups()
        except AttributeError:
            _handle_err(
                ParseError("Could not parse packet details", packet),
                packet,
                strict_mode
            )
            p = GenericPacket()

        # Create a checksum, to provide a quick comparison against other packets
        checksum = md5((source + info).encode()).hexdigest()
        logger.debug("Packet checksum is {}".format(checksum))

        logger.debug("Raw packet: {}".format(packet))

        # Do some basic sanity checking
        # The source and destination fields should be a maximum of 9 characters
        logger.debug("Destination length is {}".format(len(destination)))
        if len(source) > 9:
            _handle_err(
                ParseError("Source address is longer than 9 characters", packet),
                packet,
                strict_mode
            )
            p = GenericPacket()

        elif len(destination) > 9:
            _handle_err(
                ParseError("Destination address is longer than 9 characters", packet),
                packet,
                strict_mode
            )
            p = GenericPacket()

        # The destination field should be upper case
        if not re.match(r'^[A-Z0-9]{1,6}(\-[0-9]{1,2})?$', destination):
            _handle_err(
                ParseError("Destination address is invalid", packet),
                packet,
                strict_mode
            )
            p = GenericPacket()

        # Check for common beacon destinations
        if destination in BEACON_ADDRESSES:
            logger.debug("Packet is a beacon packet")
            p = BeaconPacket()

        elif data_type_id in '!/=@':
            logger.debug("Packet is a position packet")
            p = PositionPacket()

            if len(info) < 4:
                # TODO - handle this properly
                _handle_err(
                    ParseError("Packet is too short."),
                    packet,
                    strict_mode
                )
                p = GenericPacket()

        elif data_type_id in "`'":
            logger.debug("Packet is a Mic-E packet")
            p = MICEPacket()

        elif data_type_id == ";":
            logger.debug("Packet is an object packet")
            p = ObjectPacket()

        elif data_type_id == ")":
            _handle_err(
                UnsupportedError("Unsupported data type: '<' (Item Report) - C11 P57"),
                packet,
                strict_mode
            )
            p = GenericPacket()

        # Check for the presence of PARM, UNIT, EQNS or BITS, indicating a message defining
        # telemetry data. The APRS spec places a 67-character limit on the message field, but
        # it's common to see telemetry definitions exceed this
        elif re.search(r'::[A-Za-z0-9\-]+\s?:(PARM|UNIT|EQNS|BITS)\.', packet):
            definition_type = re.search(
                r'::[A-Za-z0-9\-]+\s?:(PARM|UNIT|EQNS|BITS)\.',
                packet
            ).groups()[0]

            if definition_type == "PARM":
                p = TelemetryParameterNamePacket()

            elif definition_type == "UNIT":
                p = TelemetryUnitLabelPacket()

            elif definition_type == "EQNS":
                p = TelemetryEquationCoefficientsPacket()

            elif definition_type == "BITS":
                p = TelemetryBitSenseProjectNamePacket()

            else:
                _handle_err(
                    ParseError("Invalid telemetry definition type: {}".format(definition_type)),
                    packet,
                    strict_mode
                )
                p = GenericPacket()

        elif data_type_id == ":":
            logger.debug("Packet is a message packet")
            p = MessagePacket()

        elif data_type_id == "T":
            logger.debug("Packet is a telemetry packet")
            p = TelemetryPacket()

        elif data_type_id == ">":
            logger.debug("Packet is a status packet")
            p = StatusPacket()

        elif data_type_id == "<":
            logger.debug("Packet is a station capability packet")
            p = StationCapabilityPacket()

        elif data_type_id == "$":
            _handle_err(
                UnsupportedError("Unsupported data type: '$' (Raw NMEA Position Report)"),
                packet,
                strict_mode
            )
            p = GenericPacket()

        elif data_type_id == "_":
            _handle_err(
                UnsupportedError("Unsupported data type: '_' (Positionless Weather Report"),
                packet,
                strict_mode
            )
            p = GenericPacket()

        elif data_type_id == "*":
            _handle_err(
                UnsupportedError("Unsupported data type: '*' (Complete Weather Report"),
                packet,
                strict_mode
            )
            p = GenericPacket()

        elif 0 <= info.find('!') <= 40:
            # As per APRS 1.01 C5 P18, position-without-timestamp packets may have the '!' located
            # anywhere up to the 40th character in the information field. If we're here, test for
            # that now.
            logger.debug("Found ! in information field, parsing as position packet")
            p = PositionPacket()

            # Store the offset
            p._offset = info.find('!')

            # Because we normally assume the first character of the info field is the data type ID,
            # update the info field to include it
            info = data_type_id + info

            # Set the data type ID
            data_type_id = '!'

        else:
            _handle_err(
                UnsupportedError("Unknown data type: {} (raw: {})".format(data_type_id, packet)),
                packet,
                strict_mode
            )
            # Return a generic APRS Packet with the basic info
            p = GenericPacket()

        # Set the source, destination, path and information fields, along with the checksum, data
        # type ID and the raw packet
        p.source = source
        p.destination = destination
        p.path = path
        p._info = info
        p.checksum = checksum
        p.data_type_id = data_type_id
        p._ts = timestamp

        # Add the raw values to the packet object
        p._raw = Raw(source=source, destination=destination, path=path, information=info)

        # Call the packet-specific parser
        try:
            p._parse()

        except ParseError as e:
            _handle_err(
                e, packet, strict_mode
            )

            p = GenericPacket()

            p.source = source
            p.destination = destination
            p.path = path
            p._info = info
            p.checksum = checksum
            p.data_type_id = data_type_id
            p._ts = timestamp

            # Add the raw values to the packet object
            p._raw = Raw(source=source, destination=destination, path=path, information=info)

        # Return the packet object
        return p
