#!/usr/bin/env python

import re
import logging

from hashlib import md5

from .exceptions import ParseError, UnsupportedError
from .packets.generic import GenericPacket
from .packets.position import PositionPacket
from .packets.status import StatusPacket
from .packets.mice import MICEPacket
from .packets.object import ObjectPacket
from .packets.message import MessagePacket

__version__ = "0.2.0"

# Set up logging
logger = logging.getLogger(__name__)


class APRS:
    """
    Main APRS class.

    This class provides functions for parsing and decoding different kinds of APRS packets.
    Packet type-specific functions are defined under the different :class:`APRSPacket` subclasses.
    """
    @staticmethod
    def parse(packet: str = None) -> GenericPacket:
        """
        Parse an APRS packet, and return a subclass of :class:`APRSPacket` appropriate for the
        packet type.

        :param str packet: a raw packet

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

        if data_type_id in '!/=@':
            logger.debug("Packet is a position packet")
            p = PositionPacket()

            if len(info) < 4:
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
            p = GenericPacket()

        # Set the source, destination, path and information fields, along with the checksum, data
        # type ID and the raw packet
        p.source = source
        p.destination = destination
        p.path = path
        p._info = info
        p.checksum = checksum
        p.data_type_id = data_type_id
        p._raw = packet

        # Call the packet-specific parser
        p._parse()

        # Return the packet object
        return p
