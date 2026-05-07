#!/usr/bin/env python

import re
import logging
import bitstring
from bitstring import Bits

from ..exceptions import ParseError
from ..utils import APRSUtils
from ..warnings import ParseWarning, ParseWarningCode
from .generic import GenericPacket

# Set up logging
logger = logging.getLogger(__name__)


class TelemetryAnalogValue:
    _value = None

    def __init__(self, value, _warnings: list = None):
        self._warnings = _warnings
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if type(value) is str:
            if value == "":
                self._value = None
                return
            try:
                self._value = round(float(value), 2) if "." in value else int(value)
                return
            except (ValueError, TypeError):
                pass

            # Try to recover a leading numeric prefix (e.g. "13.18}}" → 13.18)
            m = re.match(r'^-?[\d.]+', value)
            if m:
                recovered = m.group()
                try:
                    self._value = round(float(recovered), 2) if "." in recovered else int(recovered)
                    if self._warnings is not None:
                        self._warnings.append(ParseWarning(
                            code=ParseWarningCode.TELEMETRY_INVALID_ANALOG_VALUE,
                            message="Analog value {!r} has trailing junk; using {!r}".format(
                                value, recovered)
                        ))
                    return
                except (ValueError, TypeError):
                    pass

            if self._warnings is not None:
                self._warnings.append(ParseWarning(
                    code=ParseWarningCode.TELEMETRY_INVALID_ANALOG_VALUE,
                    message="Could not parse analog value {!r}".format(value)
                ))
            self._value = None
        else:
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
            self._av1 = TelemetryAnalogValue(value, _warnings=getattr(self, '_parse_warnings', None))

    @property
    def av2(self) -> TelemetryAnalogValue:
        return self._av2

    @av2.setter
    def av2(self, value):
        if type(value) is TelemetryAnalogValue:
            self._av2 = value
        else:
            self._av2 = TelemetryAnalogValue(value, _warnings=getattr(self, '_parse_warnings', None))

    @property
    def av3(self) -> TelemetryAnalogValue:
        return self._av3

    @av3.setter
    def av3(self, value):
        if type(value) is TelemetryAnalogValue:
            self._av3 = value
        else:
            self._av3 = TelemetryAnalogValue(value, _warnings=getattr(self, '_parse_warnings', None))

    @property
    def av4(self) -> TelemetryAnalogValue:
        return self._av4

    @av4.setter
    def av4(self, value):
        if type(value) is TelemetryAnalogValue:
            self._av4 = value
        else:
            self._av4 = TelemetryAnalogValue(value, _warnings=getattr(self, '_parse_warnings', None))

    @property
    def av5(self) -> TelemetryAnalogValue:
        return self._av5

    @av5.setter
    def av5(self, value):
        if type(value) is TelemetryAnalogValue:
            self._av5 = value
        else:
            self._av5 = TelemetryAnalogValue(value, _warnings=getattr(self, '_parse_warnings', None))

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

    def parse(self) -> bool:
        """
        Parse a telemetry packet.

        Parse and decoded values are stored in the current object.
        """

        try:
            (self.sequence_number, values) = re.match(r'#(MIC|\d+),?(.*)', self._info).groups()

        except AttributeError:
            # We didn't get any matches
            raise ParseError("Failed to parse telemetry packet.")

        # Split analog values; the spec requires 5 but many senders omit trailing ones.
        # Pad missing slots with '' so TelemetryAnalogValue stores them as None.
        parts = values.split(",", 5)
        while len(parts) < 6:
            parts.append('')
        self.av1, self.av2, self.av3, self.av4, self.av5, remainder = parts

        # A comment, if it exists, is sometimes separated from the values by a space, and sometimes
        # by a comma. Complicating things further, sometimes the digital values aren't 8 characters
        # long.
        # Telemetry packets without the digital section BUT with a comment have also been seen. If
        # we catch an exception doing this, assume the whole remainder is a comment
        try:
            (dv_str, self.comment) = re.match(r'(\d+)[\s,]?(.*)', remainder).groups()
            if not re.match(r'^[01]{1,8}$', dv_str):
                normalised = re.sub(r'[2-9]', '1', dv_str)
                self._warn(ParseWarningCode.TELEMETRY_INVALID_DIGITAL_VALUE,
                           "Digital value '{}' contains non-binary digits; normalising to '{}'".format(
                               dv_str, normalised))
                self.dv = normalised
            else:
                self.dv = dv_str

        except AttributeError:
            # No match, which means there's no digital values
            self.comment = remainder

        except ValueError:
            # This is likely due to an invalid digital value
            self._warn(ParseWarningCode.TELEMETRY_INVALID_DIGITAL_VALUE,
                       "Invalid digital value in '{}', ignoring.".format(remainder))

        except bitstring.CreationError:
            # Failed to add the digital value, so skip it
            self._warn(ParseWarningCode.TELEMETRY_INVALID_DIGITAL_VALUE,
                       "Invalid digital value in '{}', ignoring.".format(remainder))

        return True

    def __repr__(self):
        if self.source:
            return "<TelemetryPacket: {}>".format(self.source)
        else:
            return "<TelemetryPacket>"
