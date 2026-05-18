#!/usr/bin/env python

import re
import logging
from datetime import datetime, timezone
from typing import Optional

from ..exceptions import ParseError
from ..warnings import ParseWarning, ParseWarningCode, ParseWarningSeverity
from .position import PositionPacket

logger = logging.getLogger(__name__)


def parse_weather_data(data: str) -> dict:
    """
    Parse APRS weather data fields from a string.

    Handles the standard weather field letters: c, s, g, t, r, p, P, h, b,
    L, l, S, X, and the trailing software identifier (w...).

    Returns a dict with keys for each recognised field; values are None if
    the field was absent or contained only dots (unknown).
    """
    result = {
        'wind_direction': None,
        'wind_speed': None,
        'wind_gust': None,
        'temperature': None,
        'rain_1h': None,
        'rain_24h': None,
        'rain_since_midnight': None,
        'humidity': None,
        'pressure': None,
        'luminosity': None,
        'snowfall': None,
        'weather_software': None,
    }

    def _int(s: str) -> Optional[int]:
        """Return int or None if string is all dots / blank."""
        s = s.strip()
        if not s or re.fullmatch(r'\.+', s):
            return None
        try:
            return int(s)
        except ValueError:
            return None

    def _hundredths(v: str) -> Optional[float]:
        n = _int(v)
        return n / 100 if n is not None else None

    def _tenths(v: str) -> Optional[float]:
        n = _int(v)
        return n / 10 if n is not None else None

    patterns = [
        (r'c([0-9.]{3})',     'wind_direction',      _int),
        (r's([0-9.]{3})',     'wind_speed',          _int),
        (r'g([0-9.]{3})',     'wind_gust',           _int),
        # Temperature may be negative
        (r't(-?[0-9.]{2,3})', 'temperature',         _int),
        (r'r([0-9.]{3})',     'rain_1h',             _hundredths),
        (r'p([0-9.]{3})',     'rain_24h',            _hundredths),
        (r'P([0-9.]{3})',     'rain_since_midnight', _hundredths),
        (r'h([0-9.]{2})',     'humidity',            lambda v: 100 if v == '00' else _int(v)),
        (r'b([0-9.]{5})',     'pressure',            _tenths),
        (r'[Ll]([0-9.]{3})', 'luminosity',           _int),
        (r'[Ss]([0-9.]{3})', 'snowfall',             _int),
        (r'w(\S+)',           'weather_software',    lambda v: v),
    ]

    for pattern, key, transform in patterns:
        m = re.search(pattern, data)
        if m:
            result[key] = transform(m.group(1))

    return result


class WeatherPacket(PositionPacket):
    """
    Class to represent positionless weather report packets (DTI '_').

    Format: _MMDDHHMMcXXXsXXXgXXXtXXXrXXXpXXXPXXXhXXbXXXXXwXXX

    Position-based weather packets (position report with symbol '_') are
    parsed as PositionPacket; the weather fields in their comment are also
    decoded if present.

    See APRS 1.01 C12 P63.
    """

    @property
    def wind_direction(self) -> int | None:
        return getattr(self, '_wind_direction', None)

    @wind_direction.setter
    def wind_direction(self, value: int | None):
        self._wind_direction = value

    @property
    def wind_speed(self) -> int | None:
        return getattr(self, '_wind_speed', None)

    @wind_speed.setter
    def wind_speed(self, value: int | None):
        self._wind_speed = value

    @property
    def wind_gust(self) -> int | None:
        return getattr(self, '_wind_gust', None)

    @wind_gust.setter
    def wind_gust(self, value: int | None):
        self._wind_gust = value

    @property
    def temperature(self) -> int | None:
        return getattr(self, '_temperature', None)

    @temperature.setter
    def temperature(self, value: int | None):
        self._temperature = value

    @property
    def rain_1h(self) -> float | None:
        return getattr(self, '_rain_1h', None)

    @rain_1h.setter
    def rain_1h(self, value: float | None):
        self._rain_1h = value

    @property
    def rain_24h(self) -> float | None:
        return getattr(self, '_rain_24h', None)

    @rain_24h.setter
    def rain_24h(self, value: float | None):
        self._rain_24h = value

    @property
    def rain_since_midnight(self) -> float | None:
        return getattr(self, '_rain_since_midnight', None)

    @rain_since_midnight.setter
    def rain_since_midnight(self, value: float | None):
        self._rain_since_midnight = value

    @property
    def humidity(self) -> int | None:
        return getattr(self, '_humidity', None)

    @humidity.setter
    def humidity(self, value: int | None):
        self._humidity = value

    @property
    def pressure(self) -> float | None:
        return getattr(self, '_pressure', None)

    @pressure.setter
    def pressure(self, value: float | None):
        self._pressure = value

    @property
    def luminosity(self) -> int | None:
        return getattr(self, '_luminosity', None)

    @luminosity.setter
    def luminosity(self, value: int | None):
        self._luminosity = value

    @property
    def snowfall(self) -> int | None:
        return getattr(self, '_snowfall', None)

    @snowfall.setter
    def snowfall(self, value: int | None):
        self._snowfall = value

    @property
    def weather_software(self) -> str | None:
        return getattr(self, '_weather_software', None)

    @weather_software.setter
    def weather_software(self, value: str | None):
        self._weather_software = value

    def _apply_weather(self, fields: dict):
        for key, val in fields.items():
            setattr(self, key, val)

    def parse(self) -> bool:
        if not self._info:
            return True

        if len(self._info) < 8:
            raise ParseError("Positionless weather packet too short", self)

        # Parse timestamp: MMDDHHMM (8 chars)
        ts_str = self._info[0:8]
        if ts_str == '00000000':
            self.timestamp = None
            self.timestamp_type = 'positionless'
        else:
            try:
                month = int(ts_str[0:2])
                day = int(ts_str[2:4])
                hour = int(ts_str[4:6])
                minute = int(ts_str[6:8])
                year = datetime.now(timezone.utc).year
                self.timestamp = datetime(year, month, day, hour, minute, tzinfo=timezone.utc)
                self.timestamp_type = 'positionless'
            except ValueError as e:
                # Some firmware (e.g. SP9SVH-2) emits DDMMHHMM instead of the
                # spec-required MMDDHHMM. Try the swap if the first field is an
                # invalid month and the second is a valid one.
                try:
                    alt_day = int(ts_str[0:2])
                    alt_month = int(ts_str[2:4])
                    alt_hour = int(ts_str[4:6])
                    alt_minute = int(ts_str[6:8])
                    if month > 12 and 1 <= alt_month <= 12:
                        year = datetime.now(timezone.utc).year
                        self.timestamp = datetime(
                            year, alt_month, alt_day, alt_hour, alt_minute,
                            tzinfo=timezone.utc,
                        )
                        self.timestamp_type = 'positionless'
                        self._warn(
                            ParseWarningCode.TIMESTAMP_FIELD_ORDER_SWAPPED,
                            f"Weather timestamp {ts_str!r} appears to be DDMMHHMM, "
                            f"interpreting as {alt_day:02d}/{alt_month:02d} "
                            f"{alt_hour:02d}:{alt_minute:02d}",
                            ParseWarningSeverity.LENIENT,
                        )
                    else:
                        raise ValueError(e)
                except ValueError:
                    raise ParseError(f"Invalid timestamp in weather packet: {e}", self)

        weather_data = self._info[8:]
        self._apply_weather(parse_weather_data(weather_data))

        return True

    def __repr__(self):
        if self.source:
            return f"<WeatherPacket: {self.source}>"
        return "<WeatherPacket>"
