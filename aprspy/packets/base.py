from typing import Self
from aprspy.components import Path, Station
from aprspy.exceptions import InvalidSourceException, InvalidDestinationException


class Packet:
    """
    Generic base class for APRS packets.

    This is the base class for representing an APRS packet. Anything that is common to all packets
    is defined in here.
    """
    _source: str | Station | None = None
    _destination: str | Station | None = None
    _path: str | Path | None = None
    _data_type_id: str | None = None
    _info: str | None = None

    def __init__(
            self,
            source: str = None,
            destination: str = None,
            path: str = None,
            data_type_id: str = None,
            info: str = None
    ):
        if source:
            self.source = source

        if destination:
            self.destination = destination

        if path:
            self.path = path

        if data_type_id:
            self.data_type_id = data_type_id

        if info:
            self.info = info

    @property
    def source(self) -> Station:
        """Get the source address of the packet"""
        return self._source

    @source.setter
    def source(self, value: str | Station):
        """Set the source address of the packet"""
        if type(value) is str:
            self._source = Station(callsign=value)

        elif type(value) is Station:
            self._source = value

        else:
            raise InvalidSourceException(
                f"Source must be of type 'str' or 'Station' ({type(value)} given)"
            )

    @property
    def destination(self) -> Station:
        """Get the destination address of the packet"""
        return self._destination

    @destination.setter
    def destination(self, value: str | Station):
        """Set the destination address of the packet"""
        if type(value) is str:
            self._destination = Station(callsign=value)

        elif type(value) is Station:
            self._destination = value

        else:
            raise InvalidDestinationException(
                f"Destination must be of type 'str' or 'Station' ({type(value)} given)"
            )

    @property
    def path(self) -> Path:
        """Get the path of the packet"""
        return self._path

    @path.setter
    def path(self, value: str | Path):
        """Set the path for the packet"""
        if type(value) is str:
            self._path = Path(path=value)

        elif type(value) is Path:
            self._path = value

        else:
            raise TypeError(
                f"Path must be of type 'str' or 'Path' ({type(value)} given)"
            )

    @property
    def data_type_id(self) -> str:
        """Get the data type ID of the packet"""
        return self._data_type_id

    @data_type_id.setter
    def data_type_id(self, value: str):
        """Set the data type ID of the packet"""
        self._data_type_id = value

    @property
    def info(self) -> str:
        """Get the information field of the packet"""
        return self._info

    @info.setter
    def info(self, value: str):
        """Set the information field of the packet"""
        self._info = value

    @classmethod
    def parse(
            cls,
            source: str = None,
            destination: str = None,
            path: str = None,
            info: str = None
    ) -> Self:
        """
        Parse a packet.
        """
        packet = cls()
        packet.source = source
        packet.destination = destination
        packet.path = path
        packet.info = info

        return packet
