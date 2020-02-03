#!/usr/bin/env python

import logging
import json
import enum
import re

from typing import Union
from geopy.point import Point
from datetime import datetime
from bitstring import Bits

from ..components import Path, Station
from ..exceptions import GenerateError

# Set up logging
logger = logging.getLogger(__name__)


class PacketJSONEncoder(json.JSONEncoder):
    def default(self, o):
        try:
            if type(o) is datetime:
               return o.strftime('%c')
            elif type(o) is Bits:
                return o.bin
            else:
                j = {}
                for a, v in o.__dict__.items():
                    name = re.sub(r'^_', '', a)
                    if type(v) is Point:
                        j[name] = {
                            "latitude": v.latitude,
                            "longitude": v.longitude,
                            "altitude": v.altitude
                        }
                    elif type(v) is not enum.EnumMeta:
                        j[name] = v

                return j

        except:
            breakpoint()
            raise
            pass


class GenericPacket:
    """
    Generic base class for APRS packets.

    This is the base class for representing an APRS packet. Anything that is common to all packets
    is defined in here.
    """

    def __init__(self, source: str = None, destination: str = None, path: str = None,
                 data_type_id: str = None, info: str = None, symbol_table: str = None,
                 symbol_id: str = None):
        # list to hold the path hops
        self._path_hops = []

        self._raw = None

        # Set source, destination, path and info (if given)
        self.source = source
        self.destination = destination
        self.path = path
        self.data_type_id = data_type_id
        self.symbol_table = symbol_table
        self.symbol_id = symbol_id

        # TODO - info is a bit messed up
        self._info = info

        self.checksum = None
        self.timestamp = None
        self.timestamp_type = None

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
        """Get the info field of the packet"""
        return self._info

    @info.setter
    def info(self, value: str):
        """Set the info field of the packet"""
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
    def timestamp_type(self) -> str:
        """Get the timestamp type of the packet"""
        return self._timestamp_type

    @timestamp_type.setter
    def timestamp_type(self, value: str):
        """Set the timestamp type of the packet"""
        self._timestamp_type = value

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

    @property
    def raw(self) -> str:
        if self._raw:
            return "{}>{}:{}:{}".format(
                self._raw.source, self._raw.destination, self._raw.path, self._raw.information
            )

    def _parse(self) -> bool:
        return True

    def generate(self):
        """
        Generate an APRS packet based on the current object's properties.
        """
        output = ""
        if self.source is not None:
            output += f"{self.source}>"
        else:
            raise GenerateError("Missing source address")

        if self.destination is not None:
            output += f"{self.destination},"
        else:
            raise GenerateError("Missing destination address")

        if self.path is not None:
            output += f"{self.path}:"
        else:
            raise GenerateError("Missing path")

        info = self.info

        if self.data_type_id is not None:
            output += f"{self.data_type_id}"
        else:
            raise GenerateError("Missing data type ID")

        if info is not None:
            output += f"{info}"
        else:
            raise GenerateError("Missing info")

        return output

    def to_json(self):
        j = PacketJSONEncoder().encode(self)

        return j

    def __repr__(self):
        if self.source:
            return "<GenericPacket: {}>".format(self.source)
        else:
            return "<GenericPacket>"
