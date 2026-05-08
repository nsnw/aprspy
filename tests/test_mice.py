import pytest

from aprspy import APRS
from aprspy.packets.mice import MICEPacket
from aprspy.exceptions import ParseError


RAW = r'XX1XX-1>U1PRSS,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet'


@pytest.fixture
def packet():
    return APRS.parse_packet(RAW)


def test_empty():
    assert repr(MICEPacket()) == "<MICEPacket>"


def test_type(packet):
    assert type(packet) == MICEPacket


def test_repr(packet):
    assert repr(packet) == f"<MICEPacket: {packet.source}>"


def test_data_type_id(packet):
    assert packet.data_type_id == "`"


def test_source(packet):
    assert str(packet.source) == "XX1XX-1"


def test_destination(packet):
    assert str(packet.destination) == "U1PRSS"


def test_path(packet):
    assert str(packet.path) == "WIDE1-1,WIDE2-2,qAR,CALGRY"


def test_latitude(packet):
    assert packet.latitude == 51.038833


def test_longitude(packet):
    assert packet.longitude == -114.073667


def test_course(packet):
    assert packet.course == 238


def test_speed(packet):
    # The fixture packet exercises the wrap-around encoding: sp_raw=80 → speed 800 → 0 knots
    assert packet.speed == 0


def test_speed_direct_encoding():
    # sp_raw=7, dc_raw=11: speed = 7*10 + int(11/10) = 71 knots (no wrap, direct encoding)
    # dc_raw=11, se_raw=10: course = (11%10)*100 + 10 = 110 degrees
    raw = "XX1XX-1>U1PRSS,WIDE1-1,WIDE2-2,qAR,CALGRY:`" + "*\\F#'&k/"
    p = APRS.parse_packet(raw)
    assert p.speed == 71
    assert p.course == 110


def test_altitude(packet):
    assert packet.altitude == 1086


def test_symbol_table(packet):
    assert packet.symbol_table == "/"


def test_symbol_id(packet):
    assert packet.symbol_id == "k"


def test_comment(packet):
    assert packet.comment == "Test Mic-E packet"


def test_message_bits(packet):
    assert packet.message_bits is not None
    assert "a" in packet.message_bits
    assert "b" in packet.message_bits
    assert "c" in packet.message_bits
    assert "custom" in packet.message_bits


def test_message_type(packet):
    # U1PRSS → bits (1,0,1), standard → M2: In Service
    assert packet.message_type == "M2: In Service"


def test_message_type_none():
    assert MICEPacket().message_type is None


# Destination positions 1-3 set message bits; positions 4-6 set N/S, lng_offset, E/W.
# enc_set 1 (0-9) → bit=0; enc_set 2 (A-J) → bit=1, custom=True; enc_set 3 (P-Y) → bit=1, standard.
# Positions 4-6 are held constant (RSS) so longitude parsing is unaffected.
@pytest.mark.parametrize("destination,expected", [
    ("SSPRSS", "M0: Off Duty"),    # (1,1,1) standard: S→enc3, S→enc3, P→enc3
    ("SS0RSS", "M1: En Route"),    # (1,1,0) standard: S→enc3, S→enc3, 0→enc1
    ("U1PRSS", "M2: In Service"),  # (1,0,1) standard: U→enc3, 1→enc1, P→enc3
    ("S10RSS", "M3: Returning"),   # (1,0,0) standard: S→enc3, 1→enc1, 0→enc1
    ("0SPRSS", "M4: Committed"),   # (0,1,1) standard: 0→enc1, S→enc3, P→enc3
    ("0S0RSS", "M5: Special"),     # (0,1,0) standard: 0→enc1, S→enc3, 0→enc1
    ("01PRSS", "M6: Priority"),    # (0,0,1) standard: 0→enc1, 1→enc1, P→enc3
    ("510RSS", "Emergency"),       # (0,0,0) standard: 5→enc1, 1→enc1, 0→enc1
    ("AAARSS", "Custom-0"),        # (1,1,1) custom:   A→enc2, A→enc2, A→enc2
    ("AA0RSS", "Custom-1"),        # (1,1,0) custom:   A→enc2, A→enc2, 0→enc1
])
def test_message_type_variants(destination, expected):
    raw = r'XX1XX-1>{},WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}}Test Mic-E packet'.format(destination)
    p = APRS.parse_packet(raw)
    assert p.message_type == expected


