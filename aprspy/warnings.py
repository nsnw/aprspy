from dataclasses import dataclass, field
from enum import Enum


class ParseWarningSeverity(Enum):
    """Whether a warning is recoverable or caused a full parse downgrade."""
    INFO = "INFO"          # non-conformant but unambiguously parseable; no effect on result
    WARNING = "WARNING"    # recoverable ambiguity that affected how the packet was parsed
    DOWNGRADE = "DOWNGRADE"  # parse failed completely; packet returned as GenericPacket


class ParseWarningCode(Enum):
    """Stable codes identifying the category of a parse warning."""

    # Mic-E
    MICE_INVALID_DEST_CHAR = "MICE_INVALID_DEST_CHAR"

    # NMEA
    NMEA_CHECKSUM_INVALID = "NMEA_CHECKSUM_INVALID"

    # Telemetry
    TELEMETRY_INVALID_ANALOG_VALUE = "TELEMETRY_INVALID_ANALOG_VALUE"
    TELEMETRY_INVALID_DIGITAL_VALUE = "TELEMETRY_INVALID_DIGITAL_VALUE"
    TELEMETRY_PARM_TOO_MANY_FIELDS = "TELEMETRY_PARM_TOO_MANY_FIELDS"
    TELEMETRY_EQNS_TOO_MANY_FIELDS = "TELEMETRY_EQNS_TOO_MANY_FIELDS"

    # Timestamps
    TIMESTAMP_INVALID_TYPE = "TIMESTAMP_INVALID_TYPE"
    TIMESTAMP_LOCAL_TIME = "TIMESTAMP_LOCAL_TIME"
    TIMESTAMP_ALL_ZEROES = "TIMESTAMP_ALL_ZEROES"
    TIMESTAMP_PARSE_ERROR = "TIMESTAMP_PARSE_ERROR"
    TIMESTAMP_FORMAT_FALLBACK = "TIMESTAMP_FORMAT_FALLBACK"  # tried HHMMSS after DDHHMM failed

    # Position
    POSITION_NO_DATA = "POSITION_NO_DATA"              # all-spaces placeholder coords
    POSITION_DEL_CHARS_APPLIED = "POSITION_DEL_CHARS_APPLIED"  # \x7f treated as backspace
    POSITION_LEADING_WHITESPACE = "POSITION_LEADING_WHITESPACE"  # leading spaces stripped

    # Path
    PATH_INVALID_Q_CONSTRUCT = "PATH_INVALID_Q_CONSTRUCT"
    PATH_INVALID_HOP = "PATH_INVALID_HOP"

    # Messages
    MESSAGE_TOO_LONG = "MESSAGE_TOO_LONG"

    # General
    PACKET_USER_DEFINED_UNSUPPORTED = "PACKET_USER_DEFINED_UNSUPPORTED"

    # Downgrade codes — parse failed completely, packet returned as GenericPacket
    MICE_PARSE_FAILED = "MICE_PARSE_FAILED"
    POSITION_PARSE_FAILED = "POSITION_PARSE_FAILED"
    NMEA_PARSE_FAILED = "NMEA_PARSE_FAILED"
    MESSAGE_PARSE_FAILED = "MESSAGE_PARSE_FAILED"
    OBJECT_PARSE_FAILED = "OBJECT_PARSE_FAILED"
    ITEM_REPORT_PARSE_FAILED = "ITEM_REPORT_PARSE_FAILED"
    STATUS_PARSE_FAILED = "STATUS_PARSE_FAILED"
    TELEMETRY_PARSE_FAILED = "TELEMETRY_PARSE_FAILED"
    WEATHER_PARSE_FAILED = "WEATHER_PARSE_FAILED"
    THIRD_PARTY_PARSE_FAILED = "THIRD_PARTY_PARSE_FAILED"
    BEACON_PARSE_FAILED = "BEACON_PARSE_FAILED"
    QUERY_PARSE_FAILED = "QUERY_PARSE_FAILED"
    ULTIMETER_PARSE_FAILED = "ULTIMETER_PARSE_FAILED"
    USER_DEFINED_PARSE_FAILED = "USER_DEFINED_PARSE_FAILED"
    PARSE_FAILED = "PARSE_FAILED"  # fallback for unrecognised packet types


@dataclass
class ParseWarning:
    """A warning generated during packet parsing."""

    code: ParseWarningCode
    message: str
    severity: ParseWarningSeverity = field(default=ParseWarningSeverity.WARNING)

    def __str__(self) -> str:
        if self.severity == ParseWarningSeverity.DOWNGRADE:
            return "[DOWNGRADE:{}] {}".format(self.code.value, self.message)
        if self.severity == ParseWarningSeverity.INFO:
            return "[INFO:{}] {}".format(self.code.value, self.message)
        return "[{}] {}".format(self.code.value, self.message)
