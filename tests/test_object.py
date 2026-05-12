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
    # Non-standard indicator NOT followed by a timestamp still raises ParseError.
    with pytest.raises(ParseError):
        APRS.parse_packet('XX1XX>APRS,TCPIP*,qAC,TEST:;LEADER   X not-a-timestamp at all here', strict=True)


def test_too_short():
    with pytest.raises(ParseError):
        APRS.parse_packet('XX1XX>APRS,TCPIP*,qAC,TEST:;SHORT', strict=True)
