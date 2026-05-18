import pytest

from aprspy import APRS
from aprspy.packets.object import ObjectPacket
from aprspy.exceptions import ParseError


RAW_LIVE = 'XX1XX>APRS,TCPIP*,qAC,TEST:;LEADER   *092345z4903.50N/07201.75W>088/036Test comment'
RAW_KILLED = 'XX1XX>APRS,TCPIP*,qAC,TEST:;LEADER   _092345z4903.50N/07201.75W>'
RAW_PHG = 'XX1XX>APRS,TCPIP*,qAC,TEST:;IGATE    *092345z4903.50N/07201.75W#PHG5132'
RAW_COMPRESSED = 'XX1XX>APRS,TCPIP*,qAC,TEST:;COMPOBJ  *092345z/5L!!<*e7>7P[Test compressed'
RAW_SHORT_NAME = 'XX1XX>APRS,TCPIP*,qAC,TEST:;OBJ      *092345z4903.50N/07201.75W>Test'


@pytest.fixture
def packet():
    return APRS.parse_packet(RAW_LIVE)


@pytest.fixture
def killed():
    return APRS.parse_packet(RAW_KILLED)


@pytest.fixture
def compressed():
    return APRS.parse_packet(RAW_COMPRESSED)


def test_empty():
    assert repr(ObjectPacket()) == "<ObjectPacket>"


def test_type(packet):
    assert type(packet) == ObjectPacket


def test_repr(packet):
    assert repr(packet) == "<ObjectPacket: LEADER>"


def test_data_type_id(packet):
    assert packet.data_type_id == ";"


def test_object_name(packet):
    assert packet.object_name == "LEADER"


def test_object_name_stripped(packet):
    # Name field is 9 chars space-padded; trailing spaces should be stripped
    assert packet.object_name == "LEADER"
    assert len(packet.object_name) == 6


def test_alive_live(packet):
    assert packet.alive is True


def test_alive_killed(killed):
    assert killed.alive is False


def test_timestamp(packet):
    assert packet.timestamp.day == 9
    assert packet.timestamp.hour == 23
    assert packet.timestamp.minute == 45


def test_latitude(packet):
    assert packet.latitude == 49.058333


def test_longitude(packet):
    assert packet.longitude == -72.029167


def test_symbol_table(packet):
    assert packet.symbol_table == "/"


def test_symbol_id(packet):
    assert packet.symbol_id == ">"


def test_course(packet):
    assert packet.course == 88


def test_speed(packet):
    assert packet.speed == 36


def test_comment(packet):
    assert packet.comment == "Test comment"


def test_phg():
    p = APRS.parse_packet(RAW_PHG)
    assert p.power == 25
    assert p.height == 20
    assert p.gain == 3
    assert p.directivity == 90


def test_compressed_latitude(compressed):
    assert compressed.latitude == 49.5


def test_compressed_longitude(compressed):
    assert compressed.longitude == -72.750004


def test_compressed_course(compressed):
    assert compressed.course == 88


def test_compressed_speed(compressed):
    assert compressed.speed == 36.2


def test_compressed_comment(compressed):
    assert compressed.comment == "Test compressed"


def test_nonstandard_indicator_with_timestamp():
    # Non-standard indicator followed by a valid timestamp is accepted with a LENIENT warning.
    from aprspy.packets.object import ObjectPacket
    from aprspy.warnings import ParseWarningCode
    p = APRS.parse_packet('XX1XX>APRS,TCPIP*,qAC,TEST:;LEADER   X092345z4903.50N/07201.75W>')
    assert type(p) == ObjectPacket
    assert any(w.code == ParseWarningCode.OBJECT_NONSTANDARD_INDICATOR for w in p.parse_warnings)


def test_nonstandard_indicator_without_timestamp():
    # Non-standard indicator NOT followed by a timestamp falls through to the
    # missing-indicator path (lenient freeform object).
    from aprspy.warnings import ParseWarningCode
    p = APRS.parse_packet('XX1XX>APRS,TCPIP*,qAC,TEST:;LEADER   X not-a-timestamp at all here')
    assert type(p) == ObjectPacket
    assert p.alive is True
    assert any(w.code == ParseWarningCode.OBJECT_MISSING_INDICATOR for w in p.parse_warnings)


def test_too_short():
    # Short ';' frames with no indicator are now treated as freeform bulletins
    # rather than parse failures.
    from aprspy.warnings import ParseWarningCode
    p = APRS.parse_packet('XX1XX>APRS,TCPIP*,qAC,TEST:;SHORT')
    assert type(p) == ObjectPacket
    assert p.comment == 'SHORT'
    assert any(w.code == ParseWarningCode.OBJECT_MISSING_INDICATOR for w in p.parse_warnings)


@pytest.mark.parametrize("raw,name", [
    ('OE7XLI-S>APJIO4,TCPIP*,qAC,OE7XLI-GS:;OE7XLI B *141926z    .  ND     .  EaRNG0015 440 Voice 438,5750 -7,60', 'OE7XLI B'),
    ('N5BL-S>APJIO4,TCPIP*,qAC,N5BL-GS:;N5BL   C *151700z    .  ND     .  EaRNG0040 2m Voice 146.84 -0.600 Mhz', 'N5BL   C'),
    ('N4TNS-S>APJIO4,TCPIP*,qAC,N4TNS-GS:;N4TNS  C *090507z    .  ND     .  EaRNG0020 2m Voice 147.120 +0.6 MHz', 'N4TNS  C'),
])
def test_ambiguous_position(raw, name):
    # Fully ambiguous (.-padded) coordinates must not raise AttributeError
    p = APRS.parse_packet(raw)
    assert type(p) == ObjectPacket
    assert p.object_name == name
    assert p.latitude is None
    assert p.longitude is None


def test_runt_object_packet():
    # Object packet with nothing after the ';'
    p = APRS.parse_packet('NEWBRY-1>APOTU0,WIDE2-1,qAR,KC8MXW-10:;')
    assert type(p) == ObjectPacket
    assert p.object_name is None


@pytest.mark.parametrize("raw,expected_comment", [
    ('K4UAN-3>APN383,qAR,W4CAT-1:;K1LH Memorial DiGi', 'K1LH Memorial DiGi'),
    ('ACARC-1>APTT4,WIDE2-2,qAR,KO6KL-10:;!K6ARC! W2 Amador County ARC', '!K6ARC! W2 Amador County ARC'),
    ('K4UAN-3>APN383,qAR,KR4BT-10:;ARES NET SUNDAY AT 8:00 P.M. SKYWARN NET WHEN REQUESTED BY EMA or EC',
     'ARES NET SUNDAY AT 8:00 P.M. SKYWARN NET WHEN REQUESTED BY EMA or EC'),
])
def test_missing_live_killed_indicator(raw, expected_comment):
    # ';' frames without a */_ indicator are treated as freeform announcements.
    from aprspy.warnings import ParseWarningCode
    p = APRS.parse_packet(raw)
    assert type(p) == ObjectPacket
    assert p.alive is True
    assert p.object_name is None
    assert p.comment == expected_comment
    assert any(w.code == ParseWarningCode.OBJECT_MISSING_INDICATOR for w in p.parse_warnings)