def test_missing_symbol_table():
    with pytest.raises(ParseError):
        APRS.parse_packet(r'XX1XX-1>U1PRSS,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk', strict=True)


def test_missing_symbol_id():
    with pytest.raises(ParseError):
        APRS.parse_packet(r'XX1XX-1>U1PRSS,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"B', strict=True)


def test_packets_first_destination_bit():
    for raw in [
        r'XX1XX-1>U1PRSS,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet',
        r'XX1XX-1>F1PRSS,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet',
        r'XX1XX-1>51PRSS,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet',
    ]:
        p = APRS.parse_packet(raw)
        assert p.latitude == 51.038833


def test_packets_second_destination_bit():
    for raw in [
        r'XX1XX-1>U1PRSS,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet',
        r'XX1XX-1>UBPRSS,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet',
        r'XX1XX-1>UQPRSS,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet',
    ]:
        p = APRS.parse_packet(raw)
        assert p.latitude == 51.038833


def test_packets_third_destination_bit():
    for raw in [
        r'XX1XX-1>U1PRSS,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet',
        r'XX1XX-1>U1ARSS,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet',
        r'XX1XX-1>U10RSS,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet',
    ]:
        p = APRS.parse_packet(raw)
        assert p.latitude == 51.038833


def test_packets_fourth_destination_bit():
    raw = r'XX1XX-1>U1P2SS,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet'
    p = APRS.parse_packet(raw)
    assert p.latitude == -51.038833


def test_packets_fifth_destination_bit():
    raw = r'XX1XX-1>U1PR3S,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet'
    p = APRS.parse_packet(raw)
    assert p.longitude == -14.073667


def test_packets_sixth_destination_bit():
    raw = r'XX1XX-1>U1PRS3,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet'
    p = APRS.parse_packet(raw)
    assert p.longitude == 114.073667


def test_packets_klz_destination_bit():
    for raw in [
        r'XX1XX-1>U1PRKK,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet',
        r'XX1XX-1>U1PRLL,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet',
        r'XX1XX-1>U1PRZZ,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet',
    ]:
        p = APRS.parse_packet(raw)
        assert p.latitude == 51.033333


def test_packet_with_invalid_destination_bit():
    with pytest.raises(ParseError):
        APRS.parse_packet(r'XX1XX-1>M1PRSS,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet',
                          strict=True)


@pytest.mark.parametrize("destination", [
    "U1PASS",  # A in position 4
    "U1PBSS",  # B in position 4
    "U1PRAS",  # A in position 5
    "U1PRSA",  # A in position 6
    "U1PJSS",  # J (last of A-J) in position 4
])
def test_custom_chars_in_positions_4_to_6_parse_as_standard(destination):
    # A-J in positions 4-6 is spec-invalid but treated as standard (same result as P-Z).
    raw = r'XX1XX-1>{},WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}}Test Mic-E packet'.format(destination)
    p = APRS.parse_packet(raw)
    assert isinstance(p, MICEPacket)


def test_packets_with_80_subtracted_from_longitude():
    p = APRS.parse_packet(
        r'XX1XX-1>U1PRSS,WIDE1-1,WIDE2-2,qAR,CALGRY:`l\Fl"Bk/]"?l}Test Mic-E packet'
    )
    assert p.longitude == -100.073667


def test_packets_with_190_subtracted_from_longitude():
    p = APRS.parse_packet(
        r'XX1XX-1>U1PRSS,WIDE1-1,WIDE2-2,qAR,CALGRY:`x\Fl"Bk/]"?l}Test Mic-E packet'
    )
    assert p.longitude == -2.073667


