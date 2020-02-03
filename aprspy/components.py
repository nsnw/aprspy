#!/usr/bin/env python

import logging
import re

from typing import List, Optional, Union
from enum import Enum

from .exceptions import ParseError

# Set up logging
logger = logging.getLogger(__name__)


class QConstruct(Enum):
    """
    Enum for specifying q constructs.
    """
    qAC = "qAC"
    qAX = "qAX"
    qAU = "qAU"
    qAo = "qAo"
    qAO = "qAO"
    qAS = "qAS"
    qAr = "qAr"
    qAR = "qAR"
    qAZ = "qAZ"
    qAI = "qAI"


class Station:
    """
    Class for describing a station, with an optional SSID
    """
    _callsign = None

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
        logger.debug(value)
        # Ensure we're being given a str
        if type(value) is not str:
            raise TypeError("Callsign must be of type 'str' ({} given)".format(type(value)))

        callsign_ssid_regex = '^[A-Za-z0-9]+-[A-Za-z0-9]{1,2}$'
        callsign_only_regex = '^[A-Za-z0-9]+$'

        if re.match(callsign_ssid_regex, value):
            # We have been given a callsign and an SSID
            (self._callsign, self.ssid) = value.split("-")

        elif re.match(callsign_only_regex, value):
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
                if re.match(r'^[0-9]{1,2}', value):
                    # Can we convert it to an int?
                    try:
                        if int(value) == 0:
                            self._ssid = None
                        elif int(value) <= 15:
                            self._ssid = int(value)
                        else:
                            self._ssid = value

                    except ValueError:
                        # Not an integer
                        self._ssid = value
                else:
                    self._ssid = value
            else:
                raise ValueError("SSID is invalid")

        elif type(value) is int:
            if value == 0:
                self._ssid = None
            elif 1 <= value <= 15:
                self._ssid = value
            else:
                raise ValueError("SSID is invalid")

        else:
            raise TypeError("SSID must be of type 'str', 'int' or 'None' ({} given)".format(
                type(value)
            ))

    @property
    def is_valid_ax25(self) -> bool:
        """Get whether this station is a valid AX.25 address"""
        if len(self.callsign) > 6:
            # Callsign is longer than 6 characters
            return False

        if type(self.ssid) is int:
            return True
        elif self.ssid is None:
            return True
        else:
            return False

    def __str__(self) -> str:
        if self.ssid:
            return f"{self.callsign}-{self.ssid}"
        else:
            return self.callsign

    def __repr__(self) -> str:
        return "<Station: {}>".format(
            str(self)
        )


class PathHop:
    """
    Class for describing a single path hop.
    """
    def __init__(self, hop: Union[str, Station, QConstruct], used: bool = False):
        """
        Create a new path hop.

        :param str/Station/QConstruct hop: a path hop as either a ``str`` (with or without a
        trailing ``*`` to denote a used hop), a :class:`Station` or a :class:`Station`.
        :param bool used: whether the hop has been used up or not

        This will create a new :class:`PathHop` object, which describes a single hop in a path.
        A number of these can be grouped together in a single :class:`Path` object.

        A used hop can be either be specified in a single argument (with ``hop``) by appending
        a ``*`` to the end of the station, or by setting ``used`` to ``True``. Both ways are handled
        the same internally.
        """

        # 'used' must be set first, since it can be updated if we're only passed a station with a
        # '*'
        self.used = used
        self.hop = hop

    @property
    def hop(self) -> Union[Station, QConstruct]:
        """Get the hop"""
        return self._hop

    @hop.setter
    def hop(self, value: Union[str, Station, QConstruct]):
        """Set the hop"""
        # Check for a Station object
        if type(value) is Station:
            self._hop = value

        # Check for QConstruct object
        elif type(value) is QConstruct:
            self._hop = value

        # Parse the hop as a string
        elif type(value) is str:
            # Check for a q construct
            if value[0:2] == "qA":
                try:
                    self._hop = QConstruct(value=value)
                except (KeyError, ValueError):
                    raise ParseError("Invalid q construct: {}".format(value))

            # Check for a trailing *
            elif value[-1] == "*":
                self.used = True
                self._hop = Station(callsign=value[:-1])

            else:
                self.used = False
                self._hop = Station(callsign=value)
        else:
            raise TypeError(
                "Station must be of type 'str', 'Hop' or 'QConstruct' ({} given)".format(
                    type(value)
                )
            )

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
            return "{}*".format(str(self.hop))
        else:
            if type(self.hop) is QConstruct:
                return str(self.hop.value)
            else:
                return str(self.hop)

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
            self._path_hops = [PathHop(hop=path_hop) for path_hop in value.split(",")]
        else:
            raise TypeError("Path must be of type 'str' ({} given)".format(type(value)))

    @property
    def hops(self) -> list:
        return self._path_hops

    def __str__(self) -> str:
        return self.path

    def __repr__(self) -> str:
        return "<Path: {}>".format(str(self))
