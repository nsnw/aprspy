import logging

from ..exceptions import ParseError
from ..utils import APRSUtils
from .generic import GenericPacket


logger = logging.getLogger(__name__)


class UserDefinedPacket(GenericPacket):
    """
    Class to represent user-defined packets.

    The APRS spec allows for user-defined data formats, using a data type of '}'.
    The next two characters are a 'user ID' and a 'user-defined packet type'.

    See APRS 1.01 C18 P87.
    """

    _user_id: str | None
    _user_defined_packet_type: str | None
    _data: str | None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._user_id = None
        self._user_defined_packet_type = None
        self._data = None

    def user_id(self) -> str:
        return self._user_id

    def user_defined_packet_type(self) -> str:
        return self._user_defined_packet_type

    def data(self) -> str:
        return self._data

    def parse(self) -> bool:
        """
        Parse a user-defined packet.

        User-defined packets are of the form '}UXnnnnnnnnnnnnnnn', where:
        - '}' is the data type identifier
        - 'U' is the user ID
        - 'X' is the user-defined packet type
        - 'nnnnnnnnnnnnnnn' is the data

        Parsed and decoded values are stored in the current object.
        """
        self._user_id = self.info[1]
        self._user_defined_packet_type = self.info[2]
        self._data = self.info[3:]
