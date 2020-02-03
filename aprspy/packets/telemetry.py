#!/usr/bin/env python

import re
import logging
import bitstring
from bitstring import Bits

from ..exceptions import ParseError
from ..utils import APRSUtils
from .generic import GenericPacket

# Set up logging
logger = logging.getLogger(__name__)


class TelemetryAnalogValue:
    _value = None

    def __init__(self, value):
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if type(value) is str:
            if value == "":
                value = None
            elif "." in value:
                value = round(float(value), 2)
            else:
                value = int(value)

        self._value = value

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> int:
        return "<TelemetryAnalogValue: {}>".format(self.value)


class TelemetryDigitalValue:
    _value = None

    def __init__(self, value):
        self.value = value

    @property
    def value(self) -> Bits:
        return self._value

    @value.setter
    def value(self, value):
        if type(value) is str:
            if len(value) <= 8:
                self._value = Bits("0b{}".format(value))
            else:
                raise ValueError(
                    "Value must represent 8 bits or less ({} given)".format(value)
                )

        elif type(value) is int:
            self._value = Bits(uint=value, length=8)

    def __str__(self) -> str:
        return str(self.value.bin)

    def __repr__(self) -> int:
        return "<TelemetryDigitalValue: {}>".format(self.value)


class TelemetryPacket(GenericPacket):
    """
    Class to represent telemetry packets.

    See APRS 1.01 C13 P68
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._sequence_number = None
        self._av1 = None
        self._av2 = None
        self._av3 = None
        self._av4 = None
        self._av5 = None
        self._av5 = None
        self._dv = None
        self._comment = None

    @property
    def sequence_number(self) -> str:
        return self._sequence_number

    @sequence_number.setter
    def sequence_number(self, value: str):
        self._sequence_number = value

    @property
    def av1(self) -> TelemetryAnalogValue:
        return self._av1

    @av1.setter
    def av1(self, value):
        if type(value) is TelemetryAnalogValue:
            self._av1 = value
        else:
            self._av1 = TelemetryAnalogValue(value)

    @property
    def av2(self) -> TelemetryAnalogValue:
        return self._av2

    @av2.setter
    def av2(self, value):
        if type(value) is TelemetryAnalogValue:
            self._av2 = value
        else:
            self._av2 = TelemetryAnalogValue(value)

    @property
    def av3(self) -> TelemetryAnalogValue:
        return self._av3

    @av3.setter
    def av3(self, value):
        if type(value) is TelemetryAnalogValue:
            self._av3 = value
        else:
            self._av3 = TelemetryAnalogValue(value)

    @property
    def av4(self) -> TelemetryAnalogValue:
        return self._av4

    @av4.setter
    def av4(self, value):
        if type(value) is TelemetryAnalogValue:
            self._av4 = value
        else:
            self._av4 = TelemetryAnalogValue(value)

    @property
    def av5(self) -> TelemetryAnalogValue:
        return self._av5

    @av5.setter
    def av5(self, value):
        if type(value) is TelemetryAnalogValue:
            self._av5 = value
        else:
            self._av5 = TelemetryAnalogValue(value)

    @property
    def dv(self) -> TelemetryDigitalValue:
        return self._dv

    @dv.setter
    def dv(self, value):
        if type(value) is TelemetryDigitalValue:
            self._dv = value
        else:
            self._dv = TelemetryDigitalValue(value)

    @property
    def comment(self) -> str:
        return self._comment

    @comment.setter
    def comment(self, value: str):
        self._comment = value

    def _parse(self) -> bool:
        """
        Parse a telemetry packet.

        Parse and decoded values are stored in the current object.
        """

        try:
            (self.sequence_number, values) = re.match(r'#(MIC|\d+),?(.*)', self._info).groups()

        except AttributeError:
            # We didn't get any matches
            raise ParseError("Failed to parse telemetry packet.")

        try:
            (self.av1, self.av2, self.av3, self.av4, self.av5, remainder) = values.split(",", 5)

        except ValueError as e:
            # Failed to parse values
            raise ParseError("Failed to parse analog values: {}".format(e))

        # A comment, if it exists, is sometimes separated from the values by a space, and sometimes
        # by a comma. Complicating things further, sometimes the digital values aren't 8 characters
        # long.
        # Telemetry packets without the digital section BUT with a comment have also been seen. If
        # we catch an exception doing this, assume the whole remainder is a comment
        try:
            (self.dv, self.comment) = re.match(r'(\d+)[\s,]?(.*)', remainder).groups()

        except AttributeError:
            # No match, which means there's no digital values
            self.comment = remainder

        except ValueError:
            # This is likely due to an invalid digital value
            logger.warning("Invalid digital value in '{}', ignoring.".format(remainder))

        except bitstring.CreationError:
            # Failed to add the digital value, so skip it
            logger.warning("Invalid digital value in '{}', ignoring.".format(remainder))

        return True

    def __repr__(self):
        if self.source:
            return "<TelemetryPacket: {}>".format(self.source)
        else:
            return "<TelemetryPacket>"
