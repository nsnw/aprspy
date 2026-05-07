#!/usr/bin/env python

import re
import logging

from ..exceptions import ParseError, GenerateError
from ..warnings import ParseWarningCode, ParseWarningSeverity
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

    def _find_sep(self) -> int:
        """Return the index of the ':' that separates addressee from content.

        The spec mandates 9-char padding, but real senders omit it. Accept ':' anywhere in
        positions 1–10.
        """
        sep = self._info.find(':')
        if sep < 1 or sep > 10:
            raise ParseError("Invalid telemetry definition packet (missing : in 9th position)", self)
        return sep

    def _parse(self) -> bool:
        pass

    def __repr__(self):
        if self.source:
            return "<{}: {}>".format(self.__class__.__name__, self.source)
        else:
            return "<{}>".format(self.__class__.__name__)


class TelemetryParameterNamePacket(TelemetryDefinitionPacket):
    def parse(self) -> bool:
        sep = self._find_sep()
        # Skip addressee, ':', and the 5-char type prefix (e.g. "PARM.")
        values = self._info[sep + 6:].split(",")

        # Fields
        fields = ['a1', 'a2', 'a3', 'a4', 'a5', 'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8']

        for field, value in zip(fields, values):
            setattr(self, field, value)
        if len(values) > len(fields):
            self._warn(ParseWarningCode.TELEMETRY_PARM_TOO_MANY_FIELDS,
                       "PARM packet has more fields than expected ({})".format(len(values)),
                       ParseWarningSeverity.LENIENT)

        return True


class TelemetryUnitLabelPacket(TelemetryDefinitionPacket):
    def parse(self) -> bool:
        sep = self._find_sep()
        values = self._info[sep + 6:].split(",")

        # Fields
        fields = ['a1', 'a2', 'a3', 'a4', 'a5', 'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8']

        for field, value in zip(fields, values):
            setattr(self, field, value)
        if len(values) > len(fields):
            self._warn(ParseWarningCode.TELEMETRY_UNIT_TOO_MANY_FIELDS,
                       "UNIT packet has more fields than expected ({})".format(len(values)),
                       ParseWarningSeverity.LENIENT)

        return True


class TelemetryEquationCoefficientsPacket(TelemetryDefinitionPacket):
    def parse(self) -> bool:
        sep = self._find_sep()
        values = self._info[sep + 6:].split(",")

        # Fields
        fields = [
            'a1_1', 'a1_2', 'a1_3',
            'a2_1', 'a2_2', 'a2_3',
            'a3_1', 'a3_2', 'a3_3',
            'a4_1', 'a4_2', 'a4_3',
            'a5_1', 'a5_2', 'a5_3'
        ]

        for field, value in zip(fields, values):
            setattr(self, field, value)
        if len(values) > len(fields):
            self._warn(ParseWarningCode.TELEMETRY_EQNS_TOO_MANY_FIELDS,
                       "Equation coefficient specifies too many fields ({} > {})".format(
                           len(values), len(fields)),
                       ParseWarningSeverity.LENIENT)

        return True


class TelemetryBitSenseProjectNamePacket(TelemetryDefinitionPacket):
    def parse(self) -> bool:
        sep = self._find_sep()
        # Format: BITS.b1b2b3b4b5b6b7b8,project_title
        remainder = self._info[sep + 6:]
        parts = remainder.split(",", 1)
        bit_string = parts[0]
        for i, field in enumerate(['b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8']):
            setattr(self, field, bit_string[i] if i < len(bit_string) else None)
        self.project_title = parts[1] if len(parts) > 1 else None

        return True
