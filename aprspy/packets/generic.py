#!/usr/bin/env python

import logging
import json
import enum
import re

from geopy.point import Point
from datetime import datetime
from bitstring import Bits

from ..components import Path, Station
from ..exceptions import GenerateError
from .base import Packet

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

        except Exception:
            raise


class GenericPacket(Packet):
    """
    Generic base class for APRS packets.

    This is the base class for representing an APRS packet. Anything that is common to all packets
    is defined in here.
    """
    _raw: str | None
    _timestamp: str | None
    _timestamp_type: str | None
    _symbol_table: str | None
    _symbol_id: str | None

    @property
    def timestamp(self) -> str:
        """Get the timestamp of the packet"""
        return getattr(self, '_timestamp', None)

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

    def parse(self) -> bool:
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

    def to_dict(self) -> dict:
        result = {}
        for attr, val in self.__dict__.items():
            name = re.sub(r'^_', '', attr)
            if type(val) is enum.EnumMeta:
                pass
            elif isinstance(val, enum.Enum):
                result[name] = val.value
            elif type(val) is Point:
                result[name] = {
                    "latitude": val.latitude,
                    "longitude": val.longitude,
                    "altitude": val.altitude,
                }
            elif type(val) is datetime:
                result[name] = val.strftime('%c')
            elif type(val) is Bits:
                result[name] = val.bin
            elif isinstance(val, (Station, Path)):
                result[name] = str(val)
            else:
                result[name] = val
        return result

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def __repr__(self):
        if self.source:
            return f"<{self.__class__.__name__}: {self.source}>"
        else:
            return f"<{self.__class__.__name__}>"
