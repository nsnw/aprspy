#!/usr/bin/env python

import logging
import re

from typing import List, Optional, Union

# Set up logging
logger = logging.getLogger(__name__)


class Station:
    """
    Class for describing a station, with an optional SSID
    """
    def __init__(self, callsign: str, ssid: Union[str, int] = None):
        """
        Create a new station.

        :param str callsign: a callsign, with or without an SSID
        :param str/int ssid: an SSID

        This will create a new :class:`Station` object, which describes a station - with or without
        an SSID.

        A station with an SSID can either be specified in a single argument (with ``callsign``) by
        appending the SSID to it, or by setting ``ssid``. Both ways are handled the same internally.

        **Note**: stations with SSIDs other than the numbers 1-15 are only valid on APRS-IS, and
        cannot be used over AX.25.
        """

        # 'ssid' must be set first, since it can be updated if we're passed a callsign with an SSID
        self.ssid = ssid
        self.callsign = callsign

    @property
    def callsign(self) -> str:
        """Get the callsign of the station"""
        return self._callsign

    @callsign.setter
    def callsign(self, value: str):
        """Set the callsign of the station (with or without an SSID)"""
        # Ensure we're being given a str
        if type(value) is not str:
            raise TypeError("Callsign must be of type 'str' ({} given)".format(type(value)))

        if re.match(r'^[A-Za-z0-9]{1,6}-[A-Za-z0-9]{1,2}$', value):
            # We have been given a callsign and an SSID
            (self._callsign, self.ssid) = value.split("-")

        elif re.match(r'^[A-Za-z0-9]{1,6}$', value):
            # We have only been given a callsign
            self._callsign = value

        else:
            raise ValueError("Callsign is invalid")

    @property
    def ssid(self) -> str:
        """Get the SSID of the station"""
        return self._ssid

    @ssid.setter
    def ssid(self, value: Union[str, int]):
        """Set the SSID of the station"""
        # Allow None
        if value is None:
            self._ssid = None

        # Ensure we're being given a str or an int
        elif type(value) is str:
            if re.match(r'^[A-Za-z0-9]{1,2}$', value):
                # Valid SSID
                self._ssid = value
            else:
                raise ValueError("SSID is invalid")

        elif type(value) is int:
            if 0 <= value <= 15:
                self._ssid = str(value)
            else:
                raise ValueError("SSID is invalid")

        else:
            raise TypeError("SSID must be of type 'str', 'int' or 'None' ({} given)".format(
                type(value)
            ))

    def __str__(self) -> str:
        if self.ssid:
            return f"{self.callsign}-{self.ssid}"
        else:
            return self.callsign

    def __repr__(self) -> str:
        return "<Station: {}>".format(str(self))


class PathHop:
    """
    Class for describing a single path hop.
    """
    def __init__(self, station: Union[str, Station], used: bool = False):
        """
        Create a new path hop.

        :param str station: a station, with or without a trailing ``*`` to denote a used hop
        :param bool used: whether the hop has been used up or not

        This will create a new :class:`PathHop` object, which describes a single hop in a path.
        A number of these can be grouped together in a single :class:`Path` object.

        A used hop can be either be specified in a single argument (with ``station``) by appending
        a ``*`` to the end of the station, or by setting ``used`` to ``True``. Both ways are handled
        the same internally.
        """

        # 'used' must be set first, since it can be updated if we're only passed a station with a
        # '*'
        self.used = used
        self.station = station

    @property
    def station(self) -> Union[str, Station]:
        """Get the station"""
        return self._station

    @station.setter
    def station(self, value: Union[str, Station]):
        """Set the station"""
        if type(value) is Station:
            self._station = value

        elif type(value) is str and len(value) <= 9:
            if value[-1] == "*":
                self.used = True
                self._station = Station(callsign=value[:-1])
            else:
                self.used = False
                self._station = Station(callsign=value)
        else:
            raise TypeError("Station must be of type 'str' or 'Station' ({} given)".format(
                type(value)
            ))

    @property
    def used(self) -> bool:
        """Get whether the hop has been used or not"""
        return self._used

    @used.setter
    def used(self, value: bool):
        """Set whether the hop has been used or not"""
        if type(value) is bool:
            self._used = value
        else:
            raise TypeError(
                "Used status must be of type 'bool' ({} given)".format(type(value))
            )

    def __str__(self) -> str:
        if self.used:
            return "{}*".format(str(self.station))
        else:
            return str(self.station)

    def __repr__(self) -> str:
        return "<PathHop: {}>".format(str(self))


class Path:
    """
    Class for describing a path.
    """
    def __init__(self, path: Optional[Union[str, List[PathHop]]]):
        """
        Create a new path.

        :param str/List[PathHop] path: either a string representing a path, or a :term:`list` of
            :class:`PathHop` objects
        """
        self._path_hops = []
        if path:
            self.path = path

    @property
    def path(self) -> str:
        return ",".join([str(path_hop) for path_hop in self._path_hops])

    @path.setter
    def path(self, value: str):
        if type(value) is str:
            # Split the path
            self._path_hops = [PathHop(station=path_hop) for path_hop in value.split(",")]
        else:
            raise TypeError("Path must be of type 'str' ({} given)".format(type(value)))

    @property
    def hops(self) -> list:
        return self._path_hops

    def __str__(self) -> str:
        return self.path

    def __repr__(self) -> str:
        return "<Path: {}>".format(str(self))