# Telemetry packets.
# Base info without comment: longitude + speed/course (from speed=71,course=110 variant) + symbols.
# Appending telemetry separator and data bytes at info[8]+.
# Encoding: each channel/digital byte = value + 28.
_TELEM_BASE = "XX1XX-1>U1PRSS,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\\F#'&k/"
# ch1=10('&'), ch2=20('0'), ch3=30(':'), ch4=40('D'), ch5=50('N'), digital=5('!')
_TELEM_DATA = "&0:DN!"


def test_telemetry_none_when_no_telemetry():
    p = APRS.parse_packet(RAW)
    assert p.telemetry is None


def test_telemetry_type1():
    p = APRS.parse_packet(_TELEM_BASE + "," + _TELEM_DATA)
    assert p.telemetry is not None
    assert p.telemetry["analog"] == [10, 20, 30, 40, 50]
    assert p.telemetry["digital"] == 5


def test_telemetry_type2():
    p = APRS.parse_packet(_TELEM_BASE + chr(29) + _TELEM_DATA)
    assert p.telemetry is not None
    assert p.telemetry["analog"] == [10, 20, 30, 40, 50]
    assert p.telemetry["digital"] == 5


def test_telemetry_with_comment():
    p = APRS.parse_packet(_TELEM_BASE + "," + _TELEM_DATA + "hello")
    assert p.telemetry is not None
    assert p.telemetry["analog"] == [10, 20, 30, 40, 50]
    assert p.comment == "hello"


def test_telemetry_partial_channels():
    # Only 3 channels provided
    p = APRS.parse_packet(_TELEM_BASE + "," + "&0:")
    assert p.telemetry is not None
    assert p.telemetry["analog"] == [10, 20, 30]
    assert p.telemetry["digital"] == 0


def test_telemetry_no_digital_byte():
    # 5 channels but no digital byte
    p = APRS.parse_packet(_TELEM_BASE + "," + "&0:DN")
    assert p.telemetry is not None
    assert p.telemetry["analog"] == [10, 20, 30, 40, 50]
    assert p.telemetry["digital"] == 0


# Dropped SE+28 byte.
# When the SE+28 speed/course byte is a non-printable control character (e.g. 0x1c),
# some internet gateways strip it. This shifts symbol and status bytes left by one.
# The parser detects this when _info[7] is not a valid symbol table ID and recovers
# by reading the symbol from _info[5:7] instead.
#
# Packet construction (U1PRSS destination → lat 51.038833N, lng_offset True, E/W=W):
#   _info[0..2] = '*\r' = longitude 114°4.86'W
#   _info[3]    = 'l'   = SP+28 → speed 0 knots
#   _info[4]    = ' '   = DC+28 → course hundreds=4 (recomputed as 0° after drop recovery)
#   _info[5]    = '['   = symbol code (Human, primary table)
#   _info[6]    = '/'   = symbol table (primary)
#   _info[7]    = '>'   = Kenwood TH-D74 device prefix (not a valid table ID → triggers recovery)
#   _info[8..10]= '"6(' = altitude base-91 bytes → 199m
#   _info[11]   = '}'   = altitude marker
#   _info[12:]  = comment + device suffix
_DROPPED_SE_BASE = "XX1XX-1>U1PRSS,WIDE1-1,WIDE2-1:'*\\rl [/>"


def test_dropped_se_byte_symbol_id():
    p = APRS.parse_packet(_DROPPED_SE_BASE + '"6(}Test comment^')
    assert p.symbol_id == "["


def test_dropped_se_byte_symbol_table():
    p = APRS.parse_packet(_DROPPED_SE_BASE + '"6(}Test comment^')
    assert p.symbol_table == "/"


def test_dropped_se_byte_course():
    # Course recomputed from DC byte only: DC=4, hundreds=4, 400>=400 → 0 degrees
    p = APRS.parse_packet(_DROPPED_SE_BASE + '"6(}Test comment^')
    assert p.course == 0


def test_dropped_se_byte_altitude():
    p = APRS.parse_packet(_DROPPED_SE_BASE + '"6(}Test comment^')
    assert p.altitude == 199


def test_dropped_se_byte_comment():
    # Device prefix '>' and suffix '^' both stripped
    p = APRS.parse_packet(_DROPPED_SE_BASE + '"6(}Test comment^')
    assert p.comment == "Test comment"


