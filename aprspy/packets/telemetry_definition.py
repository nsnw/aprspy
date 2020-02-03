#!/usr/bin/env python

import re
import logging

from ..exceptions import ParseError, GenerateError
from .generic import GenericPacket

# Set up logging
logger = logging.getLogger(__name__)


class TelemetryDefinitionPacket(GenericPacket):
    """
    Class to represent APRS message packets.

    APRS message packets can be from one station to another, or general bulletins or announcements
    which are intended for a wider audience.

    See also APRS 1.01 C14 P71
    """

    def __init__(self, *args, **kwargs):
        """
        Create a new :class:`MessagePacket` object.

        :param str addressee: the message addressee
        :param str message: the message
        """
        super().__init__(*args, **kwargs)

        # Set the data type ID
        self.data_type_id = ":"

    def _parse(self) -> bool:
        pass

    def __repr__(self):
        if self.source:
            return "<{}: {}>".format(self.__class__.__name__, self.source)
        else:
            return "<{}>".format(self.__class__.__name__)


class TelemetryParameterNamePacket(TelemetryDefinitionPacket):
    def _parse(self) -> bool:
        # If this is a message, then ':" MUST be in the 9th position (C14 P71)
        try:
            if self._info[9] != ":":
                raise ParseError(
                    "Invalid telemetry definition packet (missing : in 9th position)",
                    self
                )

        except IndexError:
            raise ParseError("Invalid telemetry definition packet (packet is too short)")

        # Get the values, ignoring the addressee portion. As per the spec (C13 P68) "The
        # message addressee is the callsign of the of the station transmitting the telemetry data".
        # We can also ignore the next 5 characters as they contain the definition type
        values = self._info[15:].split(",")

        # Fields
        fields = ['a1', 'a2', 'a3', 'a4', 'a5', 'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8']

        field_number = 0

        for value in values:
            setattr(self, fields[field_number], value)
            field_number += 1

        return True


class TelemetryUnitLabelPacket(TelemetryDefinitionPacket):
    def _parse(self) -> bool:
        # If this is a message, then ':" MUST be in the 9th position (C14 P71)
        try:
            if self._info[9] != ":":
                raise ParseError(
                    "Invalid telemetry definition packet (missing : in 9th position)",
                    self
                )

        except IndexError:
            raise ParseError("Invalid telemetry definition packet (packet is too short)")

        # Get the values, ignoring the addressee portion. As per the spec (C13 P68) "The
        # message addressee is the callsign of the of the station transmitting the telemetry data".
        # We can also ignore the next 5 characters as they contain the definition type
        values = self._info[15:].split(",")

        # Fields
        fields = ['a1', 'a2', 'a3', 'a4', 'a5', 'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8']

        try:
            field_number = 0
            for value in values:
                setattr(self, fields[field_number], value)
                field_number += 1

        except IndexError:
            raise ParseError("Invalid number of fields for telemetry definition packet.")

        return True


class TelemetryEquationCoefficientsPacket(TelemetryDefinitionPacket):
    def _parse(self) -> bool:
        # If this is a message, then ':" MUST be in the 9th position (C14 P71)
        try:
            if self._info[9] != ":":
                raise ParseError(
                    "Invalid telemetry definition packet (missing : in 9th position)",
                    self
                )

        except IndexError:
            raise ParseError("Invalid telemetry definition packet (packet is too short)")

        # Get the values, ignoring the addressee portion. As per the spec (C13 P68) "The
        # message addressee is the callsign of the of the station transmitting the telemetry data".
        # We can also ignore the next 5 characters as they contain the definition type
        values = self._info[15:].split(",")

        # Fields
        fields = [
            'a1_1', 'a1_2', 'a1_3',
            'a2_1', 'a2_2', 'a2_3',
            'a3_1', 'a3_2', 'a3_3',
            'a4_1', 'a4_2', 'a4_3',
            'a5_1', 'a5_2', 'a5_3'
        ]

        field_number = 0
        try:
            for value in values:
                setattr(self, fields[field_number], value)
                field_number += 1
        except IndexError:
            logger.warning("Equation coefficient specifies too many fields ({} > {})".format(
                len(values), len(fields)
            ))

        return True


class TelemetryBitSenseProjectNamePacket(TelemetryDefinitionPacket):
    def _parse(self) -> bool:
        # If this is a message, then ':" MUST be in the 9th position (C14 P71)
        try:
            if self._info[9] != ":":
                raise ParseError(
                    "Invalid telemetry definition packet (missing : in 9th position)",
                    self
                )

        except IndexError:
            raise ParseError("Invalid telemetry definition packet (packet is too short)")

        # Get the values, ignoring the addressee portion. As per the spec (C13 P68) "The
        # message addressee is the callsign of the of the station transmitting the telemetry data".
        # We can also ignore the next 5 characters as they contain the definition type
        values = self._info[15:].split(",")

        # Fields
        fields = ['b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8', 'project_title']

        field_number = 0
        for value in values:
            setattr(self, fields[field_number], value)
            field_number += 1

        return True
