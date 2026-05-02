import logging
import re
from ..exceptions import ParseError
from ..utils import APRSUtils
from .generic import GenericPacket
from geopy.point import Point


logger = logging.getLogger(__name__)


class ItemReportPacket(GenericPacket):
    """
    Class to represent item report packets.

    Item report packets use the data type identifier ')', and the latitude and longitude can be either
    compressed or uncompressed. The format is similar to that of position reports.

    The uncompressed format is:-
    * [1]     the data type identifier ')'
    * [3-9]   the item name
    * [1]     the 'live' or 'kill' status, '!' or '_' respectively
    * [8]     the latitude
    * [1]     the symbol table ID
    * [9]     the longitude
    * [1]     the symbol code
    * then:-
        * [7]     the data extension
        * [0-36]  the comment
    * or:-
        * [0-43]  the comment, without a data extension

    The compressed format has the same first 3 fields, and then:-
    * [13]    the compressed position
    * [43]    the comment

    See APRS 1.01 C11 P59.
    """

    _item_name: str | None
    _status: str | None
    _compressed: bool | None

    _point: Point | None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



    def parse(self) -> bool:
        """
        Parse an item report packet.
        """

        # Parse out the 3-9 character item name and the item status.
        name, status, rest = re.match(
            r'^([^!_]{3,9})([!_])(.*)$', self.info
        ).groups()

        logger.debug(
            f"Item name: {name}, status: {status}, rest: {rest}"
        )

        # Since data type identifier ')' is used for both compressed and uncompressed formats, we need to
        # determine which format we have by checking if the first character after the '!' or '_' is a digit.
        # A digit in this position indicates a latitude, meaning that the packet is in the uncompressed format.
        # If the character is not a digit, then the packet is in the compressed format.
        if rest[0].isdigit():
            self._compressed = False

            latitude = rest[0:8]
            symbol_table_id = rest[8]
            longitude = rest[9:18]
            symbol_code = rest[18]

            try:
                latitude, ambiguity = APRSUtils.decode_uncompressed_latitude(latitude)

            except ValueError:
                raise ParseError(f"Invalid latitude: {latitude}", self)

            try:
                longitude = APRSUtils.decode_uncompressed_longitude(longitude, ambiguity)

            except ValueError:
                raise ParseError(f"Invalid longitude: {longitude}", self)

            logger.info(
                f"Uncompressed Latitude: {latitude} Longitude: {longitude}"
            )

        else:
            self._compressed = True

            symbol_table_id = rest[0]
            compressed_latitude = rest[1:6]
            compressed_longitude = rest[6:11]
            symbol_code = rest[12]

            try:
                latitude = APRSUtils.decode_compressed_latitude(compressed_latitude)

            except ValueError:
                raise ParseError(f"Invalid compressed latitude: {compressed_latitude}", self)

            try:
                longitude = APRSUtils.decode_compressed_longitude(compressed_longitude)

            except ValueError:
                raise ParseError(f"Invalid compressed longitude: {compressed_longitude}", self)

            logger.info(
                f"Compressed Latitude: {latitude} Longitude: {longitude}"
            )

        return True