# Device prefix/suffix stripping.
# Normal packets (SE byte present) also go through prefix/suffix stripping.
def test_device_prefix_not_in_comment():
    # RAW fixture has ']' at _info[8] (TM-D700 prefix) — must not appear in comment
    assert not RAW_packet_comment_contains("]")


def RAW_packet_comment_contains(s):
    p = APRS.parse_packet(RAW)
    return s in (p.comment or "")


def test_device_suffix_stripped():
    # Append a '^' suffix (TH-D74) to the existing fixture comment
    raw = r'XX1XX-1>U1PRSS,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet^'
    p = APRS.parse_packet(raw)
    assert p.comment == "Test Mic-E packet"
    assert p.device_id == "Kenwood TH-D74"


def test_device_suffix_2char_stripped():
    # Two-character Yaesu-style suffix
    raw = r'XX1XX-1>U1PRSS,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet_0'
    p = APRS.parse_packet(raw)
    assert p.comment == "Test Mic-E packet"
    assert p.device_id == "Yaesu FT3D"


def test_device_id_none_when_no_suffix():
    raw = r'XX1XX-1>U1PRSS,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet'
    p = APRS.parse_packet(raw)
    assert p.device_id is None


# Frequency specification (APRS 1.2 C18).
# Format: FFF.FFFMHz at the start of the comment, exactly 10 bytes.
def test_frequency_parsed():
    p = APRS.parse_packet(_DROPPED_SE_BASE + '"6(}146.850MHzAndy S andy@nsnw.ca^')
    assert p.frequency == 146.85


def test_frequency_stripped_from_comment():
    p = APRS.parse_packet(_DROPPED_SE_BASE + '"6(}146.850MHzAndy S andy@nsnw.ca^')
    assert p.comment == "Andy S andy@nsnw.ca"


def test_frequency_none_when_absent():
    p = APRS.parse_packet(RAW)
    assert p.frequency is None


def test_frequency_with_space_delimiter():
    # Some radios include a space after MHz before additional comment text
    p = APRS.parse_packet(_DROPPED_SE_BASE + '"6(}146.850MHz Andy S^')
    assert p.frequency == 146.85
    assert p.comment == "Andy S"


# parse_warnings attribute.
def test_no_warnings_on_clean_packet():
    p = APRS.parse_packet(RAW)
    assert p.parse_warnings == []


def test_warning_recorded_for_custom_dest_char():
    # Destination with A-J in positions 4-6 is spec-invalid; should parse and record a warning.
    from aprspy.warnings import ParseWarningCode
    raw = r'XX1XX-1>U1PRAS,WIDE1-1,WIDE2-1,qAR,X:`*\Fl"Bk/]"?l}Test'
    p = APRS.parse_packet(raw)
    assert any(w.code == ParseWarningCode.MICE_INVALID_DEST_CHAR for w in p.parse_warnings)


def test_generic_packet_downgrade_records_warning():
    # A packet that fails strict parsing should record why it was returned as GenericPacket.
    from aprspy.packets.generic import GenericPacket
    from aprspy.warnings import ParseWarningCode
    p = APRS.parse_packet(r'XX1XX>APRS,TCPIP*,qAC,TEST:`!!!!!!!!', strict=False)
    assert isinstance(p, GenericPacket)
    assert any(w.code == ParseWarningCode.MICE_PARSE_FAILED for w in p.parse_warnings)


def test_lowercase_destination_char_accepted():
    # DigiPi and some other firmware uses lowercase in Mic-E destination; should parse leniently.
    from aprspy.warnings import ParseWarningCode
    from aprspy.packets.mice import MICEPacket
    raw = r"W6BDS-9>c3TSTT,KF6ILA-10*,WIDE2-2,qAR,KN6RBP-10:`-a4o#Vk/`\"8g}_5"
    p = APRS.parse_packet(raw)
    assert isinstance(p, MICEPacket)
    assert any(w.code == ParseWarningCode.MICE_INVALID_DEST_CHAR for w in p.parse_warnings)
