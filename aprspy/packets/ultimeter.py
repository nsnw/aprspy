#!/usr/bin/env python

import logging

from ..exceptions import ParseError
from .generic import GenericPacket

logger = logging.getLogger(__name__)

# The Ultimeter II serial format is poorly documented in the APRS spec.
# The protocol.txt description is: *DWTRRRRrrrr (MPH) / #DWTRRRRrrrr (KPH)
# with the author noting "(I may have these reversed)".
#
# Based on the "14 bytes" description and field letter layout, each field is
# 2 hex digits (1 byte), except the two rainfall fields which are 4 hex digits
# (2 bytes each): 2+2+2+4+4 = 14 chars total in the info field.
#
# Field units are inferred from context; treat parsed values as best-effort.


def _signed_byte(hex2: str) -> int | None:
    """Parse 2 hex chars as a signed byte (-128..127)."""
    try:
        v = int(hex2, 16)
        return v if v < 128 else v - 256
    except ValueError:
        return None


def _unsigned_byte(hex2: str) -> int | None:
    """Parse 2 hex chars as an unsigned byte (0..255)."""
    try:
        return int(hex2, 16)
    except ValueError:
        return None


def _unsigned_word(hex4: str) -> int | None:
    """Parse 4 hex chars as an unsigned 16-bit word (0..65535)."""
    try:
        return int(hex4, 16)
    except ValueError:
        return None


class UltimeterPacket(GenericPacket):
    """
    Class to represent Peet Bros Ultimeter II weather packets.

    DTI '*' = wind speed in MPH; DTI '#' = wind speed in KPH.
    (Note: the APRS spec author flagged uncertainty about which is which.)

    Info field format (14 hex characters):
      [0:2]   wind direction  — hex byte, 0-255 maps to 0-360 degrees
      [2:4]   wind speed      — hex byte, MPH (*) or KPH (#)
      [4:6]   temperature     — signed hex byte, degrees Fahrenheit
      [6:10]  rain total      — 16-bit hex, long-term accumulated (units unclear)
      [10:14] rain today      — 16-bit hex, since midnight (units unclear)

    See APRS 1.01 protocol notes (WX.TXT / PROTOCOL.TXT).
    """

    @property
    def wind_direction(self) -> float | None:
        return getattr(self, '_wind_direction', None)

    @wind_direction.setter
    def wind_direction(self, value: float | None):
        self._wind_direction = value

    @property
    def wind_speed(self) -> int | None:
        return getattr(self, '_wind_speed', None)

    @wind_speed.setter
    def wind_speed(self, value: int | None):
        self._wind_speed = value

    @property
    def wind_unit(self) -> str | None:
        """'mph' for DTI '*', 'kph' for DTI '#'."""
        return getattr(self, '_wind_unit', None)

    @wind_unit.setter
    def wind_unit(self, value: str | None):
        self._wind_unit = value

    @property
    def temperature(self) -> int | None:
        return getattr(self, '_temperature', None)

    @temperature.setter
    def temperature(self, value: int | None):
        self._temperature = value

    @property
    def rain_total(self) -> int | None:
        """Long-term accumulated rain counter (raw counts; units unclear per spec)."""
        return getattr(self, '_rain_total', None)

    @rain_total.setter
    def rain_total(self, value: int | None):
        self._rain_total = value

    @property
    def rain_today(self) -> int | None:
        """Since-midnight rain counter (raw counts; units unclear per spec)."""
        return getattr(self, '_rain_today', None)

    @rain_today.setter
    def rain_today(self, value: int | None):
        self._rain_today = value

    def parse(self) -> bool:
        if not self._info:
            return True

        if len(self._info) < 14:
            raise ParseError(
                f"Ultimeter packet too short (expected 14 hex chars, got {len(self._info)})", self
            )

        self.wind_unit = 'mph' if self.data_type_id == '*' else 'kph'

        raw_dir = _unsigned_byte(self._info[0:2])
        if raw_dir is not None:
            self.wind_direction = round(raw_dir * 360 / 256, 1)

        self.wind_speed = _unsigned_byte(self._info[2:4])
        self.temperature = _signed_byte(self._info[4:6])
        self.rain_total = _unsigned_word(self._info[6:10])
        self.rain_today = _unsigned_word(self._info[10:14])

        return True

    def __repr__(self):
        if self.source:
            return f"<UltimeterPacket: {self.source}>"
        return "<UltimeterPacket>"
