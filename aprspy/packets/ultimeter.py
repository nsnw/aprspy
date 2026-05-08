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

_ULTW_MISSING = '----'


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


def _signed_word(hex4: str) -> int | None:
    """Parse 4 hex chars as a signed 16-bit word (-32768..32767); '----' → None."""
    if hex4 == _ULTW_MISSING:
        return None
    try:
        v = int(hex4, 16)
        return v if v < 32768 else v - 65536
    except ValueError:
        return None


def _u16(hex4: str) -> int | None:
    """Parse 4 hex chars as unsigned 16-bit word; '----' → None."""
    if hex4 == _ULTW_MISSING:
        return None
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


class Ultimeter2000Packet(GenericPacket):
    """
    Class to represent Peet Bros Ultimeter 2000 weather packets.

    Two on-air formats are handled:

    **$ULTW format** (DTI '$', info starts with 'ULTW'):
      'ULTW' + 52 hex chars (13 × 4-char fields). '----' = missing sensor.
      F0  wind_speed_peak       uint16  0.1 mph
      F1  wind_direction        uint16  degrees (0–360)
      F2  outdoor_temp          int16   0.1 °F
      F3  rain_total            uint16  0.01 in (long-term)
      F4  barometric_pressure   uint16  0.1 mbar
      F5  pressure_delta        int16   0.1 mbar (change since last reading)
      F6  [station model ID]    uint16
      F7  [flags]               uint16
      F8  outdoor_humidity      uint16  0.1 %  (may be '----')
      F9  [unknown]
      F10 wind_speed_avg        uint16  0.1 mph
      F11 rain_today            uint16  0.01 in (since midnight)
      F12 [unknown]

    **!! raw format** (DTI '!', info starts with '!'):
      '!' + 48 hex chars (12 × 4-char fields). '----' = missing sensor.
      F0  wind_speed_peak       uint16  0.1 mph
      F1  wind_direction        uint16  degrees (0–360)
      F2  outdoor_temp          int16   0.1 °F
      F3  rain_total            uint16  0.01 in (long-term)
      F4  barometric_pressure   uint16  0.1 mbar
      F5  outdoor_humidity      uint16  0.1 %  (may be '----')
      F6–F11 [unknown / reserved]
    """

    # Raw fields stored as properties with explicit units

    @property
    def wind_speed_peak(self) -> float | None:
        """Peak wind speed in mph."""
        return getattr(self, '_wind_speed_peak', None)

    @wind_speed_peak.setter
    def wind_speed_peak(self, value):
        self._wind_speed_peak = value

    @property
    def wind_direction(self) -> int | None:
        """Wind direction in degrees."""
        return getattr(self, '_wind_direction', None)

    @wind_direction.setter
    def wind_direction(self, value):
        self._wind_direction = value

    @property
    def outdoor_temp(self) -> float | None:
        """Outdoor temperature in °F."""
        return getattr(self, '_outdoor_temp', None)

    @outdoor_temp.setter
    def outdoor_temp(self, value):
        self._outdoor_temp = value

    @property
    def rain_total(self) -> float | None:
        """Long-term accumulated rain in inches."""
        return getattr(self, '_rain_total', None)

    @rain_total.setter
    def rain_total(self, value):
        self._rain_total = value

    @property
    def barometric_pressure(self) -> float | None:
        """Barometric pressure in mbar."""
        return getattr(self, '_barometric_pressure', None)

    @barometric_pressure.setter
    def barometric_pressure(self, value):
        self._barometric_pressure = value

    @property
    def pressure_delta(self) -> float | None:
        """Barometric pressure change since last reading, in mbar."""
        return getattr(self, '_pressure_delta', None)

    @pressure_delta.setter
    def pressure_delta(self, value):
        self._pressure_delta = value

    @property
    def outdoor_humidity(self) -> float | None:
        """Outdoor relative humidity in percent."""
        return getattr(self, '_outdoor_humidity', None)

    @outdoor_humidity.setter
    def outdoor_humidity(self, value):
        self._outdoor_humidity = value

    @property
    def wind_speed_avg(self) -> float | None:
        """Average/current wind speed in mph."""
        return getattr(self, '_wind_speed_avg', None)

    @wind_speed_avg.setter
    def wind_speed_avg(self, value):
        self._wind_speed_avg = value

    @property
    def rain_today(self) -> float | None:
        """Rain since midnight in inches."""
        return getattr(self, '_rain_today', None)

    @rain_today.setter
    def rain_today(self, value):
        self._rain_today = value

    def parse(self) -> bool:
        if not self._info:
            return True

        if self._info.startswith('ULTW'):
            return self._parse_ultw()
        elif self._info.startswith('!'):
            return self._parse_raw()
        else:
            raise ParseError(
                f"Unrecognised Ultimeter 2000 info field: {self._info[:10]!r}", self
            )

    def _parse_ultw(self) -> bool:
        payload = self._info[4:]
        if len(payload) < 52:
            raise ParseError(
                f"$ULTW payload too short (expected 52 hex chars, got {len(payload)})", self
            )

        fields = [payload[i:i + 4] for i in range(0, 52, 4)]

        raw_peak = _u16(fields[0])
        if raw_peak is not None:
            self.wind_speed_peak = raw_peak / 10.0

        raw_dir = _u16(fields[1])
        if raw_dir is not None:
            self.wind_direction = raw_dir

        raw_temp = _signed_word(fields[2])
        if raw_temp is not None:
            self.outdoor_temp = raw_temp / 10.0

        raw_rain_total = _u16(fields[3])
        if raw_rain_total is not None:
            self.rain_total = raw_rain_total / 100.0

        raw_bp = _u16(fields[4])
        if raw_bp is not None:
            self.barometric_pressure = raw_bp / 10.0

        raw_delta = _signed_word(fields[5])
        if raw_delta is not None:
            self.pressure_delta = raw_delta / 10.0

        # fields[6] = station model ID, fields[7] = flags — not stored as measurements

        raw_hum = _u16(fields[8])
        if raw_hum is not None:
            self.outdoor_humidity = raw_hum / 10.0

        # fields[9] unknown — skip

        raw_avg = _u16(fields[10])
        if raw_avg is not None:
            self.wind_speed_avg = raw_avg / 10.0

        raw_rain_today = _u16(fields[11])
        if raw_rain_today is not None:
            self.rain_today = raw_rain_today / 100.0

        # fields[12] unknown — skip

        return True

    def _parse_raw(self) -> bool:
        # '!!' raw format: info[0]='!' (already stripped as DTI), info starts with '!'
        payload = self._info[1:]
        if len(payload) < 48:
            raise ParseError(
                f"!! Ultimeter payload too short (expected 48 hex chars, got {len(payload)})", self
            )

        fields = [payload[i:i + 4] for i in range(0, 48, 4)]

        raw_peak = _u16(fields[0])
        if raw_peak is not None:
            self.wind_speed_peak = raw_peak / 10.0

        raw_dir = _u16(fields[1])
        if raw_dir is not None:
            self.wind_direction = raw_dir

        raw_temp = _signed_word(fields[2])
        if raw_temp is not None:
            self.outdoor_temp = raw_temp / 10.0

        raw_rain_total = _u16(fields[3])
        if raw_rain_total is not None:
            self.rain_total = raw_rain_total / 100.0

        raw_bp = _u16(fields[4])
        if raw_bp is not None:
            self.barometric_pressure = raw_bp / 10.0

        # In the !! format, humidity is at F5 (not F8 as in $ULTW)
        raw_hum = _u16(fields[5])
        if raw_hum is not None:
            self.outdoor_humidity = raw_hum / 10.0

        # fields[6–11] meanings unclear; not decoded

        return True

    def __repr__(self):
        if self.source:
            return f"<Ultimeter2000Packet: {self.source}>"
        return "<Ultimeter2000Packet>"
